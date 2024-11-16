from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import argparse
from ui.api_manager import GPMManager, ADSPowerManager, ChromeManager

def interactuar_con_twitter(token, driver=None, profile_id=None, **kwargs):
    """
    Lógica principal del farmeo de Blum en Telegram utilizando Selenium.
    """
    max_retries = 2
    gpm_manager = GPMManager()  # Instancia de GPMManager

    for attempt in range(max_retries):
        if driver is None:
            print("No se pudo iniciar el navegador.")
            return
        try:
            if login_twitter_con_token(driver, token):
                print("Farmeo exitoso. Cerrando el perfil.")
                break  # Si el farmeo fue exitoso, salimos del bucle
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

def login_twitter_con_token(driver, token):
    try:
        # Ir a X (anteriormente Twitter)
        driver.get("https://x.com")
        
        # Crear y añadir la cookie de autenticación
        auth_cookie = {
            'name': 'auth_token',
            'value': token,
            'domain': '.x.com',
            'path': '/'
        }
        driver.add_cookie(auth_cookie)
        
        # Recargar la página para aplicar la cookie
        driver.refresh()
        
        # Esperar a que se cargue la página de inicio de X
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='primaryColumn']")))
        print("Login exitoso en X (Twitter)")
    except TimeoutException:
        print("Tiempo de espera agotado al intentar iniciar sesión en X (Twitter)")
        raise
    except Exception as e:
        print(f"Error durante el login en X (Twitter): {str(e)}")
        raise

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

    interactuar_con_twitter(token="", driver=None, profile_id=None, **kwargs)
