from selenium import webdriver
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException, WebDriverException, ElementClickInterceptedException, NoSuchElementException
import argparse
from ui.api_manager import GPMManager, ADSPowerManager, ChromeManager
from ui.components import ConfigManager
from ui.Sonic.RabbyHandler import RabbyHandler


def PlayArcadeGames(driver=None, profile_id=None, **kwargs):
    max_retries = 2
    gpm_manager = GPMManager()  # Instancia de GPMManager

    if driver is None:
        print("No se pudo iniciar el navegador.")
        return

    try:
        rabby_handler = RabbyHandler(driver)
        
        # Abrir el sitio web
        driver.get("https://arcade.soniclabs.com/game/plinko")
        print("Página de Plinko abierta")

        # Esperar y hacer clic en el botón "Connect Wallet" si está disponible
        try:
            connect_wallet_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'Connect Wallet')]"))
            )
            connect_wallet_button.click()
            print("Se hizo clic en 'Connect Wallet'")

            # Esperar y hacer clic en el botón "Rabby Connect"
            rabby_connect_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//img[@alt='connector_Rabby']"))
            )
            rabby_connect_button.click()
            print("Se hizo clic en 'Rabby Connect'")

            time.sleep(2)  # Esperar un poco antes de buscar la ventana de Rabby

            if rabby_handler.verificar_y_manejar_rabby():
                print("Rabby manejado exitosamente")
            else:
                print("No se pudo manejar Rabby")

            # Esperar 10 segundos para ver si se completó todo
            time.sleep(10)
            print("Se esperó 10 segundos después de conectar la wallet")

        except TimeoutException:
            print("No se encontró el botón 'Connect Wallet' o 'Rabby Connect'")
            
        # Lógica principal del juego
        while True:  # O cualquier condición que determines para el bucle principal del juego
            # Verificar si hay una ventana de Rabby antes de cada acción
            if rabby_handler.verificar_y_manejar_rabby():
                print("Se manejó una ventana de Rabby")
            
            # Verificar nuevamente después de la acción
            if rabby_handler.verificar_y_manejar_rabby():
                print("Se manejó una ventana de Rabby después de la acción")
            
            # Continuar con la lógica del juego
            # ...
        
        print("Farmeo exitoso. Cerrando el perfil.")
    except Exception as e:
        print(f"Ocurrió un error durante el proceso: {str(e)}")
    finally:
        print("Finalizando el proceso.")
        if profile_id:
            # Cerrar el perfil desde la API
            gpm_manager.close_browser(profile_id)


def PlayPlinko(driver):
    try:
        # Abrir el sitio web
        driver.get("https://arcade.soniclabs.com/game/plinko")
    except Exception as e:
        print(f"Error al abrir el sitio web: {str(e)}")
        return False
    return True


# --- MultiThread Integration ---

def start_multithread_farming(profiles, num_concurrent, window_settings):
    """
    Inicia el farmeo de múltiples perfiles usando la infraestructura de multihilo.

    :param profiles: Lista de IDs de perfiles para farmear.
    :param num_concurrent: Número de perfiles concurrentes.
    :param window_settings: Configuraciones de ventana.
    :return: None
    """
    iniciar_farmeo_multiple(profiles, num_concurrent, "ArcadeGames", window_settings)


# --- MAIN ---
def parse_arguments():
    parser = argparse.ArgumentParser(description="Ejecutar Arcade Games")
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

    PlayArcadeGames(driver=None, profile_id=None, **kwargs)
