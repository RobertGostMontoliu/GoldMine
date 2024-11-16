import os
import time
import cv2
import numpy as np
import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from ui.WolfGame.Backend import WolfExcel as excel
from collections import deque
import random
import os.path
from ui.json_path import resource_path

# Definir la región inicial para la ventana del juego (ajustar estos valores)
game_region = (0, 0, 2560, 1440)  # Cambiar según la resolución de tu pantalla

# Obtener la ruta del directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))

# Definir la ruta de la carpeta media
media_dir = os.path.join(current_dir, 'media')

# Cargar las imágenes de flechas y popup
arrow_templates = {
    'up': cv2.imread(resource_path("ui\\media\\wolf_media\\arrow_up.png"), cv2.IMREAD_GRAYSCALE),
    'down': cv2.imread(resource_path("ui\\media\\wolf_media\\arrow_down.png"), cv2.IMREAD_GRAYSCALE),
    'left': cv2.imread(resource_path("ui\\media\\wolf_media\\arrow_left.png"), cv2.IMREAD_GRAYSCALE),
    'right': cv2.imread(resource_path("ui\\media\\wolf_media\\arrow_right.png"), cv2.IMREAD_GRAYSCALE)
}
dig_e_template = cv2.imread(resource_path("ui\\media\\wolf_media\\dig_e.png"), cv2.IMREAD_GRAYSCALE)

def move(driver, direction):
    if direction == 'up':
        ActionChains(driver).send_keys('\ue013').perform()  # ARROW_UP
    elif direction == 'down':
        ActionChains(driver).send_keys('\ue015').perform()  # ARROW_DOWN
    elif direction == 'left':
        ActionChains(driver).send_keys('\ue012').perform()  # ARROW_LEFT
    elif direction == 'right':
        ActionChains(driver).send_keys('\ue014').perform()  # ARROW_RIGHT
    
    print(f"Moviendo: {direction}")
    time.sleep(0.5)  # Reducido de 1.5 a 0.5 segundos

def capture_screenshot(region):
    """
    Captura y retorna la pantalla en escala de grises
    """
    screenshot = pyautogui.screenshot(region=region)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    return screenshot

def detect_arrows(region):
    """
    Detecta las flechas disponibles con verificación múltiple y mejor umbral
    """
    arrows = {}
    screenshot = capture_screenshot(region)
    
    # Aplicar preprocesamiento de imagen
    _, binary = cv2.threshold(screenshot, 180, 255, cv2.THRESH_BINARY)
    denoised = cv2.fastNlMeansDenoising(binary)
    
    # Verificación para cada dirección
    for direction, template in arrow_templates.items():
        result = cv2.matchTemplate(denoised, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Umbral de detección ajustado
        if max_val >= 0.8:  # Aumentamos el umbral para mayor precisión
            arrows[direction] = max_loc
            print(f"Flecha {direction} detectada con confianza: {max_val:.3f}")
    
    # Verificación de coherencia
    if arrows:
        print(f"Flechas detectadas: {list(arrows.keys())}")
    else:
        print("No se detectaron flechas - Posible pared")
    
    return arrows

def detect_dig_e_popup(driver):
    """
    Detecta si hay un popup de DIG(E) visible
    """
    try:
        # Intentar diferentes formas de encontrar el popup
        selectors = [
            "//div[contains(text(), 'DIG(E)')]",
            "//div[contains(text(), 'DIG')]",
            "//*[contains(text(), 'DIG(E)')]",
            "//div[contains(@class, 'dig-popup')]"  # Agregar si existe una clase específica
        ]
        
        for selector in selectors:
            try:
                element = driver.find_element(By.XPATH, selector)
                if element.is_displayed():
                    print("DIG(E) popup detectado")
                    return True
            except:
                continue
        return False
    except Exception as e:
        print(f"Error en detección de DIG(E): {e}")
        return False

def handle_loot(driver):
    """
    Maneja el proceso completo de recolección de loot
    """
    if not detect_dig_e_popup(driver):
        return False

    print("Iniciando recolección de loot...")
    
    try:
        # Paso 1: Presionar E para DIG
        ActionChains(driver).send_keys('e').perform()
        print("Tecla E presionada para DIG")
        time.sleep(2)  # Esperar a que aparezca el popup de OK
        
        # Esperar y verificar el botón OK
        max_attempts = 10  # Aumentamos el número de intentos
        for attempt in range(max_attempts):
            try:
                # Cargar la imagen del botón OK
                ok_template = cv2.imread(resource_path("ui\\media\\wolf_media\\ok_e.png"), cv2.IMREAD_GRAYSCALE)
                if ok_template is None:
                    print("Error: No se pudo cargar la imagen ok_e.png")
                    return False
                
                screenshot = capture_screenshot(game_region)
                
                # Aplicar preprocesamiento similar al de detect_arrows
                _, binary = cv2.threshold(screenshot, 180, 255, cv2.THRESH_BINARY)
                denoised = cv2.fastNlMeansDenoising(binary)
                
                # Buscar el botón OK en la pantalla
                result = cv2.matchTemplate(denoised, ok_template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                print(f"Intento {attempt + 1}: Confianza de detección OK: {max_val:.3f}")
                
                # Si se encuentra el botón OK con suficiente confianza
                if max_val >= 0.7:  # Reducimos ligeramente el umbral
                    print("Botón OK detectado, presionando E...")
                    time.sleep(1)  # Pequeña pausa antes de presionar E
                    ActionChains(driver).send_keys('e').perform()
                    print("Tecla E presionada para OK")
                    time.sleep(1.5)  # Esperar a que se complete la acción
                    
                    # Verificar que el popup ya no está visible
                    if not detect_dig_e_popup(driver):
                        print("Loot completado exitosamente")
                        return True
                    else:
                        print("El popup DIG(E) sigue visible después de presionar OK")
                
                time.sleep(0.5)  # Reducimos el tiempo entre intentos
            except Exception as e:
                print(f"Error en intento {attempt + 1}: {e}")
                # Guardar la captura de pantalla para diagnóstico
                cv2.imwrite(f'debug_ok_detection_{attempt}.png', screenshot)
                time.sleep(0.5)
        
        print("No se pudo completar el proceso de loot después de varios intentos")
        return False
        
    except Exception as e:
        print(f"Error en manejo de loot: {e}")
        return False

def extract_position(driver, retries=5, delay=5):
    for attempt in range(retries):
        try:
            # Lista de XPaths para la posición
            position_xpaths = [
                '//*[@id="root"]/div/div[2]/div[1]/div/div/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]/div',
                '//*[@id="root"]/div/div[2]/div/div/div/div[5]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[3]'
            ]
            
            # Intentar cada XPath
            for xpath in position_xpaths:
                try:
                    position_element = driver.find_element(By.XPATH, xpath)
                    if position_element.is_displayed():
                        position_text = position_element.text
                        print(f"Texto de posición extraído: {position_text}")
                        
                        # Extraer las coordenadas x e y
                        x_text = position_text.split('x:')[1].split(',')[0].strip()
                        y_text = position_text.split('y:')[1].strip()
                        
                        x = int(x_text)
                        y = int(y_text)
                        
                        print(f"Posición extraída: x={x}, y={y}")
                        return (x, y)
                except:
                    continue
            
            # Si ningún XPath funcionó, esperar y reintentar
            print(f"No se encontró el elemento de posición (intento {attempt + 1}/{retries})")
            time.sleep(delay)
            
        except Exception as e:
            print(f"Fallo al extraer la posición (intento {attempt + 1}/{retries}): {e}")
            time.sleep(delay)
    
    print("No se pudo extraer la posición después de varios intentos.")
    return None

def extract_energy(driver, retries=5, delay=5):
    for attempt in range(retries):
        try:
            # Lista de XPaths para la energía
            energy_xpaths = [
                '//*[@id="root"]/div/div[2]/div[1]/div/div/div[2]/div[1]/div[2]/div[2]/div[2]/div[1]/div[2]/div',
                '//*[@id="root"]/div/div[2]/div/div/div/div[5]/div[1]/div[1]/div[1]/div[2]/div[2]/div[2]/div[1]/div[2]/div'
            ]
            
            # Intentar cada XPath
            for xpath in energy_xpaths:
                try:
                    energy_element = driver.find_element(By.XPATH, xpath)
                    if energy_element.is_displayed():
                        energy_text = energy_element.text
                        print(f"Texto de energía extraído: {energy_text}")
                        current_energy = int(energy_text.split('/')[0].strip())
                        print(f"Energía actual: {current_energy}")
                        return current_energy
                except:
                    continue
            
            # Si ningún XPath funcionó, esperar y reintentar
            print(f"No se encontró el elemento de energía (intento {attempt + 1}/{retries})")
            time.sleep(delay)
            
        except Exception as e:
            print(f"Fallo al extraer la energía (intento {attempt + 1}/{retries}): {e}")
            time.sleep(delay)
    
    return 0

def extract_cave_number(driver):
    try:
        # Lista de XPaths para el número de cueva
        cave_xpaths = [
            '//*[@id="root"]/div/div[2]/div[1]/div/div/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[2]',
            '//*[@id="root"]/div/div[2]/div/div/div/div[5]/div[1]/div[1]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]'
        ]
        
        # Intentar cada XPath
        for xpath in cave_xpaths:
            try:
                cave_element = driver.find_element(By.XPATH, xpath)
                if cave_element.is_displayed():
                    cave_text = cave_element.text
                    print(f"Texto de cueva extraído: {cave_text}")
                    
                    # Intentar extraer el número de la cueva usando diferentes métodos
                    if 'Cave #' in cave_text:
                        cave_number = cave_text.split('Cave #')[1].strip()
                    elif '#' in cave_text:
                        cave_number = cave_text.split('#')[1].strip()
                    else:
                        cave_number = ''.join(filter(str.isdigit, cave_text))
                    
                    if cave_number:
                        print(f"Número de cueva extraído: {cave_number}")
                        return cave_number
            except:
                continue
        
        print("No se pudo encontrar el número de cueva en ninguna ubicación")
        return None
        
    except Exception as e:
        print(f"Error al extraer el número de la cueva: {e}")
        return None

def update_position(position, direction):
    x, y = position
    if direction == 'up':
        return (x, y - 1)
    elif direction == 'down':
        return (x, y + 1)
    elif direction == 'left':
        return (x - 1, y)
    elif direction == 'right':
        return (x + 1, y)
    return position

def get_direction_priority(current_position, size=600):
    """
    Determina la prioridad de dirección basada en la posición actual y los bordes
    """
    x, y = current_position
    distances = {
        'right': size - x,  # Distancia al borde derecho
        'down': size - y,   # Distancia al borde inferior
        'left': x,          # Distancia al borde izquierdo
        'up': y             # Distancia al borde superior
    }
    
    # Ordenar direcciones por distancia al borde más cercano
    return sorted(distances.items(), key=lambda x: x[1])

def is_spawn_area(position, mapa):
    """
    Verifica si una posición está en un área de spawn
    """
    x, y = position
    return mapa.matriz_spawns[y, x] == 1

def find_unexplored_path(current_position, visited, arrows, mapa, size=600):
    """
    Encuentra el camino más corto hacia una casilla no explorada evitando spawns
    """
    queue = deque([(current_position, [])])
    explored = {current_position}
    
    while queue:
        position, path = queue.popleft()
        x, y = position
        
        for direction in arrows.keys():
            new_x, new_y = update_position((x, y), direction)
            new_pos = (new_x, new_y)
            
            # Verificar límites del mapa
            if not (0 <= new_x < size and 0 <= new_y < size):
                continue
                
            # Evitar áreas de spawn excepto para salir de ellas
            if is_spawn_area(new_pos, mapa) and not is_spawn_area(current_position, mapa):
                continue
                
            if new_pos in explored:
                continue
                
            # Si encontramos una casilla no visitada y accesible
            if mapa.matriz_movimientos[new_y, new_x] == 0:
                can_reach = True
                current = current_position
                for step in path + [direction]:
                    next_pos = update_position(current, step)
                    if next_pos not in visited:
                        can_reach = False
                        break
                    current = next_pos
                
                if can_reach:
                    return path + [direction]
            
            if new_pos in visited:
                explored.add(new_pos)
                queue.append((new_pos, path + [direction]))
    
    return None

def choose_next_move(current_position, arrows, visited, stack, mapa, size=600):
    """
    Elige el siguiente movimiento evitando spawns
    """
    print(f"\nEvaluando movimientos desde posición {current_position}")
    print(f"Flechas disponibles: {list(arrows.keys())}")
    
    # PRIORIDAD 0: Si estamos en un spawn, salir de él
    if is_spawn_area(current_position, mapa):
        print("Detectada posición en spawn, buscando salida")
        for direction in arrows.keys():
            new_position = update_position(current_position, direction)
            new_x, new_y = new_position
            if (0 <= new_x < size and 0 <= new_y < size and 
                not is_spawn_area(new_position, mapa)):
                print(f"Encontrada salida del spawn: {direction}")
                return direction, new_position, False

    # Resto de prioridades...
    for direction in arrows.keys():
        new_position = update_position(current_position, direction)
        new_x, new_y = new_position
        
        # Evitar entrar a spawns
        if (0 <= new_x < size and 0 <= new_y < size and 
            not is_spawn_area(new_position, mapa) and
            mapa.matriz_movimientos[new_y, new_x] == 0):
            print("Encontrada casilla adyacente no visitada fuera de spawn")
            return direction, new_position, False

    # PRIORIDAD 1: Buscar casillas adyacentes no visitadas
    for direction in arrows.keys():
        new_position = update_position(current_position, direction)
        new_x, new_y = new_position
        if (0 <= new_x < size and 0 <= new_y < size and 
            mapa.matriz_movimientos[new_y, new_x] == 0):
            print("Encontrada casilla adyacente no visitada")
            return direction, new_position, False

    # PRIORIDAD 2: Si estamos en backtracking, continuar hasta encontrar una salida
    if any(mapa.matriz_movimientos[y, x] == 2 for x, y in [update_position(current_position, d) for d in arrows.keys()]):
        print("Continuando backtracking hasta encontrar salida")
        # Elegir la dirección que nos lleve a la casilla menos visitada
        best_direction = None
        min_visits = float('inf')
        
        for direction in arrows.keys():
            new_position = update_position(current_position, direction)
            new_x, new_y = new_position
            if (0 <= new_x < size and 0 <= new_y < size):
                visits = mapa.matriz_movimientos[new_y, new_x]
                if visits < min_visits:
                    min_visits = visits
                    best_direction = direction
        
        if best_direction:
            new_position = update_position(current_position, best_direction)
            return best_direction, new_position, True

    # PRIORIDAD 3: Buscar camino a casillas no exploradas
    path_to_unexplored = find_unexplored_path(current_position, visited, arrows, mapa)
    if path_to_unexplored:
        next_direction = path_to_unexplored[0]
        new_position = update_position(current_position, next_direction)
        print(f"Encontrado camino hacia área no explorada: {path_to_unexplored}")
        return next_direction, new_position, False

    # PRIORIDAD 4: Iniciar backtracking usando el stack
    if stack:
        while stack and stack[-1] == current_position:
            stack.pop()
            
        if stack:
            target_position = stack[-1]
            print(f"Iniciando backtracking hacia: {target_position}")
            
            for direction in arrows.keys():
                new_position = update_position(current_position, direction)
                if new_position == target_position:
                    return direction, new_position, True

    print("No se encontraron movimientos válidos")
    return None, None, False

def check_inventory(driver):
    """
    Verifica el contenido del inventario y retorna la información de los objetos
    """
    inventory_slots = [
        '//*[@id="root"]/div/div[2]/div/div/div/div[5]/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/div/div',
        '//*[@id="root"]/div/div[2]/div/div/div/div[5]/div[1]/div[1]/div[2]/div/div[2]/div/div[3]/div/div/div'
    ]
    
    inventory = []
    
    for slot in inventory_slots:
        try:
            item_element = driver.find_element(By.XPATH, slot)
            if item_element.is_displayed():
                item_name = item_element.text.strip()
                if item_name:
                    inventory.append(item_name)
                    print(f"Objeto encontrado en inventario: {item_name}")
        except:
            continue
    
    return inventory

def analyze_inventory(inventory, current_energy):
    """
    Analiza el inventario y determina qué objetos se deberían usar
    """
    detectors = ['DETECTOR', 'HEADLAMP', 'GOGGLES', 'PICKAXE']
    food_items = ['MILK GLASS', 'CARROT', 'DEEZ NUTS']
    explosives = ['BOMB', 'DYNAMITE']
    
    recommended_actions = []
    
    for slot, item in enumerate(inventory, 1):
        if item in detectors:
            recommended_actions.append({
                'item': item,
                'slot': slot,
                'action': 'detect',
                'priority': 1
            })
        elif item in food_items and current_energy <= 20:
            recommended_actions.append({
                'item': item,
                'slot': slot,
                'action': 'consume',
                'priority': 2
            })
        elif current_energy >= 50 and item in explosives:
            recommended_actions.append({
                'item': item,
                'slot': slot,
                'action': 'use',
                'priority': 3
            })
    
    return sorted(recommended_actions, key=lambda x: x['priority'])

def explore(driver, initial_energy, profile_id):
    cave_number = extract_cave_number(driver)
    if cave_number is None:
        return "restart"
    
    # Cargar o crear el mapa
    mapa = excel.cargar_mapa_cueva(cave_number)
    
    visited = set()
    stack = deque()
    current_position = extract_position(driver)
    if current_position is None:
        return "restart"
    
    # Inicializar exploración
    visited.add(current_position)
    stack.append(current_position)
    
    # Registrar posición inicial
    mapa.agregar_visita(current_position[0], current_position[1], profile_id)
    
    while extract_energy(driver) > 0:
        current_position = extract_position(driver)
        if current_position is None:
            return "restart"
        
        arrows = detect_arrows(game_region)
        if not arrows:
            time.sleep(0.3)  # Reducido de 1 a 0.3 segundos
            continue
        
        direction, new_position, is_backtracking = choose_next_move(
            current_position, arrows, visited, stack, mapa)
        
        if direction and new_position:
            move(driver, direction)
            
            # Esperar solo lo necesario para que el juego actualice la posición
            time.sleep(0.3)  # Reducido de 1.5 a 0.3 segundos
            
            updated_position = extract_position(driver)
            if updated_position == new_position:
                # Registrar el movimiento en el mapa
                mapa.agregar_visita(
                    updated_position[0],
                    updated_position[1],
                    profile_id,
                    is_backtracking
                )
                
                # Actualizar exploración inmediatamente
                if not is_backtracking:
                    visited.add(updated_position)
                    stack.append(updated_position)
                else:
                    if stack and stack[-1] == current_position:
                        stack.pop()
                
                # Guardar mapa de forma asíncrona o menos frecuente
                if len(visited) % 5 == 0:  # Guardar cada 5 movimientos
                    excel.guardar_mapa(excel.obtener_nombre_archivo_cueva(cave_number), mapa)
                    excel.exportar_a_txt(
                        mapa,
                        os.path.join(os.path.dirname(excel.obtener_nombre_archivo_cueva(cave_number)),
                                    f"cueva_{cave_number}_mapa.txt")
                    )
            else:
                return "restart"
        else:
            if len(stack) <= 1:
                return "complete"
            if stack:
                stack.pop()
            continue

        # Manejar loot si está disponible
        if detect_dig_e_popup(driver):
            handle_loot(driver)
            time.sleep(1)

    return "complete"

def backtrack_to_position(driver, current_position, backtrack_position):
    while current_position != backtrack_position:
        for direction in ['up', 'down', 'left', 'right']:
            new_position = update_position(current_position, direction)
            if new_position == backtrack_position:
                move(driver, direction)
                time.sleep(2)
                current_position = extract_position(driver)
                break
       
def use_inventory_item(driver, slot_number):
    """
    Usa un item específico del inventario
    slot_number: 1 o 2 para indicar qué slot del inventario usar
    """
    try:
        # XPaths para los slots y el botón de confirmar
        slot_xpaths = {
            1: '//*[@id="root"]/div/div[2]/div/div/div/div[5]/div[1]/div[1]/div[2]/div/div[2]/div/div[2]',
            2: '//*[@id="root"]/div/div[2]/div/div/div/div[5]/div[1]/div[1]/div[2]/div/div[2]/div/div[3]'
        }
        confirm_xpath = '//*[@id="root"]/div/div[2]/div/div/div/div[5]/div[1]/div[1]/div[2]/div/div[2]/div/div[4]/div[2]'
        
        # Seleccionar el item
        slot_element = driver.find_element(By.XPATH, slot_xpaths[slot_number])
        if not slot_element.is_displayed():
            print(f"Slot {slot_number} no está visible")
            return False
            
        slot_element.click()
        print(f"Slot {slot_number} seleccionado")
        time.sleep(1)
        
        # Confirmar uso del item
        confirm_element = driver.find_element(By.XPATH, confirm_xpath)
        if not confirm_element.is_displayed():
            print("Botón de confirmar no está visible")
            return False
            
        confirm_element.click()
        print("Uso de item confirmado")
        time.sleep(2)
        
        # Esperar y manejar el botón OK
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                ok_template = cv2.imread(resource_path("ui\\media\\wolf_media\\ok_e.png"), cv2.IMREAD_GRAYSCALE)
                if ok_template is None:
                    print("Error: No se pudo cargar la imagen ok_e.png")
                    return False
                
                screenshot = capture_screenshot(game_region)
                _, binary = cv2.threshold(screenshot, 180, 255, cv2.THRESH_BINARY)
                denoised = cv2.fastNlMeansDenoising(binary)
                
                result = cv2.matchTemplate(denoised, ok_template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                if max_val >= 0.7:
                    print("Botón OK detectado, presionando E...")
                    time.sleep(1)
                    ActionChains(driver).send_keys('e').perform()
                    print("Item usado exitosamente")
                    return True
                
                time.sleep(0.5)
            except Exception as e:
                print(f"Error en intento {attempt + 1}: {e}")
                time.sleep(0.5)
        
        print("No se pudo completar el uso del item")
        return False
        
    except Exception as e:
        print(f"Error al usar el item: {e}")
        return False
