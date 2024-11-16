import matplotlib.pyplot as plt
import numpy as np
import os

def visualizar_mapa(ruta_archivo):
    """
    Visualiza el mapa desde un archivo .npz con el nuevo formato
    Args:
        ruta_archivo: Ruta al archivo .npz que contiene la matriz de movimientos y perfiles
    """
    try:
        # Cargar el archivo .npz
        datos = np.load(ruta_archivo, allow_pickle=True)
        matriz_movimientos = datos['movimientos']
        contador_pasos = datos['contador_pasos']
        matriz_spawns = datos['spawns']
        
        # Crear figura
        plt.figure(figsize=(15, 15))
        
        # Crear el mapa base (fondo blanco)
        plt.imshow(np.zeros_like(matriz_movimientos), cmap='binary', alpha=0.1)
        
        # Colorear según el tipo de visita
        mascara_normal = matriz_movimientos == 1
        mascara_backtrack = matriz_movimientos == 2
        mascara_spawns = matriz_spawns == 1
        
        # Visualizar las capas en orden específico para mejor visibilidad
        plt.imshow(mascara_spawns, cmap='Blues', alpha=0.3, label='Spawn')
        plt.imshow(mascara_normal, cmap='Greens', alpha=0.5, label='Visitado')
        plt.imshow(mascara_backtrack, cmap='YlOrRd', alpha=0.5, label='Backtracking')
        
        # Marcar los centros de spawn con puntos de color celeste
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
        
        # Marcar los centros de spawn con puntos de color celeste
        spawn_x, spawn_y = zip(*spawn_bases)
        plt.plot(spawn_x, spawn_y, 'o', color='skyblue', markersize=5, 
                label='Centro Spawn', alpha=0.7)
        
        # Configurar visualización
        plt.title(f'Mapa de Exploración\nTotal de pasos: {contador_pasos}\n'
                 f'Casillas visitadas: {np.count_nonzero(matriz_movimientos)}')
        plt.grid(True, alpha=0.2)
        
        # Agregar leyenda
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='blue', alpha=0.3, edgecolor='black', label='Área Spawn'),
            Patch(facecolor='green', alpha=0.5, edgecolor='black', label='Visitado'),
            Patch(facecolor='yellow', alpha=0.5, edgecolor='black', label='Backtracking'),
            plt.Line2D([0], [0], marker='o', color='skyblue', label='Centro Spawn',
                      markerfacecolor='skyblue', markersize=8, alpha=0.7)
        ]
        plt.legend(handles=legend_elements, loc='upper right')
        
        # Mostrar el mapa
        plt.show()
        
    except Exception as e:
        print(f"Error al visualizar el mapa: {e}")
        raise e

def analizar_cobertura_spawn(ruta_archivo):
    """
    Analiza la cobertura de exploración en las áreas de spawn
    """
    try:
        datos = np.load(ruta_archivo, allow_pickle=True)
        matriz_movimientos = datos['movimientos']
        matriz_spawns = datos['spawns']
        
        # Calcular estadísticas de cobertura
        casillas_spawn = np.count_nonzero(matriz_spawns)
        casillas_visitadas_spawn = np.count_nonzero(
            np.logical_and(matriz_spawns == 1, matriz_movimientos > 0)
        )
        porcentaje_cobertura = (casillas_visitadas_spawn / casillas_spawn) * 100 if casillas_spawn > 0 else 0
        
        print(f"\nAnálisis de Cobertura de Spawns:")
        print(f"Total casillas spawn: {casillas_spawn}")
        print(f"Casillas spawn visitadas: {casillas_visitadas_spawn}")
        print(f"Porcentaje de cobertura: {porcentaje_cobertura:.2f}%")
        
        return {
            'total_spawn': casillas_spawn,
            'visitadas_spawn': casillas_visitadas_spawn,
            'porcentaje': porcentaje_cobertura
        }
    except Exception as e:
        print(f"Error al analizar cobertura: {e}")
        return None

def ver_mapa_cueva(numero_cueva):
    """
    Visualiza el mapa de una cueva específica y muestra análisis
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_archivo = os.path.join(current_dir, f"cueva_{numero_cueva}.npz")
    
    if os.path.exists(ruta_archivo):
        print(f"Visualizando mapa de cueva {numero_cueva}...")
        visualizar_mapa(ruta_archivo)
        analizar_cobertura_spawn(ruta_archivo)
    else:
        print(f"No se encontró el mapa para la cueva {numero_cueva}")
        print(f"Ruta buscada: {ruta_archivo}")

def listar_mapas():
    """
    Lista todos los archivos de mapas disponibles
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    archivos = [f for f in os.listdir(current_dir) if f.startswith('cueva_') and f.endswith('.npz')]
    
    if not archivos:
        print("No se encontraron mapas de cuevas")
        return None
    
    print("\nMapas disponibles:")
    for archivo in sorted(archivos):
        numero_cueva = archivo.replace('cueva_', '').replace('.npz', '')
        print(f"Cueva {numero_cueva}")
    
    return archivos

if __name__ == "__main__":
    print("Visualizador de Mapas de Exploración")
    print("====================================")
    
    while True:
        print("\n1. Ver lista de mapas disponibles")
        print("2. Ver mapa específico")
        print("3. Analizar cobertura de spawn")
        print("4. Salir")
        
        try:
            opcion = input("\nSelecciona una opción (1-4): ")
            
            if opcion == "1":
                listar_mapas()
            
            elif opcion == "2":
                numero = input("Ingresa el número de cueva a visualizar: ")
                try:
                    ver_mapa_cueva(int(numero))
                except ValueError:
                    print("Por favor ingresa un número válido")
            
            elif opcion == "3":
                numero = input("Ingresa el número de cueva a analizar: ")
                try:
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    ruta_archivo = os.path.join(current_dir, f"cueva_{int(numero)}.npz")
                    if os.path.exists(ruta_archivo):
                        analizar_cobertura_spawn(ruta_archivo)
                    else:
                        print("Mapa no encontrado")
                except ValueError:
                    print("Por favor ingresa un número válido")
            
            elif opcion == "4":
                print("Saliendo...")
                break
            
            else:
                print("Opción no válida")
                
        except Exception as e:
            print(f"Error: {e}")