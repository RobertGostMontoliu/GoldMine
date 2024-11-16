from ui.key_manager import KeyManager

# Generar claves de prueba
keys = {
    "free_key": 0,  # Clave para la versión gratuita (sin expiración)
    "medium_key_1": 30,  # Clave para la versión media, válida por 30 días
    "medium_key_2": 30,  # Otra clave para la versión media, válida por 30 días
    "vip_key_1": 30,  # Clave para la versión VIP, válida por 30 días
    "vip_key_2": 30,  # Otra clave para la versión VIP, válida por 30 días
}

# Agregar claves al archivo keys.json
for key, days_valid in keys.items():
    KeyManager.add_key(key, days_valid)

print("Claves generadas y guardadas en keys.json")