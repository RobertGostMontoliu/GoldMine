import sys
from ui.config import DEBUG
from ui.appStart import QApplication, load_screen_index, AdministradorPrincipal, set_screen

if not DEBUG:
    sys.tracebacklimit = 0
    
def run():
    # Initialize the Qt application
    app = QApplication(sys.argv)

    # Load screen index config and create the main window
    screen_index = load_screen_index()
    ex = AdministradorPrincipal()

    # Set the main window to open on the specified screen and resize
    set_screen(app, ex, screen_index)

    ex.show()
    sys.exit(app.exec_())