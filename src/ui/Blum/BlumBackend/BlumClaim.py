from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException, WebDriverException, ElementClickInterceptedException, NoSuchElementException
import time
import argparse
import cv2
import numpy as np
import math
from PIL import Image
import io
from ui.api_manager import GPMManager, ADSPowerManager, ChromeManager
from ui.components import ConfigManager
import os
import json
from ui.json_path import resource_path

def clear_log_file():
    log_path = resource_path("ui//JSON_FILE//farm_logs.json")
    with open(log_path, 'w') as log_file:
        json.dump([], log_file, indent=4)

class Logger:
    def __init__(self, farm_name):
        self.farm_name = farm_name
        self.logs = []

    def log(self, task_name, status):
        log_entry = {"task_name": task_name, "status": status}
        self.logs.append(log_entry)
        print(f"{task_name}: {status}")

    def save_logs(self):
        log_data = {
            "farm_name": self.farm_name,
            "logs": self.logs
        }
        log_path = resource_path("ui//JSON_FILE//farm_logs.json")
        
        # Read existing logs
        existing_logs = []
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r') as log_file:
                    existing_logs = json.load(log_file)
            except json.JSONDecodeError:
                print("Error decoding JSON from farm_logs.json. Initializing with an empty list.")
        
        # Append new logs
        existing_logs.append(log_data)

        # Save combined logs
        with open(log_path, 'w') as log_file:
            json.dump(existing_logs, log_file, indent=4)

def abrir_y_farmear_blum(driver=None, profile_id=None, is_blum_clicker_activated=False, **kwargs):
    """
    Lógica principal del farmeo de Blum en Telegram utilizando Selenium.
    """
    logger = Logger(f"Blum Farm - Profile {profile_id}")
    logger.log("Starting farm", "DONE")

    max_retries = 1
    gpm_manager = GPMManager()  # Instancia de GPMManager

    for attempt in range(max_retries):
        if driver is None:
            logger.log("Driver initialization", "FAILED")
            print("No se pudo iniciar el navegador.")
            return
        try:
            if farmear_blum(driver, is_blum_clicker_activated, logger):
                logger.log("Farming process", "DONE")
                print("Farmeo exitoso. Cerrando el perfil.")
                break  # Si el farmeo fue exitoso, salimos del bucle
        except Exception as e:
            logger.log("Farming process", "FAILED")
            print(f"Ocurrió un error durante el proceso: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Reintentando... Intento {attempt + 2} de {max_retries}")
            else:
                print("Se alcanzó el número máximo de intentos.")
        finally:
            print("Finalizando el proceso.")
            if profile_id:
                # Cerrar el perfil desde la API
                gpm_manager.close_browser(profile_id)
            logger.save_logs()

def farmear_blum(driver, is_blum_clicker_activated, logger):
    """
    Lógica principal de farmeo dentro de Telegram para Blum.

    :param driver: Instancia del controlador de Selenium.
    :param is_blum_clicker_activated: Booleano para activar el BlumClicker después de iniciar el farming.
    :param logger: Instancia del Logger para registrar eventos.
    :return: Booleano indicando si el farmeo fue exitoso.
    """
    try:
        driver.get("https://web.telegram.org/k/#?tgaddr=tg%3A%2F%2Fresolve%3Fdomain%3Dblum%26appname%3Dapp%26startapp%3D")
        logger.log("Open Telegram with Blum", "DONE")
        print("Se ha abierto Telegram con Blum correctamente")

        # Esperar y hacer clic en el botón inicial (Launch)
        launch_button_selector = ".popup-button:nth-child(1) > .c-ripple"
        try:
            launch_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, launch_button_selector)))
            driver.execute_script("arguments[0].click();", launch_button)
            logger.log("Click Launch button", "DONE")
            print("Se hizo clic en el botón de lanzamiento (Launch)")
        except TimeoutException:
            logger.log("Click Launch button", "FAILED")
            print("No se pudo encontrar el botón de lanzamiento (Launch)")
            return False

        # Cambiar al iframe de Blum
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe")))
        logger.log("Switch to Blum iframe", "DONE")
        print("Cambiado al iframe de Blum")

        # Loop para buscar y hacer clic en uno de los tres botones
        buttons = [
            ("CLAIM_BUTTON", "//div[@id='app']/div/div/div[3]/div/button/div[2]/div/div"),
            ("START_FARMING_BUTTON", "//button[contains(.,'Start farming')]"),
            ("CONTINUE_BUTTON", "//*[@id='app']/div[1]/div/div[2]/div[2]/div[3]/button")
        ]
        
        farming_detected = False
        start_time = time.time()
        while time.time() - start_time < 20:  # Loop de 20 segundos en total
            for button_name, xpath in buttons:
                try:
                    button = driver.find_element(By.XPATH, xpath)
                    if button.is_displayed() and button.is_enabled():
                        driver.execute_script("arguments[0].click();", button)
                        logger.log(f"Click {button_name}", "DONE")
                        print(f"Se hizo clic en el botón: {button_name}")
                        break
                except:
                    continue
            
            # Verificar si se detecta el texto "Farming"
            try:
                farming_text = driver.find_element(By.XPATH, "//*[contains(text(), 'Farming')]")
                if farming_text.is_displayed():
                    logger.log("Detect 'Farming' text", "DONE")
                    print("Se detectó el texto 'Farming'. El farmeo fue exitoso.")
                    farming_detected = True
                    
                    # Ejecutar el BlumClicker solo si el checkbox está activado
                    if is_blum_clicker_activated:
                        logger.log("BlumClicker activation", "DONE")
                        logger_clicker = Logger("[BlumAutoClicker]")

                        # Hacer clic en el botón "PLAY"
                        clicked_play = buscar_y_hacer_click_en_play(driver, logger_clicker)

                        if clicked_play:
                            logger_clicker.log("Click PLAY button", "DONE")
                            click_color_areas(driver, logger_clicker)
                        else:
                            logger_clicker.log("Click PLAY button", "FAILED")
                    break
            except:
                pass

            time.sleep(0.5)

        if not farming_detected:
            logger.log("Detect 'Farming' text", "FAILED")
            print("No se pudo detectar el texto 'Farming' después de 20 segundos.")
            return False

        return True

    except Exception as e:
        logger.log("Farming process", "FAILED")
        print(f"Ocurrió un error durante el proceso de farmeo: {str(e)}")
        return False


def buscar_y_hacer_click_en_play(driver, logger):
    """
    Busca el botón "PLAY" utilizando Selenium, si no está visible, realiza scroll y vuelve a intentar.
    """
    try:
        logger.log("Buscando el botón 'PLAY'...")

        # Número máximo de intentos antes de rendirse
        max_intentos = 10
        intentos = 0

        while intentos < max_intentos:
            try:
                # Intentamos encontrar el botón "PLAY" directamente con el nuevo XPath
                play_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[1]/div/div[2]/div/a'))
                )

                # Hacer clic en el botón "PLAY"
                driver.execute_script("arguments[0].scrollIntoView();", play_button)
                play_button.click()

                logger.log("Se hizo clic en el botón PLAY.")
                return True
            except TimeoutException:
                logger.log(f"No se encontró el botón PLAY. Intento {intentos + 1} de {max_intentos}.")
                driver.execute_script("window.scrollBy(0, 300);")  # Scroll hacia abajo
                time.sleep(1)  # Añadir un retraso entre intentos
                intentos += 1

        logger.log("No se encontró el botón PLAY después de varios intentos.")
        return False

    except NoSuchElementException as e:
        logger.log(f"Error al buscar el botón PLAY: {str(e)}")
        return False
    

def click_color_areas(driver, logger):
    """
    Busca áreas en la pantalla que coincidan con el color objetivo en el espacio HSV y hace clic en esas áreas.
    
    :param driver: Instancia del controlador de Selenium.
    :param logger: Instancia del Logger para registrar eventos.
    :return: None
    """
    logger.log("Iniciando el proceso de clic en áreas de color...")

    # Definir los colores objetivo en formato HEX y convertir a HSV
    target_colors_hex = ["#1e1e1e"]  # El color que mencionaste
    target_hsvs = [hex_to_hsv(color) for color in target_colors_hex]

    # Capturar una captura de pantalla de la página actual
    screenshot = driver.get_screenshot_as_png()
    image = Image.open(io.BytesIO(screenshot))
    open_cv_image = np.array(image)

    # Convertir la imagen a formato HSV
    screenshot_hsv = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2HSV)

    # Obtener la forma de la captura de pantalla
    height, width, _ = screenshot_hsv.shape

    # Búsqueda de áreas cercanas al color objetivo
    for y in range(0, height, 10):  # Iteramos por la imagen en saltos de 10 píxeles para optimizar
        for x in range(0, width, 10):
            if is_near_color(screenshot_hsv, (x, y), target_hsvs):
                # Si encontramos un área con el color objetivo, hacemos clic en ese punto
                driver.execute_script(f"window.scrollTo({x}, {y});")
                driver.execute_script(f"document.elementFromPoint({x}, {y}).click();")

                logger.log(f"Se hizo clic en el área con color objetivo cerca de ({x}, {y})")
                time.sleep(0.5)  # Esperar un poco antes del siguiente clic

    logger.log("Proceso de clic en áreas de color completado.")


def hex_to_hsv(hex_color):
    """
    Convierte un color HEX a HSV.
    
    :param hex_color: Cadena del color en formato HEX (por ejemplo, '#1e1e1e').
    :return: Color en formato HSV.
    """
    hex_color = hex_color.lstrip('#')
    h_len = len(hex_color)
    rgb = tuple(int(hex_color[i:i + h_len // 3], 16) for i in range(0, h_len, h_len // 3))
    rgb_normalized = np.array([[rgb]], dtype=np.uint8)
    hsv = cv2.cvtColor(rgb_normalized, cv2.COLOR_RGB2HSV)
    return hsv[0][0]


def is_near_color(hsv_img, center, target_hsvs, radius=8):
    """
    Verifica si hay un color cercano al objetivo en un área alrededor de un punto en la imagen HSV.
    
    :param hsv_img: Imagen en formato HSV.
    :param center: Centro del área de búsqueda (x, y).
    :param target_hsvs: Lista de colores objetivo en formato HSV.
    :param radius: Radio de búsqueda alrededor del centro.
    :return: True si se encuentra un color cercano, False en caso contrario.
    """
    x, y = center
    height, width = hsv_img.shape[:2]

    for i in range(max(0, x - radius), min(width, x + radius + 1)):
        for j in range(max(0, y - radius), min(height, y + radius + 1)):
            distance = math.sqrt((x - i) ** 2 + (y - j) ** 2)
            if distance <= radius:
                pixel_hsv = hsv_img[j, i]  # Recuerda que en OpenCV, las coordenadas están al revés (y, x)
                for target_hsv in target_hsvs:
                    # Comparamos los valores HSV con una tolerancia (atol) para H, S y V
                    if np.allclose(pixel_hsv, target_hsv, atol=[1, 50, 50]):
                        return True
    return False

# --- MultiThread Integration ---

def start_multithread_farming(profiles, num_concurrent, window_settings):
    """
    Inicia el farmeo de múltiples perfiles usando la infraestructura de multihilo.

    :param profiles: Lista de IDs de perfiles para farmear.
    :param num_concurrent: Número de perfiles concurrentes.
    :param window_settings: Configuraciones de ventana.
    :return: None
    """
    iniciar_farmeo_multiple(profiles, num_concurrent, "blum", window_settings)

# --- MAIN ---
def parse_arguments():
    parser = argparse.ArgumentParser(description="Ejecutar Blum Claim")
    parser.add_argument("--browser", type=str, required=True, help="Tipo de navegador (gpm, ads, chrome)")
    parser.add_argument("--profile_id", type=str, help="ID del perfil para GPM")
    parser.add_argument("--profile_name", type=str, help="Nombre del perfil para Chrome")
    parser.add_argument("--win_scale", type=float, help="Escala de la ventana")
    parser.add_argument("--win_pos", type=str, help="Posición de la ventana (x,y)")
    parser.add_argument("--win_size", type=str, help="Tamaño de la ventana (ancho,alto)")
    return parser.parse_args()


if __name__ == "__main__":
    # Importar desde MultiThreadFarming.py
    from ui.MultiThreadFarming import iniciar_farmeo_multiple
    args = parse_arguments()

    kwargs = {
        "win_scale": args.win_scale,
        "win_pos": args.win_pos,
        "win_size": args.win_size
    }

    profiles = [args.profile_id]  # Aquí deberías pasar una lista de IDs de perfiles si son múltiples
    num_concurrent = 1  # Cambiar a más si deseas farmeo concurrente

    start_multithread_farming(profiles, num_concurrent, kwargs)
