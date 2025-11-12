import sys
import os
import json
import json.decoder
from PyQt5.QtWidgets import QApplication, QMessageBox
from ui.main_window import AdministradorPrincipal
from PyQt5.QtCore import QSettings
from ui.api_manager import GPMManager


# Función para obtener la ruta correcta, compatible con PyInstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Load screen configuration from config.json
def load_screen_index():
    config_path = resource_path("src//ui//JSON_FILE//config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
            return int(
                config.get("screen_index", 1)
            )  # Convertir a int y por defecto a 1
    return 1


# Function to set the window on the specified screen and apply geometry settings
def set_screen(app, window, screen_index):
    screens = app.screens()
    screen_count = len(screens)

    # Ensure screen_index is within bounds and adjust to 0-based indexing
    screen_index = max(1, min(screen_index, screen_count)) - 1
    selected_screen = screens[screen_index]

    # Get the geometry of the specified screen
    screen_geometry = selected_screen.geometry()

    # Center and resize within this screen's geometry
    width = int(screen_geometry.width() * 0.75)
    height = int(screen_geometry.height() * 0.8)
    left = screen_geometry.left() + (screen_geometry.width() - width) // 2
    top = screen_geometry.top() + (screen_geometry.height() - height) // 2

    # Set the window geometry and move it to the desired screen
    window.setGeometry(left, top, width, height)
    window.move(left, top)  # Explicitly move the window to the calculated position


if __name__ == "__main__":
    # Initialize the Qt application
    app = QApplication(sys.argv)

    # Load screen index config and create the main window
    screen_index = load_screen_index()
    ex = AdministradorPrincipal()

    # Set the main window to open on the specified screen and resize
    set_screen(app, ex, screen_index)

    ex.show()
    sys.exit(app.exec_())
