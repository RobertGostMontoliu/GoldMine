import requests
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
from ui.json_path import resource_path

class GPMManager:
    def __init__(self, api_url="http://127.0.0.1:19995"):
        # Load url from config.json
        config_path = resource_path("ui/JSON_FILE/config.json")
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
    
        self.api_url = config.get("gpm_url", api_url)

    def fetch_profiles(self, group=None, max_profiles=1000, sort=1, search=None):
        per_page = min(max_profiles, 1000)
        params = {
            "group_id": group,
            "page": 1,
            "per_page": per_page,
            "sort": sort,
            "search": search
        }
        try:
            response = requests.get(f"{self.api_url}/api/v3/profiles", params=params)
            data = response.json()

            if data['success']:
                profiles = data['data']
                filtered_profiles = [
                    {
                        "id": profile["id"],
                        "name": profile["name"],
                        "group_id": profile.get("group_id", "Sin Grupo"),
                        "created_at": profile["created_at"]
                    }
                    for profile in profiles
                ]
                return filtered_profiles[:max_profiles]
            else:
                print(f"Error: {data['message']}")
                return []
        except Exception as e:
            print(f"Error al conectar con la API de GPM_Login: {e}")
            return []

    def open_profile(self, profile_id, **kwargs):
        url = f"{self.api_url}/api/v3/profiles/start/{profile_id}"
        params = {
            "win_scale": kwargs.get("win_scale", 1.0),  # Escala de ventana
            "win_pos": kwargs.get("win_pos", "0,0"),    # Posición de ventana
            "win_size": kwargs.get("win_size", "500,500"),  # Tamaño de ventana
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                profile_data = data.get("data", {})
                if profile_data.get("success") is False:
                    print(f"Error al abrir el perfil GPM: {profile_data.get('message', 'Error desconocido')}")
                    return None
                
                remote_debugging_address = profile_data.get("remote_debugging_address")
                driver_path = profile_data.get("driver_path")
                
                if remote_debugging_address and driver_path:
                    options = webdriver.ChromeOptions()
                    options.add_experimental_option("debuggerAddress", remote_debugging_address)
                    service = Service(executable_path=driver_path)
                    driver = webdriver.Chrome(service=service, options=options)
                    return driver
                else:
                    print("Falta información necesaria en la respuesta de la API")
            else:
                print(f"Error al abrir el perfil GPM: {data.get('message', 'Error desconocido')}")
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión al abrir el perfil GPM: {e}")
        except Exception as e:
            print(f"Error inesperado al abrir el perfil GPM: {e}")
        return None

    def get_profile_info(self, profile_id):
        try:
            info_url = f"{self.api_url}/api/v1/profile/info?profile_id={profile_id}"
            print(f"Obteniendo información del perfil: {info_url}")
            
            response = requests.get(info_url)
            
            if response.status_code != 200:
                print(f"Error al obtener información del perfil. Código de estado: {response.status_code}")
                return None

            data = response.json()
            print(f"Información del perfil: {data}")

            if data.get('code') != 0:
                print(f"Error al obtener información del perfil: {data.get('msg', 'Mensaje de error desconocido')}")
                return None

            # Aquí puedes procesar la información del perfil y abrir el navegador manualmente
            # Por ejemplo:
            options = webdriver.ChromeOptions()
            # Añadir opciones necesarias basadas en la información del perfil
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Navegar a la URL del perfil si está disponible
            if 'data' in data and 'url' in data['data']:
                driver.get(data['data']['url'])
            
            return driver

        except Exception as e:
            print(f"Error al obtener información del perfil: {e}")
            return None
        
    def close_browser(self, profile_id):
        close_url = f"{self.api_url}/api/v3/profiles/close/{profile_id}"
        try:
            response = requests.get(close_url)
            data = response.json()
            if response.status_code == 200 and data.get('success'):
                print(f"Navegador cerrado correctamente para el perfil {profile_id}.")
            else:
                print(f"Error al cerrar el navegador para el perfil {profile_id}. Mensaje: {data.get('message', 'Desconocido')}")
        except requests.exceptions.RequestException as e:
            print(f"Error al cerrar el navegador para el perfil {profile_id}: {e}")
            
    def get_profile_name_by_id(self, profile_id):
        profiles = self.fetch_profiles()  # Obtén todos los perfiles
        for profile in profiles:
            if profile['id'] == profile_id:
                return profile['name']  # Devuelve el nombre del perfil si coincide el ID
        return "Empty"  # Retorna None si no se encuentra el perfil

class ADSPowerManager:
    def __init__(self, api_url):
        # Load url from config.json
        config_path = resource_path("ui/JSON_FILE/config.json")
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)

        self.api_url = config.get("adspower_url", api_url)

    def fetch_profiles(self, max_profiles=1000, sort_by="created_time", sort_order="asc"):
        # Ajustar el parámetro page_size para solicitar hasta 1000 perfiles
        page_size = min(max_profiles, 1000)  # Máximo 1000 perfiles
        user_sort = {sort_by: sort_order}  # Definir el orden de los perfiles
        
        params = {
            "page": 1,  # Solo haremos una solicitud
            "page_size": page_size,
            "user_sort": user_sort  # Agregar el campo de ordenación
        }
        try:
            response = requests.get(f"{self.api_url}/api/v1/user/list", params=params)
            data = response.json()
            if data['code'] == 0:
                profiles = data['data']['list']
                filtered_profiles = [
                    {
                        "user_id": profile["user_id"],
                        "name": profile["name"],
                        "group_name": profile["group_name"],
                        "created_time": profile["created_time"]
                    }
                    for profile in profiles
                ]
                return filtered_profiles[:max_profiles]
            else:
                print(f"Error: {data['msg']}")
                return []
        except Exception as e:
            print(f"Error al conectar con la API de ADS_Power: {e}")
            return []

    def open_profile(self, profile_id):
        try:
            response = requests.get(f"{self.api_url}/api/v1/browser/start?user_id={profile_id}")
            data = response.json()
            if data['code'] == 0:
                debugger_address = data['data']['ws']['selenium']
                options = webdriver.ChromeOptions()
                options.add_experimental_option("debuggerAddress", debugger_address)
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                
                # Esperar a que el navegador esté completamente cargado
                time.sleep(5)
                return driver
            else:
                print(f"Error al abrir el perfil ADS: {data['msg']}")
                return None
        except Exception as e:
            print(f"Error al abrir el perfil ADS: {e}")
            return None
        
    def close_browser(self, profile_id):
        close_url = f"{self.api_url}/api/v3/profiles/stop/{profile_id}"
        try:
            response = requests.get(close_url)
            data = response.json()
            if response.status_code == 200 and data.get('success'):
                print(f"Navegador cerrado correctamente para el perfil {profile_id}.")
            else:
                print(f"Error al cerrar el navegador para el perfil {profile_id}. Mensaje: {data.get('message', 'Desconocido')}")
        except requests.exceptions.RequestException as e:
            print(f"Error al cerrar el navegador para el perfil {profile_id}: {e}")

class ChromeManager:
    def __init__(self, profile_path):
        self.profile_path = profile_path

    def fetch_profiles(self):
        profiles = []
        if os.path.exists(self.profile_path):
            for folder in os.listdir(self.profile_path):
                if folder.startswith("Profile") or folder == "Default":
                    profiles.append(folder)
        else:
            print(f"Ruta no válida: {self.profile_path}")
        return profiles

    def open_profile(self, profile_name):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument(f"user-data-dir={self.profile_path}")
            options.add_argument(f"profile-directory={profile_name}")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Esperar a que el navegador esté completamente cargado
            time.sleep(5)
            return driver
        except Exception as e:
            print(f"Error al abrir el perfil Chrome: {e}")
            return None
