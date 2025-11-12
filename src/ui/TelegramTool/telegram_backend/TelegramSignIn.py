from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException, ElementNotInteractableException
import time
import argparse
import random
import json
import os
import logging
import traceback
from ui.api_manager import GPMManager, ADSPowerManager, ChromeManager
from ui.components import ConfigManager
from ui.json_path import resource_path

# Configuración básica del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def telegramTool(driver=None, profile_id=None, **kwargs):
    """
    Lógica principal del farmeo de Blum en Telegram utilizando Selenium.
    """
    
    # Construir la ruta al archivo JSON
    file_path = resource_path("ui//JSON_FILE//TelegramTool.json")
    
    # Imprimir la ruta para verificar
    print(f"Intentando abrir el archivo JSON en: {file_path}")
    
    # Verificar si el archivo existe
    if not os.path.exists(file_path):
        print(f"El archivo JSON no existe en la ruta: {file_path}")
        return

    # Leer el archivo JSON y extraer 'country' y 'phone_urls'
    with open(file_path, "r") as json_file:
        data = json.load(json_file)

    country = data.get("country")
    phone_urls = data.get("phone_urls", [])

    if not phone_urls:
        print("No hay más números de teléfono y enlaces para procesar.")
        return

    # Obtener el primer elemento de phone_urls y separarlo en phone_number y link
    item = phone_urls[0]
    try:
        phone_number, link = item.split('/', 1)
        phone_number = phone_number.strip()
        link = link.strip()
    except ValueError:
        print(f"Formato incorrecto en el elemento: {item}")
        # Eliminar el elemento problemático y guardar cambios
        phone_urls.pop(0)
        data['phone_urls'] = phone_urls
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        return

    max_retries = 1
    gpm_manager = GPMManager()  # Instancia de GPMManager

    for attempt in range(max_retries):
        if driver is None:
            # Inicializar el driver usando GPMManager
            driver = gpm_manager.start_browser(profile_id)
            if driver is None:
                print("No se pudo iniciar el navegador.")
                return
        try:
            # Pasar los parámetros necesarios a farmeo_principal
            if farmeo_principal(driver, country=country, phone_number=phone_number, link=link):
                print("Farmeo exitoso. Cerrando el perfil.")
                # Si el farmeo fue exitoso, eliminamos el elemento de phone_urls y guardamos
                phone_urls.pop(0)
                data['phone_urls'] = phone_urls
                with open(file_path, 'w') as json_file:
                    json.dump(data, json_file, indent=4)
                break  # Salimos del bucle
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

def farmeo_principal(driver, country, phone_number, link):
    try:
        logging.info("Iniciando farmeo_principal")
        wait = WebDriverWait(driver, 30)
        short_wait = WebDriverWait(driver, 10)

        # Paso 1: Navegar a https://web.telegram.org/k/
        logging.info("Paso 1: Navegando a https://web.telegram.org/k/")
        driver.get('https://web.telegram.org/k/')
        logging.info("Navegación a Telegram Web exitosa")

        # Paso 2: Hacer clic en el botón especificado
        logging.info("Paso 2: Haciendo clic en el botón de inicio de sesión")
        button_xpath = '//*[@id="auth-pages"]/div/div[2]/div[3]/div/div[2]/button[1]'
        button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
        button.click()
        logging.info("Click en el botón de inicio de sesión exitoso")

        # Paso 3: Seleccionar el input de país
        logging.info(f"Paso 3: Ingresando el país: {country}")
        country_input_xpath = '//*[@id="auth-pages"]/div/div[2]/div[2]/div/div[3]/div[1]/div[1]/span'
        country_input = wait.until(EC.presence_of_element_located((By.XPATH, country_input_xpath)))
        country_input.clear()
        human_like_delay()
        country_input.send_keys(country)
        human_like_delay()
        logging.info("País ingresado exitosamente")
        
        # Simular la pulsación de la tecla Enter
        country_input.send_keys(Keys.ENTER)
        logging.info("País ingresado exitosamente y tecla Enter presionada")

        # Paso 5: Seleccionar el input de número de teléfono
        logging.info(f"Paso 5: Ingresando el número de teléfono: {phone_number}")
        phone_input_xpath = '//*[@id="auth-pages"]/div/div[2]/div[2]/div/div[3]/div[2]/div[1]'
        phone_input = wait.until(EC.presence_of_element_located((By.XPATH, phone_input_xpath)))
        human_like_delay()
        phone_input.send_keys(phone_number)
        human_like_delay()
        logging.info("Número de teléfono ingresado exitosamente")

        # Paso 7: Hacer clic en el botón 'Siguiente'
        logging.info("Paso 7: Haciendo clic en el botón 'Siguiente'")
        next_button_xpath = '//*[@id="auth-pages"]/div/div[2]/div[2]/div/div[3]/button[1]'
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, next_button_xpath)))
        next_button.click()
        logging.info("Click en el botón 'Siguiente' exitoso")
        
        code, password = get_otp_and_password(driver, link)

        try:
            otp_input = wait_for_element(driver, "#auth-pages > div > div.tabs-container.auth-pages__container > div.tabs-tab.page-authCode.active > div > div.input-wrapper > div > input")
            write_to_element(otp_input, code)
            logging.info("OTP code entered")
        except TimeoutException:
            logging.error("OTP input field not found")

        human_like_delay()

        logging.info("Step 8: Checking for password field")
        try:
            password_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#auth-pages > div > div.tabs-container.auth-pages__container > div.tabs-tab.page-password.active > div > div.input-wrapper > div > input.input-field-input.is-empty"))
            )
            if password:
                write_to_element(password_input, password)
                logging.info("Password entered")
                
                logging.info("Step 9: Clicking final Next button")
                try:
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "#auth-pages > div > div.tabs-container.auth-pages__container > div.tabs-tab.page-password.active > div > div.input-wrapper > button > div"))
                    )
                    click_element(next_button)
                    logging.info("Clicked final Next button")
                except TimeoutException:
                    logging.error("Final Next button not found")
            else:
                logging.warning("Password field found but no password available")
        except TimeoutException:
            logging.info("No password field found, continuing without password")

        # Paso 15: Esperar 2 segundos
        logging.info("Paso 15: Esperando 2 segundos")
        time.sleep(2)

        logging.info("Proceso completado exitosamente")
        return True  # Indicar que el proceso fue exitoso

    except TimeoutException as e:
        logging.error("Timeout al esperar por un elemento.")
        logging.error(f"Detalle del error: {e}")
        return False

    except Exception as e:
        logging.error(f"Ocurrió un error durante el proceso: {str(e)}")
        traceback_str = ''.join(traceback.format_exception(None, e, e.__traceback__))
        logging.error(f"Traceback del error:\n{traceback_str}")
        # Tomar una captura de pantalla si ocurre un error
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        screenshot_filename = f'error_{timestamp}.png'
        screenshot_path = os.path.join(os.getcwd(), screenshot_filename)
        driver.save_screenshot(screenshot_path)
        logging.info(f"Captura de pantalla guardada en: {screenshot_path}")
        return False

def click_element(element):
    retry_action(element.click)

def human_like_delay():
    time.sleep(random.uniform(1, 3))

def write_to_element(element, text):
    def write_action():
        element.clear()
        element.send_keys(text)
    retry_action(write_action)

def retry_action(action, max_retries=5):
    for attempt in range(max_retries):
        try:
            return action()
        except (StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException) as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(1)

def wait_for_element(driver, selector, timeout=30):
    def find_element():
        return driver.find_element(By.CSS_SELECTOR, selector)
    return WebDriverWait(driver, timeout).until(lambda d: retry_action(find_element))

def get_otp_and_password(driver, url):
    # Esperar a que el campo de entrada OTP esté disponible antes de cambiar de pestaña
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#auth-pages > div > div.tabs-container.auth-pages__container > div.tabs-tab.page-authCode.active > div > div.input-wrapper > div > input"))
        )
        logging.info("El campo de entrada OTP está disponible antes de cambiar de pestaña.")
    except TimeoutException:
        logging.error("Campo de entrada OTP no encontrado antes de cambiar de pestaña.")
        return None, None
    
    # Abrir la nueva pestaña y cambiar a ella
    current_handles = driver.window_handles
    driver.execute_script(f"window.open('{url}', '_blank');")
    new_handle = [handle for handle in driver.window_handles if handle not in current_handles][0]
    driver.switch_to.window(new_handle)
    
    # Esperar a que el elemento body esté presente
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    
    code = None
    password = None
    
    try:
        code = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "code"))
        ).get_attribute("value")
        logging.info(f"Código OTP obtenido: {code}")
    except TimeoutException:
        logging.error("Código OTP no encontrado.")
    
    try:
        password = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pass2fa"))
        ).get_attribute("value")
        logging.info(f"Contraseña obtenida: {password}")
    except TimeoutException:
        logging.error("Contraseña no encontrada.")
    
    driver.close()
    driver.switch_to.window(current_handles[0])
    
    if not code or not password:
        logging.error("No se pudo obtener el código OTP o la contraseña.")
    
    return code, password

# --- MultiThread Integration ---

def start_multithread_farming(profiles, num_concurrent, window_settings):
    """
    Inicia el farmeo de múltiples perfiles usando la infraestructura de multihilo.

    :param profiles: Lista de IDs de perfiles para farmear.
    :param num_concurrent: Número de perfiles concurrentes.
    :param window_settings: Configuraciones de ventana.
    :return: None
    """
    iniciar_farmeo_multiple(profiles, num_concurrent, "TelegramTool", window_settings)

# --- MAIN ---
def parse_arguments():
    parser = argparse.ArgumentParser(description="Ejecutar Blum Claim")
    parser.add_argument("--browser", type=str, required=True, help="Tipo de navegador (gpm, ads, chrome)")
    parser.add_argument("--profile_ids", type=str, nargs='+', help="IDs de los perfiles para GPM")
    parser.add_argument("--profile_names", type=str, nargs='+', help="Nombres de los perfiles para Chrome")
    parser.add_argument("--win_scale", type=float, help="Escala de la ventana")
    parser.add_argument("--win_pos", type=str, help="Posición de la ventana (x,y)")
    parser.add_argument("--win_size", type=str, help="Tamaño de la ventana (ancho,alto)")
    return parser.parse_args()

if __name__ == "__main__":
    from ui.MultiThreadFarming import iniciar_farmeo_multiple
    args = parse_arguments()

    kwargs = {
        "win_scale": args.win_scale,
        "win_pos": args.win_pos,
        "win_size": args.win_size
    }

    profiles = args.profile_ids  # Lista de IDs de perfiles
    num_concurrent = 1  # Cambiar a más si deseas farmeo concurrente

    start_multithread_farming(profiles, num_concurrent, kwargs)
