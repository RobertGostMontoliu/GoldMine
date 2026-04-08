import os
import sys

# Función para obtener la ruta correcta, compatible con PyInstaller
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        # Si la ruta comienza con "ui/", agregar "src/" al principio
        if relative_path.startswith("ui/"):
            base_path = os.path.abspath(".")
        else:
            # Para otros casos, obtener el directorio del archivo actual
            base_path = os.path.dirname(os.path.abspath(__file__))
            base_path = os.path.dirname(base_path)  # subir un nivel desde ui/ a src/
        
        # Si relative_path comienza con "ui/", buscar en la raíz
        if relative_path.startswith("ui/"):
            # Buscar si estamos en src/ui o solo ui
            if os.path.exists(os.path.join(base_path, relative_path)):
                return os.path.join(base_path, relative_path)
            else:
                # Intentar agregar "src/" si no existe
                return os.path.join(base_path, "src", relative_path)
    
    return os.path.join(base_path, relative_path)