import numpy as np
import os
import time

class MapaLaberinto:
    def __init__(self, size=600):
        self.size = size
        self.active = True
        # Matriz de movimientos: 0 = no visitado, 1 = visitado normal, 2 = backtracking
        self.matriz_movimientos = np.zeros((size, size), dtype=int)
        # Diccionario para almacenar los perfiles que han visitado cada casilla
        self.matriz_perfiles = {}
        self.contador_pasos = 0
        # Matriz para los spawns: 0 = no spawn, 1 = área de spawn
        self.matriz_spawns = np.zeros((size, size), dtype=int)
        self._inicializar_spawns()

    def _inicializar_spawns(self):
        """
        Inicializa las áreas de spawn (25 áreas de 5x5)
        """
        # Coordenadas base para los spawns (x, y)
        spawn_bases = [
            # Primera fila (y=100)
            (100, 100), (200, 100), (300, 100), (400, 100), (500, 100),
            # Segunda fila (y=200)
            (100, 200), (200, 200), (300, 200), (400, 200), (500, 200),
            # Tercera fila (y=300)
            (100, 300), (200, 300), (300, 300), (400, 300), (500, 300),
            # Cuarta fila (y=400)
            (100, 400), (200, 400), (300, 400), (400, 400), (500, 400),
            # Quinta fila (y=500)
            (100, 500), (200, 500), (300, 500), (400, 500), (500, 500)
        ]
        
        # Crear áreas de 5x5 alrededor de cada spawn
        for base_x, base_y in spawn_bases:
            for dx in range(-2, 3):  # 5x5 área
                for dy in range(-2, 3):
                    x, y = base_x + dx, base_y + dy
                    if 0 <= x < self.size and 0 <= y < self.size:
                        self.matriz_spawns[y, x] = 1

    def is_active(self):
        """
        Verifica si el mapa está activo y utilizable
        """
        return self.active and hasattr(self, 'matriz_movimientos') and self.matriz_movimientos is not None

    def agregar_visita(self, x, y, profile_id, is_backtracking=False):
        """
        Registra la visita de un perfil a una casilla
        Args:
            x: coordenada x (0-599)
            y: coordenada y (0-599)
            profile_id: número de perfil
            is_backtracking: indica si es un movimiento de retroceso
        """
        # Validar coordenadas
        if not (0 <= x < self.size and 0 <= y < self.size):
            print(f"Coordenadas fuera de rango: x={x}, y={y}")
            return False

        # Extraer solo el número del perfil
        try:
            # Si el profile_id viene como "profile_X" o similar
            if isinstance(profile_id, str) and '_' in profile_id:
                profile_num = profile_id.split('_')[-1]
            else:
                # Si ya es un número o string numérico
                profile_num = str(profile_id)
            
            # Asegurar que solo tenemos dígitos
            profile_num = ''.join(filter(str.isdigit, profile_num))
            
            if not profile_num:
                print(f"No se pudo extraer número de perfil válido de: {profile_id}")
                return False
                
        except Exception as e:
            print(f"Error procesando profile_id: {e}")
            return False

        key = f"{x},{y}"
        if key not in self.matriz_perfiles:
            self.matriz_perfiles[key] = set()
        self.matriz_perfiles[key].add(profile_num)

        # Actualizar matriz de movimientos
        if self.matriz_movimientos[y, x] == 0:
            self.matriz_movimientos[y, x] = 1
            self.contador_pasos += 1
        elif is_backtracking:
            self.matriz_movimientos[y, x] = 2

def crear_laberinto(filename, size=600):
    """
    Crea un nuevo mapa de laberinto y lo guarda en formato NPZ
    """
    mapa = MapaLaberinto(size)
    guardar_mapa(filename, mapa)
    return mapa

def abrir_documento(filename):
    """
    Carga un mapa existente desde archivo NPZ
    """
    if not os.path.exists(filename):
        return crear_laberinto(filename)
    
    try:
        data = np.load(filename, allow_pickle=True)
        mapa = MapaLaberinto()
        mapa.matriz_movimientos = data['movimientos']
        mapa.matriz_perfiles = {k: set(v) for k, v in data['perfiles'].item().items()}
        mapa.contador_pasos = data['contador_pasos']
        mapa.active = True
        return mapa
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return crear_laberinto(filename)

def guardar_mapa(filename, mapa):
    """
    Guarda el mapa actual en formato NPZ
    """
    if not mapa.is_active():
        print("Error: El mapa no está activo")
        return False
        
    try:
        # Convertir el diccionario de perfiles a formato serializable
        perfiles_serializado = {k: list(v) for k, v in mapa.matriz_perfiles.items()}
        
        np.savez(filename,
                movimientos=mapa.matriz_movimientos,
                perfiles=perfiles_serializado,
                contador_pasos=mapa.contador_pasos,
                spawns=mapa.matriz_spawns)
        return True
    except Exception as e:
        print(f"Error al guardar el mapa: {e}")
        return False

def obtener_info_posicion(mapa, x, y):
    """
    Obtiene la información completa de una posición específica
    """
    if not mapa.is_active():
        print("Error: El mapa no está activo")
        return None

    if not (0 <= x < mapa.size and 0 <= y < mapa.size):
        return None
    
    return {
        'visitado': mapa.matriz_movimientos[y, x] > 0,
        'tipo_movimiento': mapa.matriz_movimientos[y, x],
        'flechas': mapa.matriz_flechas[y, x],
        'energia': mapa.matriz_energia[y, x],
        'orden_visita': mapa.matriz_secuencia[y, x]
    }

def obtener_estadisticas(mapa):
    """
    Obtiene estadísticas generales del mapa explorado
    """
    if not mapa.is_active():
        print("Error: El mapa no está activo")
        return None

    return {
        'casillas_visitadas': np.count_nonzero(mapa.matriz_movimientos > 0),
        'casillas_backtracking': np.count_nonzero(mapa.matriz_movimientos == 2),
        'total_pasos': mapa.contador_pasos,
        'energia_minima': np.min(mapa.matriz_energia[mapa.matriz_energia >= 0]),
        'energia_maxima': np.max(mapa.matriz_energia[mapa.matriz_energia >= 0])
    }

def exportar_a_txt(mapa, filename):
    """
    Exporta el mapa completo a un archivo de texto para visualización
    """
    if not mapa.is_active():
        print("Error: El mapa no está activo")
        return False

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Escribir encabezado con información
            f.write(f"Mapa {mapa.size}x{mapa.size} - Total pasos: {mapa.contador_pasos}\n")
            f.write("⬜ = No visitado | 🟩 = Visitado | 🟨 = Backtracking\n\n")
            
            # Escribir el mapa
            for y in range(mapa.size):
                for x in range(mapa.size):
                    # Dibujar solo el estado de la casilla sin números
                    if mapa.matriz_movimientos[y, x] == 0:
                        f.write('⬜')  # No visitado
                    elif mapa.matriz_movimientos[y, x] == 1:
                        f.write('🟩')  # Visitado normal
                    else:
                        f.write('🟨')  # Backtracking
                    
                    f.write(' ')  # Espacio entre casillas
                f.write('\n')
        return True
    except Exception as e:
        print(f"Error al exportar mapa: {e}")
        return False

def obtener_nombre_archivo_cueva(numero_cueva):
    """
    Genera el nombre del archivo para una cueva específica
    """
    # Obtener la ruta del directorio actual (Backend)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Crear el directorio 'maps' dentro de Backend si no existe
    maps_dir = os.path.join(current_dir, 'maps')
    if not os.path.exists(maps_dir):
        os.makedirs(maps_dir)
    
    # Retornar la ruta completa del archivo
    return os.path.join(maps_dir, f"cueva_{numero_cueva}.npz")

def cargar_mapa_cueva(numero_cueva, size=600):
    """
    Carga o crea el mapa compartido para una cueva específica
    """
    filename = obtener_nombre_archivo_cueva(numero_cueva)
    return abrir_documento(filename)

def actualizar_posicion(mapa, x, y, energia, arrows, is_backtracking=False):
    """
    Actualiza la posición en el mapa
    """
    if not mapa.is_active():
        print("Error: El mapa no está activo")
        return False

    if not (0 <= x < mapa.size and 0 <= y < mapa.size):
        print(f"Coordenadas fuera de rango: x={x}, y={y}")
        return False

    # Actualizar matriz de movimientos
    if mapa.matriz_movimientos[y, x] == 0:
        # Primera visita
        mapa.matriz_movimientos[y, x] = 1
        mapa.contador_pasos += 1
        mapa.matriz_secuencia[y, x] = mapa.contador_pasos
    elif is_backtracking:
        # Marcar como backtracking solo si no es primera visita
        mapa.matriz_movimientos[y, x] = 2
    
    # Actualizar energía si es menor que la actual o no hay energía registrada
    if mapa.matriz_energia[y, x] == -1 or energia < mapa.matriz_energia[y, x]:
        mapa.matriz_energia[y, x] = energia
    
    # Actualizar flechas disponibles
    mapa.matriz_flechas[y, x] = [
        'up' in arrows,
        'right' in arrows,
        'down' in arrows,
        'left' in arrows
    ]
    
    return True
