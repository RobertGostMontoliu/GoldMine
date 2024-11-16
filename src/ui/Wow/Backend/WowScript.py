from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException, WebDriverException, ElementClickInterceptedException, NoSuchElementException
import time
import argparse
import cv2
import numpy as np
import math
from PIL import Image
import io
from ui.api_manager import GPMManager, ADSPowerManager, ChromeManager
from ui.components import ConfigManager
from selenium.webdriver.common.action_chains import ActionChains


def Wow(driver=None, profile_id=None, **kwargs):
    max_retries = 2
    gpm_manager = GPMManager()  # Instancia de GPMManager

    for attempt in range(max_retries):
        if driver is None:
            print("No se pudo iniciar el navegador.")
            return
        try:
            """
        #Aqui va la funcion de la linea 46
            """
            if farmeo_principal(driver, Wow): 
                print("Farmeo exitoso. Cerrando el perfil.")
                break  # Si el farmeo fue exitoso, salimos del bucle
        except Exception as e:
            print(f"Ocurrió un error durante el proceso: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Reintentando... Intento {attempt + 2} de {max_retries}")
            else:
                print("Se alcanzó el número máximo de intentos.")
        finally:
            print("Finalizando el proceso.")
            if profile_id:
                # Cerrar el perfil desde la API
                gpm_manager.close_browser(profile_id)

def farmeo_principal(driver, test):
    try:
        # Paso 1: Navegar a la página web y esperar que cargue correctamente
        driver.get("https://web.telegram.org/k/#?tgaddr=tg%3A%2F%2Fresolve%3Fdomain%3Dwow3_bot%26appname%3Dcoinflip%26startapp%3D1418302636")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("Página cargada correctamente")

        # Paso 2: Click en launch (en la ventana principal)
        launch_button_selector = ".popup-button:nth-child(1) > .c-ripple"
        try:
            launch_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, launch_button_selector))
            )
            driver.execute_script("arguments[0].click();", launch_button)
            print("Se hizo clic en el botón de lanzamiento (Launch)")
        except TimeoutException:
            print("No se pudo encontrar el botón de lanzamiento (Launch)")
            return False

        # Esperar a que el iframe esté disponible y cambiar a él
        try:
            iframe = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe"))
            )
            driver.switch_to.frame(iframe)
            print("Cambiado al iframe de Wow")
        except TimeoutException:
            print("No se pudo encontrar el iframe")
            return False

        # Esperar a que el contenido del iframe cargue
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//body"))
        )

        # Loop para buscar y hacer clic en los botones hasta que se detecte el botón de quest
        buttons = [
            ("WOW lets go", "/html/body/div[1]/div[1]/div[2]/button"),
            ("Continue 1", "/html/body/div[1]/div[1]/div[2]/button"),
            ("Continue 2", "/html/body/div[1]/div[1]/div[2]/button"),
            ("Continue 3", "/html/body/div[1]/div[1]/div[2]/button"),
            ("Daily check in", "//*[@id='check_in']/div[4]/button"),
            ("Cancelar", "//*[@id='check_in']/div[1]/button")
        ]

        quest_button_xpath = "/html/body/div[1]/div[1]/div[2]/nav/a[2]"
        max_attempts = 20
        attempts = 0
        daily_claim_clicked = False

        while attempts < max_attempts:
            try:
                # Verificar si el botón de quest está presente
                if driver.find_elements(By.XPATH, quest_button_xpath):
                    print("Botón de quest detectado. Continuando con los pasos de quest.")
                    break

                for button_name, locator in buttons:
                    try:
                        button = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, locator))
                        )
                        
                        if button_name == "Daily check in":
                            driver.execute_script("arguments[0].click();", button)
                            print(f"Se hizo clic en el botón: {button_name}")
                            daily_claim_clicked = True
                            time.sleep(1)  # Esperar un segundo después del daily claim
                        elif button_name == "Cancelar" and daily_claim_clicked:
                            driver.execute_script("arguments[0].click();", button)
                            print(f"Se hizo clic en el botón: {button_name}")
                            daily_claim_clicked = False  # Reiniciar el flag
                            time.sleep(1)  # Esperar un segundo después de cancelar
                            break  # Salir del bucle interno después de cancelar
                        elif not daily_claim_clicked:
                            driver.execute_script("arguments[0].click();", button)
                            print(f"Se hizo clic en el botón: {button_name}")
                            time.sleep(1)  # Esperar un segundo después de cada clic
                            break  # Salir del bucle interno si se hizo clic en un botón
                    except TimeoutException:
                        continue
            except Exception as e:
                print(f"Error durante el loop de botones: {str(e)}")

            attempts += 1
            time.sleep(1)  # Esperar un segundo antes de la siguiente iteración

        if attempts >= max_attempts:
            print("No se pudo detectar el botón de quest después de múltiples intentos.")
            return False

        # Aquí puedes continuar con los pasos de quest
        # Por ejemplo:
        quest_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, quest_button_xpath))
        )
        driver.execute_script("arguments[0].click();", quest_button)
        print("Se hizo clic en el botón de quest")

        # Paso 10: Click en Visit Wow3
        visit_wow3_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='wow3-game']/div/div[5]/div/div[2]/button"))
        )
        driver.execute_script("arguments[0].click();", visit_wow3_button)
        print("Visitando Wow3")

        # Paso 11: Cerrar ventana adicional
        driver.switch_to.default_content()  # Volver al contexto principal
        main_window = driver.current_window_handle
        for handle in driver.window_handles:
            if handle != main_window:
                driver.switch_to.window(handle)
                driver.close()
        driver.switch_to.window(main_window)
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe")))  # Volver al iframe
        print("Ventana adicional cerrada")

        # Paso 12: Click en One time task
        one_time_task_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='wow3-game']/div/div[4]/button[2]/div/span"))
        )
        driver.execute_script("arguments[0].click();", one_time_task_button)
        print("One time task seleccionado")

        # Paso 13: Revisar y hacer click en todos los Div class de One Time Tasks
        one_time_tasks_completed = False
        while not one_time_tasks_completed:
            try:
                # Verificar si el navegador aún está abierto
                try:
                    driver.current_url
                except (WebDriverException, NoSuchWindowException):
                    print("El navegador ha sido cerrado. Terminando el proceso.")
                    return False

                # Intentar hacer clic en el primer div de One Time Tasks
                div_xpath = "//*[@id='wow3-game']/div/div[5]/div/div[1]"
                div_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, div_xpath))
                )

                # Agregar un delay de 2 segundos antes de verificar si está completado
                time.sleep(2)

                # Verificar si la imagen está presente (indicando que la tarea está completada)
                img_xpath = "//*[@id='wow3-game']/div/div[5]/div/div[1]/button/div[2]/img"
                img_present = len(driver.find_elements(By.XPATH, img_xpath)) > 0

                if img_present:
                    print("Todas las One Time Tasks han sido completadas")
                    one_time_tasks_completed = True
                    break

                # Si la imagen no está presente, hacer clic en el div
                driver.execute_script("arguments[0].click();", div_element)
                print("Clic en el div de One Time Task")

                # Esperar a que se abra la nueva ventana
                try:
                    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
                    print("Nueva ventana detectada")
                    
                    # Cambiar al contexto de la nueva ventana
                    new_window = driver.window_handles[-1]
                    driver.switch_to.window(new_window)
                    
                    # Esperar a que se cargue la nueva página
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    print("Nueva página cargada")
                    
                    # Cerrar la ventana actual
                    driver.close()
                    print("Ventana cerrada")
                    
                    # Volver a la ventana original
                    driver.switch_to.window(driver.window_handles[0])
                    
                    # Volver al iframe de Wow
                    WebDriverWait(driver, 20).until(
                        EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe"))
                    )
                    print("Volviendo al iframe de Wow")
                    
                except TimeoutException:
                    print("No se abrió una nueva ventana")
                except (WebDriverException, NoSuchWindowException):
                    print("El navegador ha sido cerrado. Terminando el proceso.")
                    return False

                # Esperar un momento antes de continuar con el siguiente intento
                time.sleep(3)
                
            except Exception as e:
                print(f"Error al procesar One Time Task: {str(e)}")
                if "no such window" in str(e).lower():
                    print("El navegador ha sido cerrado. Terminando el proceso.")
                    return False
                time.sleep(3)  # Esperar un poco antes de intentar de nuevo

        # Una vez completadas las One Time Tasks, proceder con las Partner Tasks
        if partner_tasks(driver):
            print("Partner Tasks completadas con éxito")
        else:
            print("Hubo un problema al completar las Partner Tasks")

        return True  # Indica que el farmeo fue exitoso
    except Exception as e:
        print(f"Error durante el farmeo: {str(e)}")
        return False
    finally:
        # Asegurarse de volver al contexto principal del documento
        try:
            driver.switch_to.default_content()
        except:
            pass  # Ignorar errores al intentar volver al contexto principal


def partner_tasks(driver):
    try:
        # 1. Click en la categoría Partner Tasks
        partner_tasks_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='wow3-game']/div/div[4]/button[3]"))
        )
        driver.execute_script("arguments[0].click();", partner_tasks_button)
        print("Categoría Partner Tasks seleccionada")

        partners_completed = 0
        max_partners = 5

        while partners_completed < max_partners:
            try:
                # Click en el primer div de Partner Tasks
                div_xpath = "//*[@id='wow3-game']/div/div[5]/div/div[1]"
                div_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, div_xpath))
                )
                driver.execute_script("arguments[0].click();", div_element)
                print(f"Entrando al partner {partners_completed + 1}")

                # Verificar cuántas tareas hay disponibles
                tasks_available = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='wow3-game']/div/div[2]/span[1]"))
                )
                total_tasks = int(tasks_available.text.split('/')[1])
                completed_tasks = 0

                while completed_tasks < total_tasks:
                    try:
                        # Intentar hacer clic en el botón de iniciar tarea
                        start_task_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//*[@id='wow3-game']/div/button[1]"))
                        )
                        driver.execute_script("arguments[0].click();", start_task_button)
                        print(f"Iniciando tarea {completed_tasks + 1} de {total_tasks}")

                        # Esperar a que se abra una nueva ventana
                        try:
                            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
                            new_window = driver.window_handles[-1]
                            driver.switch_to.window(new_window)
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                            WebDriverWait(driver, 20).until(
                                EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe"))
                            )
                            print("Nueva ventana cerrada")
                        except TimeoutException:
                            print("No se abrió una nueva ventana")

                        # Verificar si aparece el botón de cancelar
                        try:
                            cancel_button = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, "/html/body/div[8]/div/div[2]/button[2]/div"))
                            )
                            driver.execute_script("arguments[0].click();", cancel_button)
                            print("Tarea cancelada")
                        except TimeoutException:
                            pass

                        # Actualizar el contador de tareas completadas
                        tasks_available = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//*[@id='wow3-game']/div/div[2]/span[1]"))
                        )
                        completed_tasks = int(tasks_available.text.split('/')[0])

                    except Exception as e:
                        print(f"Error al realizar la tarea: {str(e)}")
                        break

                # Volver atrás una vez completadas todas las tareas
                back_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div[7]/div/div[1]/button[1]"))
                )
                driver.execute_script("arguments[0].click();", back_button)
                print(f"Partner {partners_completed + 1} completado")

                partners_completed += 1

            except Exception as e:
                print(f"Error al procesar el partner {partners_completed + 1}: {str(e)}")
                partners_completed += 1

        print("Todas las Partner Tasks completadas")
        return True

    except Exception as e:
        print(f"Error durante las Partner Tasks: {str(e)}")
        return False

# --- MultiThread Integration ---

def start_multithread_farming(profiles, num_concurrent, window_settings):
    """
    Inicia el farmeo de múltiples perfiles usando la infraestructura de multihilo.

    :param profiles: Lista de IDs de perfiles para farmear.
    :param num_concurrent: Número de perfiles concurrentes.
    :param window_settings: Configuraciones de ventana.
    :return: None
    """
    iniciar_farmeo_multiple(profiles, num_concurrent, "wow", window_settings)   


# --- MAIN ---
def parse_arguments():
    parser = argparse.ArgumentParser(description="Ejecutar Wow") 
    parser.add_argument("--browser", type=str, required=True, help="Tipo de navegador (gpm, ads, chrome)")
    parser.add_argument("--profile_id", type=str, help="ID del perfil para GPM")
    parser.add_argument("--profile_name", type=str, help="Nombre del perfil para Chrome")
    parser.add_argument("--win_scale", type=float, help="Escala de la ventana")
    parser.add_argument("--win_pos", type=str, help="Posición de la ventana (x,y)")
    parser.add_argument("--win_size", type=str, help="Tamaño de la ventana (ancho,alto)")
    return parser.parse_args()


if __name__ == "__main__":
    # Importar desde MultiThreadFarming.py
    from ui.MultiThreadFarming import iniciar_farmeo_multiple
    args = parse_arguments()

    kwargs = {
        "win_scale": args.win_scale,
        "win_pos": args.win_pos,
        "win_size": args.win_size
    }

    profiles = [args.profile_id]  # Aquí deberías pasar una lista de IDs de perfiles si son múltiples
    num_concurrent = 1  # Cambiar a más si deseas farmeo concurrente

    start_multithread_farming(profiles, num_concurrent, kwargs)















