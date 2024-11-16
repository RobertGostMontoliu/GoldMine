from PyQt5.QtWidgets import QTableWidgetItem
from ui.PlantillaAirdrop import PlantillaAirdrop
from ui.api_manager import GPMManager, ADSPowerManager, ChromeManager
from ui.components import ConfigManager

class ImxPage(PlantillaAirdrop):
    def __init__(self, window):
        # Llamamos al constructor de la plantilla base con el título específico de Sonic Airdrop
        super().__init__(title="IMX Airdrop")
        self.window = window

        # Cargar la tabla de perfiles
        self.load_profiles_from_api("GPM")  # Por ejemplo, cargar perfiles desde GPM al inicio

    def load_profiles_from_api(self, source):
        """
        Esta función es llamada para cargar perfiles desde la API seleccionada.
        """
        profile_table = self.profile_table  # La tabla que está en la plantilla
        profile_table.setRowCount(0)  # Limpiar la tabla antes de cargar nuevos perfiles

        if source == "GPM":
            gpm_manager = GPMManager(ConfigManager.get_gpm_url())
            profiles = gpm_manager.fetch_profiles()
            for i, profile in enumerate(profiles):
                profile_table.insertRow(i)
                profile_table.setItem(i, 0, QTableWidgetItem(profile["name"]))
                profile_table.setItem(i, 1, QTableWidgetItem(profile["id"]))
                # Verificamos si el campo "group_id" existe y lo mostramos
                group_id = profile.get("group_id", "Sin Grupo")  # Revisar si está presente el group_id
                profile_table.setItem(i, 2, QTableWidgetItem(str(group_id)))  # Convertir a string si no lo es

        elif source == "ADS":
            adspower_manager = ADSPowerManager(ConfigManager.get_ads_url())
            profiles = adspower_manager.fetch_profiles()
            for i, profile in enumerate(profiles):
                profile_table.insertRow(i)
                profile_table.setItem(i, 0, QTableWidgetItem(profile["name"]))
                profile_table.setItem(i, 1, QTableWidgetItem(profile["user_id"]))
                profile_table.setItem(i, 2, QTableWidgetItem(profile.get("group_name", "Sin Grupo")))

        elif source == "Chrome":
            chrome_manager = ChromeManager(ConfigManager.get_chrome_path())
            profiles = chrome_manager.fetch_profiles()
            for i, profile in enumerate(profiles):
                profile_table.insertRow(i)
                profile_table.setItem(i, 0, QTableWidgetItem(profile))
