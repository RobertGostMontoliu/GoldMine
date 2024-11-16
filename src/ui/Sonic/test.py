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
from PyQt5.QtWidgets import QMessageBox

def parse_arguments():
    parser = argparse.ArgumentParser(description="Ejecutar farmeo de Plinko")
    parser.add_argument("--browser", type=str, required=True, help="Tipo de navegador (gpm, ads, chrome)")
    parser.add_argument("--profile_id", type=str, help="ID del perfil para GPM")
    parser.add_argument("--profile_name", type=str, help="Nombre del perfil para Chrome")
    parser.add_argument("--win_scale", type=float, help="Escala de la ventana")
    parser.add_argument("--win_pos", type=str, help="Posición de la ventana (x,y)")
    parser.add_argument("--win_size", type=str, help="Tamaño de la ventana (ancho,alto)")
    return parser.parse_args()

def abrir_y_farmear_plinko(browser, driver=None, profile_id=None, profile_name=None, **kwargs):
    print(f"abrir_y_farmear_plinko llamado con: browser={browser}, profile_id={profile_id}, kwargs={kwargs}")
    if driver is None:
        if browser == "gpm":
            gpm_manager = GPMManager()
            driver = gpm_manager.open_profile(profile_id, **kwargs)
            print(f"Abierto el perfil GPM: {profile_id}")
            if driver is None:
                print(f"No se pudo abrir el perfil GPM: {profile_id}")
                return
        else:
            raise ValueError("Tipo de navegador no soportado")
    
    if driver is None:
        print("No se pudo iniciar el navegador.")
        return

    try:
        # Abrir el sitio web
        driver.get("https://arcade.soniclabs.com/game/plinko")

        # Guardar el identificador de la ventana principal
        main_window = driver.current_window_handle

        # Esperar y hacer clic en el botón "Connect Wallet" si está disponible
        try:
            connect_wallet_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'Connect Wallet')]"))
            )
            connect_wallet_button.click()
            print("Se hizo clic en 'Connect Wallet'")

            # Esperar y hacer clic en el botón "Rabby Connect"
            rabby_connect_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//img[@alt='connector_Rabby']"))
            )
            rabby_connect_button.click()
            print("Se hizo clic en 'Rabby Connect'")
        except TimeoutException:
            print("Los botones 'Connect Wallet' o 'Rabby Connect' no estaban disponibles. Asumiendo que ya está conectado.")

        # Esperar a que se abra una nueva pestaña
        print("Esperando a que se abra la pestaña de Rabby Wallet")
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        
        # Cambiar a la nueva pestaña (la última abierta)
        driver.switch_to.window(driver.window_handles[-1])
        print("Cambiado a la pestaña de Rabby Wallet")

        # Esperar a que la página de Rabby Wallet cargue
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Intentar desbloquear Rabby Wallet
        try:
            # Esperar y encontrar el campo de contraseña
            password_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))
            )
            password_field.send_keys("Wells081995!")
            print("Contraseña ingresada")

            # Esperar y hacer clic en el botón de desbloqueo
            unlock_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/form/div[2]/div/div/div/button'))
            )
            unlock_button.click()
            print("Se hizo clic en el botón de desbloqueo")

            # Esperar a que se complete el desbloqueo (puedes ajustar este tiempo según sea necesario)
            time.sleep(5)
        except TimeoutException:
            print("No se pudo encontrar el campo de contraseña o el botón de desbloqueo")

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

        print("De vuelta en la página principal")

        # Verificar si el botón de submit está disponible y hacer clic
        try:
            submit_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )
            submit_button.click()
            print("Se hizo clic en el botón de submit")

            # Esperar a que se abra una nueva pestaña
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
            print("Se detectó una nueva pestaña")

            # Cambiar a la nueva pestaña
            new_window = [window for window in driver.window_handles if window != main_window][0]
            driver.switch_to.window(new_window)
            print("Cambiado a la nueva pestaña")

            # Esperar 2 segundos antes de interactuar con la nueva pestaña
            print("Esperando 2 segundos antes de interactuar con la nueva pestaña")
            time.sleep(2)

            # Esperar a que la página de la nueva pestaña cargue
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Interactuar con la nueva pestaña (Rabby Wallet)
            try:
                # Buscar y hacer clic en el botón de sign
                sign_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign') or contains(text(), 'Firmar')]"))
                )
                sign_button.click()
                print("Se hizo clic en el botón de sign en Rabby")

                # Esperar y hacer clic en el botón de confirmar
                confirm_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Confirmar')]"))
                )
                confirm_button.click()
                print("Se hizo clic en el botón de confirmar en Rabby")

                # Esperar a que se cierre la pestaña de Rabby
                WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(1))
                print("La pestaña de Rabby se cerró automáticamente")

            except TimeoutException:
                print("No se pudo interactuar con la pestaña de Rabby")
            except Exception as e:
                print(f"Error al interactuar con Rabby: {str(e)}")
            finally:
                # Verificar si la pestaña de Rabby aún está abierta
                if len(driver.window_handles) > 1:
                    print("La pestaña de Rabby no se cerró automáticamente. Cerrándola manualmente.")
                    driver.close()

            # Volver a la pestaña principal
            driver.switch_to.window(main_window)
            print("De vuelta en la pestaña principal")

        except TimeoutException:
            print("El botón de submit no estaba disponible o no se pudo abrir la nueva pestaña")

        # Esperar 3 segundos
        time.sleep(3)

        # Volver a detectar la ventana de Rabby
        try:
            driver.switch_to.window(driver.window_handles[-1])
            
            # Buscar y hacer clic en el botón de sign
            sign_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/footer/div/section/div[2]/div/button")))
            sign_button.click()
            print("Se hizo clic en el botón de sign en Rabby")

            # Esperar 2 segundos antes de hacer clic en el botón de confirmar
            time.sleep(2)

            # Buscar y hacer clic en el botón de confirmar
            confirm_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/footer/div/section/div[2]/div/button[1]")))
            confirm_button.click()
            print("Se hizo clic en el botón de confirmar en Rabby")

            # Esperar 2 segundos antes de volver a la ventana principal
            time.sleep(2)

        except (TimeoutException, NoSuchWindowException, WebDriverException) as e:
            print(f"No se pudo interactuar con la ventana de Rabby: {e}")

        # Volver a la pestaña principal
        driver.switch_to.window(main_window)
        print("De vuelta en la pestaña principal")

        # Esperar 2 segundos adicionales antes de comenzar a jugar
        time.sleep(2)

        # Función para obtener el número de tickets
        def get_ticket_count():
            try:
                ticket_element = driver.find_element(By.XPATH, '//*[@id="app-layout"]/div[2]/form/div/section[1]/div/div[1]/div/button[2]/span')
                ticket_text = ticket_element.text
                # Separar los dos valores
                current_tickets, total_tickets = map(int, ticket_text.split('/'))
                return current_tickets, total_tickets
            except Exception as e:
                print(f"Error al obtener el número de tickets: {e}")
                return 0, 0

        def click_element(driver, element):
            try:
                element.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", element)

        # Jugar mientras haya tickets disponibles
        while True:
            current_tickets, total_tickets = get_ticket_count()
            print(f"Tickets disponibles: {current_tickets}/{total_tickets}")
            if current_tickets <= 0:
                print("No quedan más tickets")
                break

            try:
                play_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
                )
                
                # Intentar hacer clic de varias maneras
                try:
                    click_element(driver, play_button)
                except Exception as e:
                    print(f"Error al hacer clic: {e}")
                    try:
                        ActionChains(driver).move_to_element(play_button).click().perform()
                    except Exception as e:
                        print(f"Error al usar ActionChains: {e}")
                        driver.execute_script("arguments[0].scrollIntoView(true);", play_button)
                        time.sleep(1)
                        driver.execute_script("arguments[0].click();", play_button)
                
                print("Se hizo clic en el botón de play")

                # Esperar a que se complete la jugada
                time.sleep(5)  # Ajusta este tiempo según sea necesario

            except TimeoutException:
                print("El botón de play no está disponible")
                break
            except Exception as e:
                print(f"Error inesperado: {e}")
                break

        print("Se han agotado todos los tickets o no se puede jugar más")

    finally:
            print("Finalizando el proceso.")
            if profile_id:
                # Cerrar el perfil desde la API
                gpm_manager.close_browser(profile_id)

def interactuar_con_rabby(driver, main_window):
    try:
        print("Iniciando interacción con Rabby wallet")
        # Esperar a que se abra la ventana de Rabby
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

        # Cambiar a la ventana de Rabby
        rabby_window = None
        for handle in driver.window_handles:
            if handle != main_window:
                rabby_window = handle
                driver.switch_to.window(rabby_window)
                break

        if not rabby_window:
            print("No se pudo encontrar la ventana de Rabby")
            return

        print("Cambiado a la ventana de Rabby")

        # Esperar y hacer clic en el botón de sign
        sign_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign') or contains(text(), 'Firmar')]"))
        )
        sign_button.click()
        print("Se hizo clic en el botón de sign en Rabby")

        # Esperar y hacer clic en el botón de confirmar
        confirm_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Confirmar')]"))
        )
        confirm_button.click()
        print("Se hizo clic en el botón de confirmar en Rabby")

        # Esperar a que se cierre la ventana de Rabby
        try:
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(1))
            print("La ventana de Rabby se cerró automáticamente")
        except TimeoutException:
            print("La ventana de Rabby no se cerró automáticamente, intentando cerrarla manualmente")
            driver.close()

    except Exception as e:
        print(f"Error al interactuar con Rabby: {str(e)}")

    finally:
        # Asegurarse de volver a la pestaña principal
        if main_window in driver.window_handles:
            driver.switch_to.window(main_window)
            print("De vuelta en la pestaña principal")
        else:
            print("La ventana principal ya no existe")

    # Esperar antes de continuar
    time.sleep(5)

if __name__ == "__main__":
    args = parse_arguments()
    
    kwargs = {
        "win_scale": args.win_scale,
        "win_pos": args.win_pos,
        "win_size": args.win_size
    }
    
    abrir_y_farmear_plinko(args.browser, profile_id=args.profile_id, profile_name=args.profile_name, **kwargs)

