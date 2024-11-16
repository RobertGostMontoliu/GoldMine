from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException, WebDriverException, ElementClickInterceptedException, NoSuchElementException
import time
import argparse
from ui.api_manager import GPMManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import random
from ui.WolfGame.Backend import WolfAuto

def WolfGame(driver=None, profile_id=None, **kwargs):
    max_retries = 2
    gpm_manager = GPMManager()  # Instancia de GPMManager

    for attempt in range(max_retries):
        if driver is None:
            print("No se pudo iniciar el navegador.")
            return
        try:
            if farmeo_principal(driver, WolfGame):
                print("Farmeo inicial exitoso. Iniciando automatización...")
                # Iniciar la automatización
                result = start_automation(driver, profile_id)
                if result == "complete":
                    print("Automatización completada. Cerrando el perfil.")
                    break
                elif result == "restart":
                    print("Reiniciando el proceso de automatización...")
                    continue
            else:
                print("Farmeo inicial fallido. Reintentando...")
        except Exception as e:
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

def farmeo_principal(driver, test):
    try:
        # Navegar a la página web y esperar que cargue correctamente
        driver.get("https://cave.wolf.game/")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("Página cargada correctamente")

        # Lista de botones con sus XPaths y nombres de referencia
        botones = [
            ("//div[@id='root']/div/div[2]/div/div/div/div[2]/div/div/div", "Botón de log in"),
            ("//*[@id='root']/div/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[1]", "Botón de Sign"),
            ("//*[@id='privy-modal-content']/div/div[1]/div[3]/div/button", "Botón de Twitter"),
            ("//*[@id='react-root']/div/div/div[2]/main/div/div/div[2]/div/div/div[1]/div[3]/button", "Botón de auth Twitter"),
            ("//*[@id='root']/div/div[1]/div/div[2]/div/div/div/div/div[4]/div/div[2]", "Botón de Sign 2")
        ]

        # Botón para romper el loop
        boton_romper_loop = "//div[2]/div/div/div/div/div/button"

        def click_button(xpath, name):
            try:
                element = driver.find_element(By.XPATH, xpath)
                driver.execute_script("arguments[0].click();", element)
                print(f"Se hizo clic en: {name}")
                return True
            except NoSuchElementException:
                return False

        while True:
            random.shuffle(botones)
            
            for xpath, nombre in botones:
                if click_button(xpath, nombre):
                    time.sleep(1)  # Pequeña pausa para permitir que la página responda
                    break

            if click_button(boton_romper_loop, "Botón para romper el loop"):
                print("Se detectó y se hizo clic en el botón para romper el loop. Finalizando el proceso.")
                break

        # Lista de XPaths para la oveja disponible
        sheep_xpaths = [
            "//*[@id='root']/div/div[2]/div/div/div/div[5]/div/div[2]/div[2]/div[2]/div[2]/div/div[2]/div/div",
            "//div[@id='root']/div/div[2]/div/div/div/div[3]/div/div/div[2]/div[2]/div[2]/div/div[2]/div/div/div/div[3]/div/div[2]/div"
        ]

        # Click en la oveja disponible
        print("Esperando y haciendo clic en la oveja disponible...")
        sheep_found = False
        for xpath in sheep_xpaths:
            try:
                sheep_element = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                sheep_element.click()
                sheep_found = True
                print(f"Oveja encontrada y clickeada usando xpath: {xpath}")
                break
            except:
                continue

        if not sheep_found:
            print("No se pudo encontrar la oveja disponible")
            return False

        time.sleep(1)  # Delay de 1 segundo

        # Click en Resume play (versión actualizada)
        print("Esperando y haciendo clic en Resume play...")
        resume_play_xpath = "//div[2]/div/div/div/div/div/div[2]/div[2]"
        resume_play_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, resume_play_xpath))
        )
        ActionChains(driver).move_to_element(resume_play_button).click().perform()
        time.sleep(1)  # Delay de 1 segundo

        # Espera de 10 segundos para ver si todo sale bien
        print("Esperando 10 segundos para verificar que todo salió bien...")
        time.sleep(10)

        print("Proceso inicial completado. Iniciando automatización...")
        return True  # Indica que el proceso inicial fue exitoso
    except Exception as e:
        print(f"Error durante el proceso inicial: {str(e)}")
        driver.save_screenshot("error_screenshot.png")
        print("Se ha guardado una captura de pantalla del error")
        return False

def start_automation(driver, profile_id):
    # Extraer la energía inicial
    initial_energy = WolfAuto.extract_energy(driver)
    if initial_energy is None or initial_energy == 0:
        print("No se pudo obtener la energía inicial. Saliendo de la automatización.")
        return "restart"

    print(f"Energía inicial: {initial_energy}")

    # Iniciar la exploración
    result = WolfAuto.explore(driver, initial_energy, profile_id)
    return result

# --- MultiThread Integration ---

def start_multithread_farming(profiles, num_concurrent, window_settings):
    """
    Inicia el farmeo de múltiples perfiles usando la infraestructura de multihilo.

    :param profiles: Lista de IDs de perfiles para farmear.
    :param num_concurrent: Número de perfiles concurrentes.
    :param window_settings: Configuraciones de ventana.
    :return: None
    """
    iniciar_farmeo_multiple(profiles, num_concurrent, "wolfgame", window_settings)  


# --- MAIN ---
def parse_arguments():
    parser = argparse.ArgumentParser(description="Ejecutar Wolf Game")
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
