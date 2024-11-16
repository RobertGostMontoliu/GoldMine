import concurrent.futures
import logging
from matplotlib.pyplot import sca
import pyautogui
from ui.api_manager import GPMManager
from ui.components import ConfigManager
from ui.Sonic.test2 import abrir_y_farmear_claim
from ui.Sonic.Arcadegames import PlayArcadeGames
from ui.twitter.TwitterBackend.TwitterLogin import interactuar_con_twitter
import threading
import time
from PyQt5.QtCore import QThread
from ui.Blum.BlumBackend.BlumClaim import abrir_y_farmear_blum
from ui.FarmeosTelegram.Pawns.PawnsBackend.PawnsScript import abrir_y_farmear_pawns
from ui.FarmeosTelegram.TronKeeper.TronBackend.TronScript import abrir_y_farmear_tronkeeper
from ui.Wallets.RabbyBackend.RabbyScript import rabby_Wallets
from ui.Wallets.MetamaskBackend.MetamaskScript import metamask_Wallets
from ui.Wallets.TonKeeperBackend.TonKeeperScript import tonkeeper_Wallets
from ui.Wallets.PhantomBackend.PhantomScript import phantom_Wallets
from ui.WolfGame.Backend.WolfGameScript import WolfGame
from ui.Wow.Backend.WowScript import Wow
from ui.Wallets.RoninBackend.RoninScript import ronin_Wallets
from ui.TelegramTool.telegram_backend.TelegramSignIn import telegramTool
from ui.TelegramTool.telegram_backend.TelegramPassword import telegramToolPassword
 
# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
MARGIN = 10  # A small margin to prevent windows from being too close

class PositionManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.occupied_positions = {}  # Almacena la posición en formato {(row, col): (x, y)}
        self.max_columns = 0
        self.max_rows = 0

    def initialize_grid(self, scaled_window_width, scaled_window_height):
        # Calcular el número máximo de columnas y filas según el tamaño de pantalla
        self.max_columns = SCREEN_WIDTH // (scaled_window_width + MARGIN)
        self.max_rows = SCREEN_HEIGHT // (scaled_window_height + MARGIN)

        # Limpiar la tabla de posiciones ocupadas
        self.occupied_positions = {}

    def get_next_position(self, scaled_window_width, scaled_window_height, scale_factor):
        # Inicializar la cuadrícula si es la primera vez
        if not self.occupied_positions:
            self.initialize_grid(scaled_window_width, scaled_window_height)

        # Calcular el ajuste basado en el inverso del factor de escala
        adjustment_factor = 1 / scale_factor if scale_factor != 1 else 1

        with self.lock:
            for row in range(self.max_rows):
                for col in range(self.max_columns):
                    if (row, col) not in self.occupied_positions:  # Verificar si la posición está libre
                        # Calcular las coordenadas (x, y) para la posición con el ajuste aplicado
                        x_position = int(col * (scaled_window_width + MARGIN) * adjustment_factor)
                        y_position = int(row * (scaled_window_height + MARGIN) * adjustment_factor)
                        position = (x_position, y_position)
                        
                        logger.info(f"POSICION LIBRE ENCONTRADA Y ASIGNADA --> {position} en fila {row}, columna {col}")

                        # Marcar como ocupada y almacenar la posición
                        self.occupied_positions[(row, col)] = position
                        return position

            # Si no hay posiciones disponibles, devolver None
            logger.info("No hay posiciones disponibles en la cuadrícula")
            return None

    def release_position(self, position):
        with self.lock:
            # Encontrar la fila y columna correspondiente a la posición
            for (row, col), pos in self.occupied_positions.items():
                if pos == position:
                    logger.info(f"LIBERANDO POSICIÓN --> {position} en fila {row}, columna {col}")
                    del self.occupied_positions[(row, col)]
                    break
            else:
                logger.warning(f"No se encontró la posición {position} en ocupaciones para liberar.")

position_manager = PositionManager()

def process_profile(profile_id, farming_function, browser, window_settings, **kwargs):
    # Obtener el tamaño y escala de la ventana desde window_settings
    window_size = window_settings.get('win_size', '500,500')  # Valores por defecto si no se proporcionan
    window_width, window_height = map(int, window_size.split(','))

    # Obtener el factor de escala de la ventana y aplicarlo
    scale_factor = window_settings.get('win_scale', 1.0)
    scaled_window_width = int(window_width * scale_factor)
    scaled_window_height = int(window_height * scale_factor)

    # Esperar una posición disponible en la cuadrícula
    while True:
        position = position_manager.get_next_position(scaled_window_width, scaled_window_height, scale_factor)
        if position:
            break
        logger.info(f"No available position for profile {profile_id}, waiting...")
        time.sleep(1)  # Espera de 1 segundo antes de intentar de nuevo

    # Configurar la posición (x, y) en window_settings
    window_settings['win_pos'] = f"{position[0]},{position[1]}"
    
    # Abrir el perfil con la posición y el tamaño configurado
    gpm_manager = GPMManager(ConfigManager.get_gpm_url())
    driver = gpm_manager.open_profile(profile_id, **window_settings)
    
    try:
        if driver:
            logger.info(f"Perfil GPM abierto exitosamente: {profile_id}")
            
            # Configurar el nivel de zoom con el valor de 'zoom' ya preprocesado
            zoom_level = window_settings.get('zoom', 1.0)  # El valor por defecto es 100% (1.0)
            driver.execute_script(f"document.body.style.zoom='{zoom_level}'")  # Aplicar el zoom directamente
            
            # Llamar a la función de farmeo según el tipo
            if farming_function == "blum":
                abrir_y_farmear_blum(driver=driver, profile_id=profile_id, is_blum_clicker_activated=window_settings.get("blum_clicker_activado", False))
            elif farming_function == "ArcadeGames":
                PlayArcadeGames(driver=driver, profile_id=profile_id, **kwargs)
            elif farming_function == "claim":
                abrir_y_farmear_claim(browser, driver=driver, profile_id=profile_id, profile_name="", **kwargs)
            elif farming_function == "twitter":
                interactuar_con_twitter(driver=driver, token=profile_id, browser_type=browser, profile_id=profile_id, profile_name="", **kwargs)
            elif farming_function == "rabby":
                rabby_Wallets(password="", perfil="", driver=driver, profile_id=profile_id, directorio_excel="", **kwargs)
            elif farming_function == "TelegramTool":
                telegramTool(driver=driver, profile_id=profile_id, **kwargs)
            elif farming_function == "telegramToolPassword":
                telegramToolPassword(driver=driver, profile_id=profile_id, **kwargs)
            elif farming_function == "metamask":
                metamask_Wallets(password="", profile_id=profile_id, perfil_id=profile_id, perfil_nombre="", driver=driver, **kwargs) 
            elif farming_function == "TonKeeper":
                tonkeeper_Wallets(password="123456789", profile_id=profile_id, perfil_id=profile_id, perfil_nombre="", driver=driver, **kwargs) 
            elif farming_function == "Phantom":
                phantom_Wallets(password="123456789", profile_id=profile_id, perfil_id=profile_id, perfil_nombre="", driver=driver, **kwargs) 
            elif farming_function == "WolfGame":
                WolfGame(driver=driver, profile_id=profile_id, **kwargs)
            elif farming_function == "Wow":
                Wow(driver=driver, profile_id=profile_id, **kwargs)
            elif farming_function == "Ronin":
                ronin_Wallets(password="123456789", profile_id=profile_id, perfil_id=profile_id, perfil_nombre="", driver=driver, **kwargs)
            elif farming_function == "pawns":
                abrir_y_farmear_pawns(driver=driver, profile_id=profile_id, is_pawns_clicker_activated=window_settings.get("pawns_clicker_activado", False))
            elif farming_function == "tronkeeper":
                abrir_y_farmear_tronkeeper(driver=driver, profile_id=profile_id, is_tronkeeper_clicker_activated=window_settings.get("tronkeeper_clicker_activado", False))
            else:
                logger.error(f"Función de farmeo no reconocida: {farming_function}")
        else:
            logger.error(f"No se pudo abrir el perfil GPM: {profile_id}")
    except Exception as e:
        logger.error(f"Error al procesar el perfil {profile_id}: {str(e)}")
    finally:
        if driver:
            driver.quit()
        position_manager.release_position(position)

class FarmingThread(QThread):
    def __init__(self, profiles, num_concurrent, farming_function, browser, window_settings, **kwargs):
        super().__init__()
        self.profiles = profiles
        self.num_concurrent = num_concurrent
        self.farming_function = farming_function
        self.browser = browser
        self.window_settings = window_settings
        self.kwargs = kwargs  # Almacenar los kwargs para pasarlos a la función
        self.is_running = False

    def run(self):
        self.is_running = True
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_concurrent) as executor:
            futures = []
            for profile_id in self.profiles:
                if not self.is_running:
                    break
                # Submit each profile with a delay of 0.5 seconds between each
                futures.append(executor.submit(process_profile, profile_id, self.farming_function, self.browser, self.window_settings.copy(), **self.kwargs))
                time.sleep(1)  # Delay between opening each profile
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error en el proceso de farmeo: {str(e)}")
        self.is_running = False

def iniciar_farmeo_multiple(profiles, num_concurrent, farming_type, window_settings):
    if farming_type == "claim":
        farming_function = "claim"
    elif farming_type == "ArcadeGames":
        farming_function = "ArcadeGames"
    elif farming_type == "blum":
        farming_function = "blum"
    elif farming_type == "twitter":
        farming_function = "twitter"
    elif farming_type == "rabby":
        farming_function = "rabby" 
    elif farming_type == "metamask":
        farming_function = "metamask"
    elif farming_type == "TelegramTool":
        farming_function = "TelegramTool"
    elif farming_type == "telegramToolPassword":
        farming_function = "telegramToolPassword"
    elif farming_type == "TonKeeper":
        farming_function = "TonKeeper"
    elif farming_type == "Phantom":
        farming_function = "Phantom"
    elif farming_type == "WolfGame":
        farming_function = "WolfGame"
    elif farming_type == "Wow":
        farming_function = "Wow"
    elif farming_type == "Ronin":
        farming_function = "Ronin"
    elif farming_type == "pawns":
        farming_function = "pawns"
    elif farming_type == "tronkeeper":
        farming_function = "tronkeeper"
    else:
        logger.error(f"Función de farmeo no reconocida: {farming_type}")
        return

    # Definir el tipo de navegador
    browser = window_settings.get('browser', 'gpm')  # Aquí, puedes ajustar el tipo de navegador según la configuración

    # Corregir la llamada a FarmingThread pasando browser y window_settings
    farming_thread = FarmingThread(profiles, num_concurrent, farming_function, browser, window_settings)
    farming_thread.start()

    return farming_thread
