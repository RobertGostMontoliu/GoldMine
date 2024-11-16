from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException, WebDriverException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
import time
from ui.api_manager import GPMManager, ADSPowerManager, ChromeManager
from ui.components import ConfigManager
import argparse
import pytest

def parse_arguments():
    parser = argparse.ArgumentParser(description="Ejecutar farmeo de Plinko")
    parser.add_argument("--browser", type=str, required=True, help="Tipo de navegador (gpm, ads, chrome)")
    parser.add_argument("--profile_id", type=str, help="ID del perfil para GPM")
    parser.add_argument("--profile_name", type=str, help="Nombre del perfil para Chrome")
    parser.add_argument("--win_scale", type=float, help="Escala de la ventana")
    parser.add_argument("--win_pos", type=str, help="Posición de la ventana (x,y)")
    parser.add_argument("--win_size", type=str, help="Tamaño de la ventana (ancho,alto)")
    return parser.parse_args()

def abrir_y_farmear_claim(browser, driver=None, profile_id=None, profile_name=None, **kwargs):
    print(f"abrir_y_farmear_claim llamado con: browser={browser}, profile_id={profile_id}, kwargs={kwargs}")
    if driver is None:
        if browser == "gpm":
            gpm_manager = GPMManager()
            driver = gpm_manager.open_profile(profile_id, **kwargs)
            print(f"Abierto el perfil GPM: {profile_id}")
            if driver is None:
                print(f"No se pudo abrir el perfil GPM: {profile_id}")
                return
        elif browser == "ads":
            driver = abrir_navegador_ads(profile_id)
            print(f"Abierto el perfil ADS: {profile_id}")
        elif browser == "chrome":
            driver = abrir_navegador_chrome(profile_name)
        else:
            raise ValueError("Tipo de navegador no soportado")
    
    if driver is None:
        print("No se pudo iniciar el navegador.")
        return

    try:
        # Guardar el identificador de la ventana principal
        main_window = driver.current_window_handle
        
        # 1. Abrir la página web y esperar que cargue correctamente
        print("Abriendo la página web")
        driver.get("https://arcade.soniclabs.com/")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".bg-\\[\\#10283C\\]")))
        print("Página cargada correctamente")

        # 2. Click en connect wallet
        print("Haciendo clic en 'Connect Wallet'")
        connect_wallet = WebDriverWait(driver, 10).until(
          EC.element_to_be_clickable((By.CSS_SELECTOR, ".bg-\\[\\#10283C\\]"))
        )
        connect_wallet.click()
        print("Click en 'Connect Wallet' realizado")

        # 3. Click en Rabby
        print("Haciendo clic en Rabby")
        rabby_wallet = WebDriverWait(driver, 10).until(
          EC.element_to_be_clickable((By.CSS_SELECTOR, ".flex:nth-child(7) > .ui-inline-flex"))
        )
        rabby_wallet.click()
        print("Click en Rabby realizado")

        # 4. Esperar a que se abra una nueva pestaña y cambiar a ella
        print("Esperando a que se abra la pestaña de Rabby Wallet")
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        
        # Cambiar a la nueva pestaña (la última abierta)
        driver.switch_to.window(driver.window_handles[-1])
        print("Cambiado a la pestaña de Rabby Wallet")

        # Esperar a que la página de Rabby Wallet cargue
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # 6. Ingresar password
        print("Intentando encontrar el campo de contraseña")
        try:
          password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))
          )
          password_field.send_keys("Wells081995!")
          print("Contraseña ingresada")
        except TimeoutException:
          print("No se pudo encontrar el campo de contrasea")
          print("Contenido de la página:")
          print(driver.page_source)
          pytest.fail("No se pudo encontrar el campo de contraseña")

        # 7. Click en unlock
        print("Buscando el botón de 'Unlock'")
        try:
          unlock_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/form/div[2]/div/div/div/button'))
          )
          unlock_button.click()
          print("Click en 'Unlock' realizado")
        except TimeoutException:
          print("No se pudo encontrar el botón 'Unlock'")
          print("Contenido de la página:")
          print(driver.page_source)
          pytest.fail("No se pudo encontrar el botón 'Unlock'")

        # Esperar 3 segundos
        print("Esperando 3 segundos")
        time.sleep(3)
        
        # Verificar si la ventana de Rabby aún está abierta
        try:
          # Intentar cambiar a la ventana de Rabby
          driver.switch_to.window(driver.window_handles[-1])
          
          # Verificar si existe el botón "Ignore all"
          try:
            ignore_all_button = WebDriverWait(driver, 5).until(
              EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div/div/div/div[3]/div/div/div/span[2]'))
            )
            print("Se detectó el botón 'Ignore all'. Ejecutando variante 'Connect to Dapp'")
            
            # Variante: Connect to Dapp
            ignore_all_button.click()
            print("Click en 'Ignore all' realizado")
            
            # Click en "Connect"
            connect_button = WebDriverWait(driver, 10).until(
              EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div/div/div[3]/div/div/button[1]'))
            )
            connect_button.click()
            print("Click en 'Connect' realizado")
            
            # Esperar 2 segundos
            print("Esperando 2 segundos")
            time.sleep(2)
          except TimeoutException:
            print("No se detectó el botón 'Ignore all'. No se necesita conectar a la dapp.")
        except (NoSuchWindowException, WebDriverException):
          print("La ventana de Rabby se ha cerrado automáticamente.")

        # Asegurarse de volver a la pestaña principal
        print("Volviendo a la pestaña principal")
        driver.switch_to.window(main_window)
        
        # Esperar a que la página principal se cargue completamente
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//main[@id='app-layout']")))
        
        # Buscar y hacer clic en el botón "Add testnet"
        print("Buscando el botón 'Add testnet'")
        try:
          add_testnet_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//main[@id='app-layout']/div/div/div/div/div[4]/a"))
          )
          # Usar JavaScript para hacer clic en el botón
          driver.execute_script("arguments[0].click();", add_testnet_button)
          print("Click en 'Add testnet' realizado")
        except TimeoutException:
          print("No se pudo encontrar el botón 'Add testnet'")
          print("Contenido de la página:")
          print(driver.page_source)
          pytest.fail("No se pudo encontrar el botón 'Add testnet'")

        # Esperar 3 segundos
        print("Esperando 3 segundos")
        time.sleep(3)

        # Verificar si la ventana de Rabby se ha abierto nuevamente
        try:
          # Intentar cambiar a la última ventana abierta
          driver.switch_to.window(driver.window_handles[-1])
          
          # Verificar si existe el botón "ADD"
          try:
            add_button = WebDriverWait(driver, 5).until(
              EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div[3]/button[2]'))
            )
            print("Se detectó el botón 'ADD'. Ejecutando variante 'Add Testnet'")
            
            # Variante: Add Testnet
            add_button.click()
            print("Click en 'ADD' realizado")
            
            # Esperar 2 segundos
            print("Esperando 2 segundos")
            time.sleep(2)
          except TimeoutException:
            print("No se detectó el botón 'ADD'. No se necesita agregar el testnet.")
        except (NoSuchWindowException, WebDriverException):
          print("No se detectó una nueva ventana de Rabby.")

        # Asegurarse de volver a la pestaña principal
        driver.switch_to.window(main_window)
        print("Volviendo a la pestaña principal")

        # Pausa para asegurar que la página se ha cargado completamente
        time.sleep(5)

        # Hacer clic en "Get some tokens"
        print("Buscando el botón 'Get some tokens'")
        try:
          get_tokens_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//main[@id='app-layout']/div/div/div/div[2]/div[3]/a"))
          )
          driver.execute_script("arguments[0].click();", get_tokens_button)
          print("Click en 'Get some tokens' realizado")
        except TimeoutException:
          print("No se pudo encontrar el botón 'Get some tokens'")
          print("Contenido de la página:")
          print(driver.page_source)
          pytest.fail("No se pudo encontrar el botón 'Get some tokens'")

        # Verificar si el usuario está logueado con Twitter
        print("Verificando estado de login con Twitter")
        try:
          sign_in_button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(.,'Sign in with')]"))
          )
          print("Usuario no está logueado. Haciendo clic en 'Sign in with Twitter'")
          driver.execute_script("arguments[0].click();", sign_in_button)
          print("Click en 'Sign in with Twitter' realizado")

          # Esperar y hacer clic en el botón de autorización de Twitter
          print("Esperando el botón de autorización de Twitter")
          try:
            authorize_button = WebDriverWait(driver, 10).until(
              EC.element_to_be_clickable((By.XPATH, "//div[@id='react-root']/div/div/div[2]/main/div/div/div[2]/div/div/div/div[3]/button/div/span/span"))
            )
            driver.execute_script("arguments[0].click();", authorize_button)
            print("Click en el botón de autorización de Twitter realizado")
          except TimeoutException:
            print("No se pudo encontrar el botón de autorización de Twitter")
            print("Contenido de la página:")
            print(driver.page_source)
            pytest.fail("No se pudo encontrar el botón de autorización de Twitter")

        except TimeoutException:
          print("No se detectó el botón 'Sign in with Twitter'. El usuario ya está logueado o no es necesario iniciar sesión.")

        # Verificar si necesitamos seguir a @0xSonicLabs
        print("Verificando si necesitamos seguir a @0xSonicLabs")
        try:
          follow_button = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(.,'Follow @0xSonicLabs')]"))
          )
          print("Se detectó que necesitamos seguir a @0xSonicLabs")
          
          # Hacer clic en el botón de seguir
          driver.execute_script("arguments[0].click();", follow_button)
          print("Click en 'Follow @0xSonicLabs' realizado")
          
          # Esperar 5 segundos
          print("Esperando 5 segundos")
          time.sleep(5)
          
          # Volver a la pestaña principal
          driver.switch_to.window(main_window)
          print("Volviendo a la pestaña principal")
          
        except TimeoutException:
          print("No se detectó la necesidad de seguir a @0xSonicLabs. Continuando con el siguiente paso.")
        except WebDriverException as e:
          print(f"Error al interactuar con el botón: {str(e)}")
          print("Continuando con el siguiente paso...")

        # Get $420 tokens
        print("Iniciando proceso para obtener $420 tokens")

        # Paso 1: Volver atrás
        print("Volviendo atrás")
        try:
          back_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ring-offset-background > svg"))
          )
          driver.execute_script("arguments[0].click();", back_button)
          print("Click en botón 'Volver' realizado")
        except TimeoutException:
          print("No se pudo encontrar el botón para volver atrás")
          pytest.fail("No se pudo encontrar el botón para volver atrás")

        # Paso 2: Volver a presionar el botón de "Get some $token"
        print("Buscando el botón 'Get some $token'")
        try:
          get_tokens_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//main[@id='app-layout']/div/div/div/div[2]/div[3]/a"))
          )
          driver.execute_script("arguments[0].click();", get_tokens_button)
          print("Click en 'Get some $token' realizado")
        except TimeoutException:
          print("No se pudo encontrar el botón 'Get some $token'")
          pytest.fail("No se pudo encontrar el botón 'Get some $token'")

        # Paso 3: Hacer click en "Get 420 $TOKEN"
        print("Buscando el botón 'Get 420 $TOKEN'")
        try:
          get_420_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Get 420 $TOKEN')]"))
          )
          driver.execute_script("arguments[0].click();", get_420_button)
          print("Click en 'Get 420 $TOKEN' realizado")
        except TimeoutException:
          print("No se pudo encontrar el botón 'Get 420 $TOKEN'")
          pytest.fail("No se pudo encontrar el botón 'Get 420 $TOKEN'")

        # Pausa final
        print("Pausa de 10 segundos para verificación visual")
        time.sleep(10)

    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        pytest.fail(f"Error inesperado: {str(e)}")
      
    print("Test completado con éxito")

# ABRIR NAVEGADORES EN ADS
def abrir_navegador_ads(profile_id):
    ads_manager = ADSPowerManager(ConfigManager.get_ads_url())
    # Aquí iría la lógica para abrir el perfil de ADS
    # Por ahora, usaremos un navegador Chrome normal como ejemplo
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service)

# ABRIR NAVEGADORES EN GOOGLE CHROME
def abrir_navegador_chrome(profile_name):
    chrome_manager = ChromeManager(ConfigManager.get_chrome_path())
    # Aquí iría la lógica para abrir el perfil de Chrome
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={ConfigManager.get_chrome_path()}")
    options.add_argument(f"profile-directory={profile_name}")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

if __name__ == "__main__":
    args = parse_arguments()
    
    kwargs = {
        "win_scale": args.win_scale,
        "win_pos": args.win_pos,
        "win_size": args.win_size
    }
    
    abrir_y_farmear_claim(args.browser, profile_id=args.profile_id, profile_name=args.profile_name, **kwargs)
