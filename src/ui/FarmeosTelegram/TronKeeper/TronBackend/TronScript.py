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
from ui.Log_JSON import Logger

def abrir_y_farmear_tronkeeper(driver=None, profile_id=None, is_tronkeeper_clicker_activated=False, **kwargs):    
    """
    Lógica principal del farmeo de TronKeeper en Telegram utilizando Selenium. 
    """
    logger = Logger(f"TronKeeper Farm - Profile {profile_id}")
    logger.log("Starting farm", "DONE")

    max_retries = 1
    gpm_manager = GPMManager()  # Instancia de GPMManager

    for attempt in range(max_retries):
        if driver is None:
            logger.log("Driver initialization", "FAILED")
            print("No se pudo iniciar el navegador.")
            return
        try:
            if farmear_tronkeeper(driver, is_tronkeeper_clicker_activated, logger): 
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

def farmear_tronkeeper(driver, is_tronkeeper_clicker_activated, logger):  
    try:
        # Abrir Telegram con TronKeeper
        driver.get("https://web.telegram.org/k/#?tgaddr=tg%3A%2F%2Fresolve%3Fdomain%3DTronKeeperBot%26appname%3Dapp%26startapp%3D1418302636")
        logger.log("Open Telegram with TronKeeper", "DONE") 
        print("Se ha abierto Telegram con TronKeeper correctamente")

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

        # Cambiar al iframe de TronKeeper 
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe")))
        logger.log("Switch to TronKeeper iframe", "DONE")
        print("Cambiado al iframe de TronKeeper")

        if is_tronkeeper_clicker_activated:
            # Realizar pasos de registro
            # Esperar y hacer clic en Subscribe Now dentro del iframe
            subscribe_now_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div[3]/button[1]'))
            )
            subscribe_now_button.click()
            logger.log("Click Subscribe Now in iframe", "DONE")

            # Volver al contenido principal
            driver.switch_to.default_content()
            
            # Hacer clic en el botón Subscribe en la ventana principal
            subscribe_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="column-center"]/div/div/div[2]/div[1]/div[2]/button[1]'))
            )
            subscribe_button.click()
            logger.log("Click Subscribe in main window", "DONE")

            # Volver al iframe
            WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe")))
            
            # Hacer clic en Continue
            continue_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div[3]/button[2]'))
            )
            continue_button.click()
            logger.log("Click Continue in iframe", "DONE")
        else:
            try:
                # Obtener el número de tickets disponibles usando el XPath exacto
                tickets_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[1]/div/div[4]/div[1]/span[2]/span'))
                )
                # Esperar 2 segundos antes de leer el valor
                time.sleep(2)
                
                available_tickets = int(tickets_element.text)
                print(f"Tickets disponibles: {available_tickets}")
                logger.log(f"Available tickets: {available_tickets}", "INFO")

            except Exception as e:
                print(f"Error al detectar tickets: {str(e)}")
                logger.log(f"Error detecting tickets: {str(e)}", "ERROR")
                return False

            if available_tickets <= 0:
                print("No hay tickets disponibles")
                logger.log("No tickets available", "INFO")
                return True

            # Interactuar con la moneda tantas veces como tickets haya
            for ticket in range(available_tickets):
                print(f"Iniciando hold de moneda {ticket + 1} de {available_tickets}")
                logger.log(f"Starting coin hold {ticket + 1}/{available_tickets}", "INFO")
                
                coin = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[1]/div/div[4]/div[2]/div[2]'))
                )
                print("Moneda detectada, esperando 2 segundos antes de iniciar")
                logger.log("Coin detected, waiting 2 seconds", "DONE")
                
                # Esperar 2 segundos antes de iniciar el click
                time.sleep(2)
                
                print("Iniciando click sostenido por 32 segundos")
                # Mantener el click sostenido por 32 segundos usando JavaScript
                driver.execute_script("""
                    var element = arguments[0];
                    var mousedownEvent = new MouseEvent('mousedown', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    element.dispatchEvent(mousedownEvent);
                """, coin)
                
                # Esperar 32 segundos
                time.sleep(32)
                
                # Liberar el click
                driver.execute_script("""
                    var element = arguments[0];
                    var mouseupEvent = new MouseEvent('mouseup', {
                        bubbles: true,
                        cancelable: true,
                        view: window
                    });
                    element.dispatchEvent(mouseupEvent);
                """, coin)
                
                logger.log(f"Completed coin hold {ticket + 1}/{available_tickets}", "DONE")
                
                # Si hay más tickets, esperar 2 segundos entre cada hold
                if ticket < available_tickets - 1:
                    print("Esperando 2 segundos antes del siguiente hold")
                    time.sleep(2)
            
            logger.log("All coin holds completed", "DONE")

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

def click_coin_if_present(driver, logger):
    try:
        coin = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[1]/div/div[4]/div[2]/div[2]'))
        )
        print("Moneda detectada, iniciando clicks")
        logger.log("Coin detected, starting clicks", "DONE")
        
        # Click en la moneda durante 32 segundos
        end_time = time.time() + 32
        while time.time() < end_time:
            try:
                # Verificar si la clase actual es 'Coin' (no activa)
                if 'Coin active' not in coin.get_attribute('class'):
                    coin.click()
                time.sleep(0.1)  # Pequeña pausa entre verificaciones
            except:
                pass
        logger.log("Coin clicking completed", "DONE")
        return True
    except TimeoutException:
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
