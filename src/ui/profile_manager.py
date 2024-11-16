from ui.api_manager import GPMManager, ADSPowerManager, ChromeManager
from ui.components import ConfigManager

class ProfileManager:
    _profiles = []  # Definir la lista de perfiles como un atributo de clase

    def __init__(self):
        pass

    def fetch_profiles_from_gpm(self, api_url):
        gpm_manager = GPMManager(api_url)
        profiles = gpm_manager.fetch_profiles()
        self.display_profiles(profiles)

    def fetch_profiles_from_adspower(self, api_key):
        adspower_manager = ADSPowerManager(api_key)
        profiles = adspower_manager.fetch_profiles()
        self.display_profiles(profiles)

    def fetch_profiles_from_chrome(self, profile_path):
        chrome_manager = ChromeManager(profile_path)
        profiles = chrome_manager.fetch_profiles()
        self.display_profiles(profiles)

    def display_profiles(self, profiles):
        # Implementar la lógica para mostrar los perfiles en la interfaz de usuario.
        print("Perfiles obtenidos:")
        for profile in profiles:
            print(profile)

    @classmethod
    def update_profiles(cls, profiles):
        cls._profiles = profiles  # Actualizar la lista de perfiles

    @classmethod
    def get_profiles(cls):
        return cls._profiles  # Retornar la lista de perfiles

    def fetch_profiles(self, browser_type):
        if browser_type == "GPM":
            return self.fetch_profiles_from_gpm(ConfigManager.get_gpm_url())
        elif browser_type == "ADS":
            return self.fetch_profiles_from_adspower(ConfigManager.get_ads_url())
        elif browser_type == "Chrome":
            return self.fetch_profiles_from_chrome(ConfigManager.get_chrome_path())
        else:
            raise ValueError("Tipo de navegador no soportado")
