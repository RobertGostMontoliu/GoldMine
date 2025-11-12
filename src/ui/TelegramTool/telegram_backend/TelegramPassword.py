from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, JavascriptException
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
logger = logging.getLogger(__name__)

def telegramToolPassword(driver=None, profile_id=None, **kwargs):
    """
    Lógica principal del farmeo de Blum en Telegram utilizando Selenium.
    """
    
    # Construir la ruta al archivo JSON
    file_path = resource_path("ui//JSON_FILE//TelegramToolPasswords.json")
    
    # Imprimir la ruta para verificar
    print(f"Intentando abrir el archivo JSON en: {file_path}")
    
    # Verificar si el archivo existe
    if not os.path.exists(file_path):
        print(f"El archivo JSON no existe en la ruta: {file_path}")
        return

    # Leer el archivo JSON y extraer 'country' y 'phone_urls'
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
        
    oldPass = data.get("oldPassword")
    newPass = data.get("newPassword")
    
    logger.info(f"Contraseña actual ingresada usando JavaScript: {oldPass}")
    logger.info(f"Contraseña actual ingresada usando JavaScript: {newPass}")

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
            if farmeo_principal(driver, oldPass=oldPass, newPass=newPass):
                print("Farmeo exitoso. Cerrando el perfil.")
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

def farmeo_principal(driver, oldPass, newPass):
    try:           
        driver.get("https://web.telegram.org/k/")
        logger.info("Página de Telegram cargada")

        # Esperar y hacer clic en el botón de la barra lateral
        if not wait_and_click(driver, "//*[contains(@class,'sidebar-tools')]", "botón de la barra lateral"):
            return False

        # Esperar un momento para que el menú se abra completamente
        time.sleep(2)

        # Esperar y hacer clic en Settings
        if not wait_and_click(driver, "//span[text()='Settings']", "Settings"):
            return False

        # Esperar y hacer clic en Privacy and Security
        if not wait_and_click(driver, "//span[text()='Privacy and Security']", "Privacy and Security"):
            return False

        # Intentar hacer clic en Two-Step Verification con la nueva función
        if not find_and_click_two_step(driver):
            logger.error("No se pudo hacer clic en Two-Step Verification")
            return False
        
        # Esperar a que aparezca el campo de contraseña actual
        oldPass_xpath = '//*[@id="column-left"]/div/div[4]/div[2]/div/div[2]/div/div/div[2]/div/input[2]'
        try:
            logger.info("Esperando a que el campo de contraseña actual sea visible y tenga tamaño")
            oldPass_field = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, oldPass_xpath))
            )
                
            # Esperar un momento adicional para asegurarse de que la página se ha cargado completamente
            time.sleep(3)
                
            # Verificar si el elemento tiene tamaño y ubicación
            size = oldPass_field.size
            location = oldPass_field.location
            if size['width'] == 0 or size['height'] == 0:
                logger.error("El campo de contraseña actual no tiene tamaño")
                return False
                
            logger.info(f"Campo de contraseña actual encontrado. Tamaño: {size}, Ubicación: {location}")
                
            # Intentar hacer clic en el campo de contraseña actual usando JavaScript
            driver.execute_script("arguments[0].click();", oldPass_field)
            logger.info("Clic realizado en el campo de contraseña actual usando JavaScript")
                
            # Esperar un momento para asegurarse de que el campo tiene el foco
            time.sleep(1)
                
            # Intentar escribir la contraseña actual usando JavaScript
            driver.execute_script("arguments[0].value = arguments[1];", oldPass_field, oldPass)
            logger.info(f"Contraseña actual ingresada usando JavaScript: {oldPass}")
                
            # Verificar si la contraseña se ingresó correctamente
            entered_password = driver.execute_script("return arguments[0].value;", oldPass_field)
            if entered_password == oldPass:
                logger.info("Contraseña actual ingresada correctamente")
            else:
                logger.warning("La contraseña actual no se ingresó correctamente")
                
            # Hacer clic en el botón de continuar
            continue_button_selector = "#column-left > div > div.tabs-tab.sidebar-slider-item.scrolled-top.scrolled-bottom.scrollable-y-bordered.two-step-verification.two-step-verification-enter-password.active > div.sidebar-content > div > div.sidebar-left-section-container > div > div > div.input-wrapper > button > div"
            continue_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, continue_button_selector))
            )
            driver.execute_script("arguments[0].click();", continue_button)
            logger.info("Clic en botón de continuar realizado")
                
            # Esperar un momento para que la página se actualice
            time.sleep(3)
                
        except TimeoutException:
            logger.error("No se pudo encontrar el campo de contraseña actual o el botón de continuar")
            return False
        except Exception as e:
            logger.error(f"Error al interactuar con el campo de contraseña actual o el botón de continuar: {str(e)}")
            return False

        # Reemplazar el antiguo código de clic en "Change Password" con la nueva función
        if not find_and_click_change_password(driver):
            logger.error("No se pudo hacer clic en 'Change Password'. Abortando el proceso.")
            return False

        # Ingresar nueva contraseña
        newPass_selector = "#column-left > div > div.tabs-tab.sidebar-slider-item.scrolled-top.scrolled-bottom.scrollable-y-bordered.two-step-verification.two-step-verification-enter-password.active > div.sidebar-content > div > div.sidebar-left-section-container > div > div > div.input-wrapper > div > input.input-field-input.is-empty"
        try:
            newPass_field = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, newPass_selector))
            )
            newPass_field.clear()
            newPass_field.send_keys(newPass)
            logger.info("Nueva contraseña ingresada")
        except TimeoutException:
            logger.error("No se pudo encontrar el campo de nueva contraseña")
            return False

        # Clic en Continuar después de ingresar nueva contraseña
        continue_after_newPass_selector = "#column-left > div > div.tabs-tab.sidebar-slider-item.scrolled-top.scrolled-bottom.scrollable-y-bordered.two-step-verification.two-step-verification-enter-password.active > div.sidebar-content > div > div.sidebar-left-section-container > div > div > div.input-wrapper > button > div"
        if not wait_and_click(driver, continue_after_newPass_selector, "Continuar después de nueva contraseña"):
            return False

        # Re-ingresar nueva contraseña
        reenter_password_selector = "#column-left > div > div.tabs-tab.sidebar-slider-item.scrolled-top.scrolled-bottom.scrollable-y-bordered.two-step-verification.two-step-verification-enter-password.two-step-verification-re-enter-password.active > div.sidebar-content > div > div.sidebar-left-section-container > div > div > div.input-wrapper > div > input.input-field-input.is-empty"
        try:
            reenter_password_field = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, reenter_password_selector))
            )
            reenter_password_field.clear()
            reenter_password_field.send_keys(newPass)
            logger.info("Nueva contraseña re-ingresada")
        except TimeoutException:
            logger.error("No se pudo encontrar el campo para re-ingresar la nueva contraseña")
            return False

        # Clic en Continuar después de re-ingresar nueva contraseña
        continue_after_renewPass_selector = "#column-left > div > div.tabs-tab.sidebar-slider-item.scrolled-top.scrolled-bottom.scrollable-y-bordered.two-step-verification.two-step-verification-enter-password.two-step-verification-re-enter-password.active > div.sidebar-content > div > div.sidebar-left-section-container > div > div > div.input-wrapper > button > div"
        if not wait_and_click(driver, continue_after_renewPass_selector, "Continuar después poner la cantraseña por segunda vez"):
            return False

        logger.info("Esperando 2 segundos después de hacer clic en Continuar...")
        time.sleep(2)
            
        # Clic en Skip en el apartado de hint
        continue_after_renewPass_selector = "#column-left > div > div.tabs-tab.sidebar-slider-item.scrolled-top.scrolled-bottom.scrollable-y-bordered.two-step-verification.two-step-verification-hint.active > div.sidebar-content > div > div.sidebar-left-section-container > div > div > div.input-wrapper > button.btn-primary.btn-secondary.btn-primary-transparent.primary.rp > div"
        if not wait_and_click(driver, continue_after_renewPass_selector, "Continuar después poner la cantraseña por segunda vez"):
            return False
            
        time.sleep(2)
            
        # Clic en Skip en el apartado de correo
        continue_after_renewPass_selector = "#column-left > div > div.tabs-tab.sidebar-slider-item.scrolled-top.scrolled-bottom.scrollable-y-bordered.two-step-verification.two-step-verification-email.active > div.sidebar-content > div > div.sidebar-left-section-container > div > div:nth-child(3) > div > button.btn-primary.btn-secondary.btn-primary-transparent.primary.rp > div"
        if not wait_and_click(driver, continue_after_renewPass_selector, "Continuar después poner la cantraseña por segunda vez"):
            return False
            
        time.sleep(2)
            
        # Clic en Skip en el apartado de verificación del correo
        continue_after_renewPass_selector = "body > div.popup.popup-peer.popup-skip-email.active > div > div.popup-buttons > button.popup-button.btn.danger.rp > div"
        if not wait_and_click(driver, continue_after_renewPass_selector, "Continuar después poner la cantraseña por segunda vez"):
            return False
            
        time.sleep(2)
            
        # Clic en Return to Settings
        continue_after_renewPass_selector = "#column-left > div > div.tabs-tab.sidebar-slider-item.scrolled-top.scrolled-bottom.scrollable-y-bordered.two-step-verification.two-step-verification-set.active > div.sidebar-content > div > div.sidebar-left-section-container > div > div:nth-child(3) > div > button > div"
        if not wait_and_click(driver, continue_after_renewPass_selector, "Continuar después poner la cantraseña por segunda vez"):
            return False

        logger.info(f"Contraseña cambiada exitosamente para el perfil {driver}")
        return True

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

def wait_and_click(driver, selector, description, timeout=30):
    try:
        if selector.startswith('/'):
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
        else:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(1)  # Pequeña pausa para asegurar que el elemento esté visible
        driver.execute_script("arguments[0].click();", element)
        logger.info(f"Clic en {description} realizado")
        return True
    except Exception as e:
        logger.error(f"Error al hacer clic en {description}: {str(e)}")
        return False
    
def find_and_click_two_step(driver):
    selector = "#column-left > div > div.tabs-tab.sidebar-slider-item.scrolled-top.scrollable-y-bordered.dont-u-dare-block-me.active > div.sidebar-content > div > div:nth-child(2) > div.sidebar-left-section.no-delimiter > div > div:nth-child(2) > div.c-ripple"
    
    js_script = f"""
    const boton = document.querySelector('{selector}');
    if (boton) {{
      try {{
        boton.click();
        return 'El botón es clicable';
      }} catch (error) {{
        return 'El botón no es clicable: ' + error.message;
      }}
    }} else {{
      return 'No se encontró el botón';
    }}
    """
    
    try:
        logger.info("Esperando a que el elemento Two-Step Verification sea visible")
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
        )
        
        logger.info("Elemento Two-Step Verification visible, esperando 2 segundos adicionales")
        time.sleep(2)
        
        logger.info("Ejecutando script JavaScript para hacer clic")
        result = driver.execute_script(js_script)
        logger.info(f"Resultado del script JavaScript: {result}")
        
        logger.info("Esperando 2 segundos más después del clic")
        time.sleep(2)
        
        # Verificar si el clic fue exitoso
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='notsearch_password']"))
            )
            logger.info("Campo de contraseña encontrado, clic exitoso")
            return True
        except TimeoutException:
            logger.error("No se pudo encontrar el campo de contraseña después del clic")
            return False
        
    except TimeoutException:
        logger.error("No se pudo encontrar el elemento Two-Step Verification")
        return False
    except JavascriptException as e:
        logger.error(f"Error al ejecutar JavaScript: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado al intentar hacer clic en Two-Step Verification: {str(e)}")
        return False
    
def find_and_click_change_password(driver):
    logger.info("Intentando encontrar y hacer clic en el botón 'Change Password'")
    
    selector = "//button[contains(.,'Change Password')]"
    
    try:
        logger.info(f"Intentando con el selector: {selector}")
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, selector))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(1)  # Pequeña pausa para asegurar que el elemento esté visible
        driver.execute_script("arguments[0].click();", element)
        logger.info("Botón 'Change Password' encontrado y clicado")
        return True
    except Exception as e:
        logger.error(f"No se pudo hacer clic en 'Change Password'. Error: {str(e)}")
        return False
    
def wait_and_click_with_retry(driver, selector, description, timeout=30):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", element)
        logger.info(f"Clic en {description} realizado")
        return True
    except Exception as e:
        logger.error(f"Error al hacer clic en {description}: {str(e)}")
        return False

def click_continue_button(driver, max_retries=3):
    selectors = [
        ("#column-left > div > div.tabs-tab.sidebar-slider-item.scrolled-top.scrolled-bottom.scrollable-y-bordered.two-step-verification.two-step-verification-hint.active > div.sidebar-content > div > div.sidebar-left-section-container > div > div > div.input-wrapper > button.btn-primary.btn-color-primary.rp > div", By.CSS_SELECTOR),
        ("//*[@id='column-left']/div/div[7]/div[2]/div/div[2]/div/div/div[2]/button[1]/div", By.XPATH)
    ]
    
    for attempt in range(max_retries):
        for selector, by in selectors:
            try:
                logger.info(f"Intentando clic en 'Continuar' con selector: {selector}")
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((by, selector))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", element)
                logger.info(f"Clic en 'Continuar' realizado con éxito usando {by}: {selector}")
                return True
            except Exception as e:
                logger.warning(f"Error al hacer clic en 'Continuar' con {by}: {selector}. Error: {str(e)}")
        
        if attempt < max_retries - 1:
            logger.info(f"Reintentando en 2 segundos (intento {attempt + 2} de {max_retries})")
            time.sleep(2)
    
    logger.error(f"No se pudo hacer clic en 'Continuar' después de {max_retries} intentos con todos los selectores")
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
