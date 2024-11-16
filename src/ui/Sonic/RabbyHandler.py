from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException, StaleElementReferenceException, WebDriverException
import time

class RabbyHandler:
    def __init__(self, driver):
        self.driver = driver
        self.main_window = driver.current_window_handle

    def verificar_y_manejar_rabby(self):
        try:
            ventana_rabby = self.buscar_ventana_rabby()
            if ventana_rabby:
                self.driver.switch_to.window(ventana_rabby)
                self.manejar_ventana_rabby()
                self.driver.switch_to.window(self.main_window)
                return True
            return False
        except WebDriverException:
            print("El navegador se ha cerrado.")
            return False

    def buscar_ventana_rabby(self):
        try:
            for handle in self.driver.window_handles:
                if handle != self.main_window:
                    self.driver.switch_to.window(handle)
                    if "Rabby" in self.driver.title:
                        return handle
            self.driver.switch_to.window(self.main_window)
        except WebDriverException:
            print("El navegador se ha cerrado.")
        return None

    def manejar_ventana_rabby(self):
        if self.es_ventana_desbloqueo():
            self.manejar_desbloqueo()
        elif self.es_ventana_firma_contrato():
            self.manejar_firma_contrato()
        elif self.es_ventana_confirmacion():
            self.manejar_confirmacion()
        elif self.es_ventana_conexion():
            self.manejar_conexion()
        elif self.es_ventana_cambio_red():
            self.manejar_cambio_red()
        else:
            print("Ventana de Rabby no reconocida")

    def esperar_y_hacer_clic(self, elemento):
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", elemento)

    def esperar_y_enviar_teclas(self, elemento, teclas):
        time.sleep(0.5)
        elemento.clear()
        elemento.send_keys(teclas)

    def es_ventana_desbloqueo(self):
        try:
            return WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
            )
        except TimeoutException:
            return False

    def es_ventana_firma_contrato(self):
        try:
            return WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Firmar') or contains(text(), 'Sign')]"))
            )
        except TimeoutException:
            return False

    def es_ventana_confirmacion(self):
        try:
            return WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Confirmar') or contains(text(), 'Confirm')]"))
            )
        except TimeoutException:
            return False

    def es_ventana_conexion(self):
        try:
            return WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Conectar') or contains(text(), 'Connect')]"))
            )
        except TimeoutException:
            return False

    def es_ventana_cambio_red(self):
        try:
            return WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Cambiar red') or contains(text(), 'Switch network')]"))
            )
        except TimeoutException:
            return False

    def manejar_desbloqueo(self):
        try:
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
            )
            self.esperar_y_enviar_teclas(password_input, "Wells081995!")

            unlock_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='root']/div/form/div[2]/div/div/div/button"))
            )
            self.esperar_y_hacer_clic(unlock_button)
            print("Rabby desbloqueado exitosamente")
        except Exception as e:
            print(f"Error al desbloquear Rabby: {str(e)}")

    def manejar_firma_contrato(self):
        sign_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Firmar') or contains(text(), 'Sign')]")
        self.esperar_y_hacer_clic(sign_button)

    def manejar_confirmacion(self):
        confirm_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Confirmar') or contains(text(), 'Confirm')]")
        self.esperar_y_hacer_clic(confirm_button)

    def manejar_conexion(self):
        connect_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Conectar') or contains(text(), 'Connect')]")
        self.esperar_y_hacer_clic(connect_button)

    def manejar_cambio_red(self):
        switch_network_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Cambiar red') or contains(text(), 'Switch network')]")
        self.esperar_y_hacer_clic(switch_network_button)
