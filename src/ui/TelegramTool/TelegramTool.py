from PyQt5.QtWidgets import (QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QGroupBox, QAbstractItemView, QComboBox, QWidget, QDialog, QTableWidgetItem)
from ui.PlantillaAirdrop import PlantillaAirdrop
import json
import os
import re
from selenium.webdriver.support import expected_conditions as EC
from ui.MultiThreadFarming import iniciar_farmeo_multiple
from ui.style_box import apply_text_input_style
from ui.style_box import apply_button_style, apply_button_grey_style
from ui.LogWindow import LogWindow
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QTimer
from ui.json_path import resource_path

class TelegramToolPage(PlantillaAirdrop):
    def __init__(self, window):
        # Llamamos al constructor de la plantilla base con el título específico de telegram Airdrop
        super().__init__(title="Telegram Accounts")
        self.window = window

        # Cargar la tabla de perfiles
        self.load_gpm_profiles()  # Por ejemplo, cargar perfiles desde GPM al inicio
        
        # Añadir Window Settings
        self.add_window_settings()
        
        # Añadir opciones específicas de telegram
        self.add_telegram_settings()
        
        # Añadir botones de ejecución en la parte derecha e inferior
        self.add_execution_buttons()

        # Modificar la configuración de selección de la tabla de perfiles
        self.profile_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.profile_table.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def add_telegram_settings(self):
        # Añadir recuadro de texto multi-línea para pegar el texto de los teléfonos y links del chino
        self.phone_option = QTextEdit()
        self.phone_option.setPlaceholderText("Pegar aquí el texto de los phone/URL")
        apply_text_input_style(self.phone_option)  # Apply the common style
        self.advanced_layout.addWidget(self.phone_option)
                
    def add_window_settings(self):
        # Crear un QGroupBox para los ajustes de la ventana
        window_settings_group = QGroupBox("Window Settings")
        window_layout = QVBoxLayout()
        
        # Añadir la opción de Multithread
        multithread_layout = QHBoxLayout()
        multithread_label = QLabel("Multithread:")
        self.multithread_input = QLineEdit("1")  # Número de threads por defecto a 1
        apply_text_input_style(self.multithread_input)  # Apply the common style
        multithread_layout.addWidget(multithread_label)
        multithread_layout.addWidget(self.multithread_input)
        window_layout.addLayout(multithread_layout)
        
        # Country
        country_layout = QHBoxLayout()
        country_label = QLabel("Country:")

        # Create a combo box for countries
        self.country_input = QComboBox()

        # List of countries
        countries = [
            "Afghanistan", "Albania", "Algeria", "American Samoa", "Andorra", "Angola",
            "Anguilla", "Anonymous Numbers", "Antigua & Barbuda", "Argentina", "Armenia",
            "Aruba", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh",
            "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia",
            "Bonaire, Sint Eustatius & Saba", "Bosnia & Herzegovina", "Botswana", "Brazil",
            "British Virgin Islands", "Brunei Darussalam", "Bulgaria", "Burkina Faso", "Burundi",
            "Cambodia", "Cameroon", "Canada", "Cape Verde", "Cayman Islands",
            "Central African Rep.", "Chad", "Chile", "China", "Colombia", "Comoros",
            "Congo (Dem. Rep.)", "Congo (Rep.)", "Cook Islands", "Costa Rica", "Côte d'Ivoire",
            "Croatia", "Cuba", "Curaçao", "Cyprus", "Czech Republic", "Denmark", "Diego Garcia",
            "Djibouti", "Dominica", "Dominican Rep.", "Ecuador", "Egypt", "El Salvador",
            "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Falkland Islands",
            "Faroe Islands", "Fiji", "Finland", "France", "French Guiana", "French Polynesia",
            "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Gibraltar", "Greece", "Greenland",
            "Grenada", "Guadeloupe", "Guam", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana",
            "Haiti", "Honduras", "Hong Kong", "Hungary", "Iceland", "India", "Indonesia", "Iran",
            "Iraq", "Ireland", "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan",
            "Kenya", "Kiribati", "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon",
            "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Macau",
            "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands",
            "Martinique", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco",
            "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia",
            "Nauru", "Nepal", "Netherlands", "New Caledonia", "New Zealand", "Nicaragua", "Niger",
            "Nigeria", "Niue", "Norfolk Island", "North Korea", "North Macedonia",
            "Northern Mariana Islands", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama",
            "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal",
            "Puerto Rico", "Qatar", "Réunion", "Romania", "Russian Federation", "Rwanda",
            "Saint Helena", "Saint Kitts & Nevis", "Saint Lucia", "Saint Pierre & Miquelon",
            "Saint Vincent & the Grenadines", "Samoa", "San Marino", "São Tomé & Príncipe",
            "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore",
            "Sint Maarten", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa",
            "South Korea", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden",
            "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste",
            "Togo", "Tokelau", "Tonga", "Trinidad & Tobago", "Tunisia", "Turkey", "Turkmenistan",
            "Turks & Caicos Islands", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates",
            "United Kingdom", "Uruguay", "US Virgin Islands", "USA", "Uzbekistan", "Vanuatu",
            "Venezuela", "Vietnam", "Wallis & Futuna", "Yemen", "Zambia", "Zimbabwe"
            ]
        
        # Add countries to the combo box
        self.country_input.addItems(countries)
        
        country_layout.addWidget(country_label)
        country_layout.addWidget(self.country_input)
        window_layout.addLayout(country_layout)

        # Tamaño de la ventana
        size_layout = QHBoxLayout()
        size_label = QLabel("Window Size:")
        self.window_width_input = QLineEdit("500")  # Ancho por defecto
        apply_text_input_style(self.window_width_input)  # Apply the common style
        self.window_height_input = QLineEdit("500")  # Alto por defecto
        apply_text_input_style(self.window_height_input)  # Apply the common style
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.window_width_input)
        size_layout.addWidget(QLabel("x"))  # Separador entre ancho y alto
        size_layout.addWidget(self.window_height_input)
        window_layout.addLayout(size_layout)

        # Escala de la ventana
        scale_layout = QHBoxLayout()
        scale_label = QLabel("Window Scale (%):")
        self.window_scale_input = QLineEdit("100")  # Escala por defecto
        apply_text_input_style(self.window_scale_input)  # Apply the common style
        scale_layout.addWidget(scale_label)
        scale_layout.addWidget(self.window_scale_input)
        window_layout.addLayout(scale_layout)

        # Posición de la ventana
        position_layout = QHBoxLayout()
        position_label = QLabel("Window Position:")
        self.window_pos_x_input = QLineEdit("0")  # Posición X por defecto
        apply_text_input_style(self.window_pos_x_input)  # Apply the common style
        self.window_pos_y_input = QLineEdit("0")  # Posición Y por defecto
        apply_text_input_style(self.window_pos_y_input)  # Apply the common style
        position_layout.addWidget(position_label)
        position_layout.addWidget(self.window_pos_x_input)
        position_layout.addWidget(QLabel(","))  # Separador entre X e Y
        position_layout.addWidget(self.window_pos_y_input)
        window_layout.addLayout(position_layout)
        
        # Añadir Zoom
        zoom_layout = QHBoxLayout()
        zoom_label = QLabel("Zoom (%):")
        self.window_zoom_input = QLineEdit("100")  # Zoom por defecto al 100%
        apply_text_input_style(self.window_zoom_input)  # Apply the common style
        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(self.window_zoom_input)
        window_layout.addLayout(zoom_layout)
        
        # Añadir Password actual
        actualPass_layout = QHBoxLayout()
        actualPass_label = QLabel("Old Password:")
        self.window_actualPass_input = QLineEdit("")  
        apply_text_input_style(self.window_actualPass_input)  # Apply the common style
        actualPass_layout.addWidget(actualPass_label)
        actualPass_layout.addWidget(self.window_actualPass_input)
        window_layout.addLayout(actualPass_layout)

        # Añadir Password nueva
        newPass_layout = QHBoxLayout()
        newPass_label = QLabel("New Password:")
        self.window_newPass_input = QLineEdit("")  
        apply_text_input_style(self.window_newPass_input)  # Apply the common style
        newPass_layout.addWidget(newPass_label)
        newPass_layout.addWidget(self.window_newPass_input)
        window_layout.addLayout(newPass_layout)

        # Crear un widget para Confirm Password y su layout
        self.confirmPass_widget = QWidget()  # Crear un widget para contener el layout de confirm password
        self.confirmPass_layout = QHBoxLayout()
        self.confirmPass_label = QLabel("Confirm Password:")
        self.window_confirmPass_input = QLineEdit("")  
        apply_text_input_style(self.window_confirmPass_input)  # Apply the common style
        self.confirmPass_error_label = QLabel()  
        self.confirmPass_error_label.setStyleSheet("color: red;")  
        
        self.confirmPass_layout.addWidget(self.confirmPass_label)
        self.confirmPass_layout.addWidget(self.window_confirmPass_input)
        self.confirmPass_layout.addWidget(self.confirmPass_error_label)
        
        # Establecer el layout en el widget de Confirm Password
        self.confirmPass_widget.setLayout(self.confirmPass_layout)
        window_layout.addWidget(self.confirmPass_widget)  # Añadir el widget al layout de la ventana
        self.confirmPass_widget.setVisible(False)  # Ocultar el widget inicialmente

        # Conectar el evento de texto modificado para validar contraseñas
        self.window_newPass_input.textChanged.connect(self.update_confirm_password_field)
        self.window_confirmPass_input.textChanged.connect(self.update_confirm_password_field)

        # Aplicar el layout al QGroupBox
        window_settings_group.setLayout(window_layout)

        # **Añadir el grupo de Window Settings al layout avanzado**
        self.advanced_layout.addWidget(window_settings_group)
        
    # Método para obtener los valores de las cajas de Window Settings
    def get_window_settings(self):
        win_size = f"{self.window_width_input.text()},{self.window_height_input.text()}"
        win_scale = float(self.window_scale_input.text()) / 100  # Convertir a decimal
        win_pos = f"{self.window_pos_x_input.text()},{self.window_pos_y_input.text()}"
        zoom = float(self.window_zoom_input.text()) / 100  # Convertir zoom a decimal
        return {
            "win_size": win_size,
            "win_scale": win_scale,
            "win_pos": win_pos,
        }
        
    def add_execution_buttons(self):
        # Crear un layout horizontal para los botones
        buttons_layout = QHBoxLayout()

        # Crear los botones de ejecución
        accounts_button = QPushButton("Set Up Accounts")
        apply_button_style(accounts_button)  # Apply the common style 
        self.password_button = QPushButton("Change Password")
        apply_button_grey_style(self.password_button)  # Apply the common style

        # Deshabilitar el botón inicialmente
        self.password_button.setEnabled(False)  
    
        # Conectar el botón de Accounts con la función que ejecuta el script
        accounts_button.clicked.connect(self.button_farm_one)
    
        # Conectar el botón de Password con la función que ejecuta el script
        self.password_button.clicked.connect(self.button_farm_two)

        # Añadir los botones al layout
        buttons_layout.addWidget(accounts_button)
        buttons_layout.addWidget(self.password_button)

        # Añadir el layout de botones directamente al advanced_layout
        self.advanced_layout.addLayout(buttons_layout)
            
    def button_farm_one(self):
        # Clear the content of farm_logs.json
        json_path = resource_path("ui//JSON_FILE//farm_logs.json")
        with open(json_path, 'w') as file:
            json.dump([], file)
        
        # Verificar si se ha ingresado el país
        country = self.country_input.currentText().strip()
        if not country:
            QMessageBox.warning(self, "Advertencia", "Falta rellenar el campo de país.")
            return

        # Obtener el texto del bloque de texto y verificar el formato
        phone_url_text = self.phone_option.toPlainText().strip()
        if not self.validate_phone_url_format(phone_url_text):
            QMessageBox.warning(self, "Advertencia", "El formato de 'phone / URL' no es correcto. Debe ser: 'Número / URL'")
            return

        # Guardar la información en un JSON
        self.save_info_to_json(country, phone_url_text)

        # Si todo está correcto, continuar con el proceso
        selected_profiles = self.get_selected_profiles()
        
        if not selected_profiles:
            QMessageBox.warning(self, "Advertencia", "No se seleccionaron perfiles. Por favor, selecciona al menos un perfil antes de iniciar el farmeo.")
            return

        num_concurrent = int(self.multithread_input.text())
        window_settings = self.get_window_settings()

        self.farming_thread = iniciar_farmeo_multiple(selected_profiles, num_concurrent, "TelegramTool", window_settings)
        
        # Remove the previous Log column if it exists
        log_column_index = self.profile_table.columnCount() - 1
        if self.profile_table.horizontalHeaderItem(log_column_index).text() == "Log":
            self.profile_table.removeColumn(log_column_index)
        
        # Add a new column for logs
        self.profile_table.setColumnCount(self.profile_table.columnCount() + 1)
        self.profile_table.setHorizontalHeaderItem(self.profile_table.columnCount() - 1, QTableWidgetItem("Log"))
        
        # Define the colors for animation
        colors = ['#FFE862', '#FFE44D', '#FFE137', '#FFDE21', '#FFD901']
        self.animation_timers = {}

        # Add log buttons to each selected profile row
        for row in range(self.profile_table.rowCount()):
            item = self.profile_table.item(row, 0)
            if item and item.isSelected():
                log_button = QPushButton("View Log")
                log_button.setStyleSheet("background-color: yellow; color: black; border: 1px solid black; padding: 5px 10px; border-radius: 5px;")
                log_button.clicked.connect(lambda _, r=row: self.show_log_window(r))
                self.profile_table.setCellWidget(row, self.profile_table.columnCount() - 1, log_button)
            
                # Set up a timer to animate the button color
                timer = QTimer(self)
                timer.timeout.connect(lambda button=log_button: self.animate_button_color(button, colors))
                timer.start(200)  # Update color every 200 milliseconds

                # Store the timer with the button as the key
                self.animation_timers[log_button] = timer

        # Update log buttons dynamically while farming is in progress
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.update_log_buttons(selected_profiles))
        self.timer.start(1000)  # Update every second

        # Stop the timer when farming is done
        self.farming_thread.finished.connect(self.timer.stop)
        self.farming_thread.finished.connect(lambda: self.update_log_buttons(selected_profiles))

    def button_farm_two(self):
        # Clear the content of farm_logs.json
        json_path = resource_path("ui//JSON_FILE//farm_logs.json")
        with open(json_path, 'w') as file:
            json.dump([], file)
        
        # Verificar si se ha ingresado la password vieja
        oldPass = self.window_actualPass_input.text().strip()
        if not oldPass:
            QMessageBox.warning(self, "Advertencia", "Falta rellenar el campo de contraseña vieja.")
            return
        
        # Verificar si se ha ingresado la password nueva
        newPass = self.window_newPass_input.text().strip()
        if not newPass:
            QMessageBox.warning(self, "Advertencia", "Falta rellenar el campo de contraseña nueva.")
            return

        # Guardar la información en un JSON
        self.save_pass_to_json(oldPass, newPass)

        # Si todo está correcto, continuar con el proceso
        selected_profiles = self.get_selected_profiles()
        
        if not selected_profiles:
            QMessageBox.warning(self, "Advertencia", "No se seleccionaron perfiles. Por favor, selecciona al menos un perfil antes de iniciar el farmeo.")
            return

        num_concurrent = int(self.multithread_input.text())
        window_settings = self.get_window_settings()

        self.farming_thread = iniciar_farmeo_multiple(selected_profiles, num_concurrent, "telegramToolPassword", window_settings)
        
        # Remove the previous Log column if it exists
        log_column_index = self.profile_table.columnCount() - 1
        if self.profile_table.horizontalHeaderItem(log_column_index).text() == "Log":
            self.profile_table.removeColumn(log_column_index)
        
        # Add a new column for logs
        self.profile_table.setColumnCount(self.profile_table.columnCount() + 1)
        self.profile_table.setHorizontalHeaderItem(self.profile_table.columnCount() - 1, QTableWidgetItem("Log"))
        
        # Define the colors for animation
        colors = ['#FFE862', '#FFE44D', '#FFE137', '#FFDE21', '#FFD901']
        self.animation_timers = {}

        # Add log buttons to each selected profile row
        for row in range(self.profile_table.rowCount()):
            item = self.profile_table.item(row, 0)
            if item and item.isSelected():
                log_button = QPushButton("View Log")
                log_button.setStyleSheet("background-color: yellow; color: black; border: 1px solid black; padding: 5px 10px; border-radius: 5px;")
                log_button.clicked.connect(lambda _, r=row: self.show_log_window(r))
                self.profile_table.setCellWidget(row, self.profile_table.columnCount() - 1, log_button)
            
                # Set up a timer to animate the button color
                timer = QTimer(self)
                timer.timeout.connect(lambda button=log_button: self.animate_button_color(button, colors))
                timer.start(200)  # Update color every 200 milliseconds

                # Store the timer with the button as the key
                self.animation_timers[log_button] = timer

        # Update log buttons dynamically while farming is in progress
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.update_log_buttons(selected_profiles))
        self.timer.start(1000)  # Update every second

        # Stop the timer when farming is done
        self.farming_thread.finished.connect(self.timer.stop)
        self.farming_thread.finished.connect(lambda: self.update_log_buttons(selected_profiles))
    
    def validate_phone_url_format(self, text):
        # Expresión regular para validar el formato del número de teléfono
        phone_pattern = re.compile(r'^\d+$')  # Solo permite dígitos

        # Expresión regular para validar una URL
        url_pattern = re.compile(r'^(https?://[^\s]+)$')  # Valida URLs que comienzan con http:// o https://

        # Verificar que cada línea siga el formato correcto
        for line in text.split('\n'):
            line = line.strip()
            if " / " not in line or not line:
                return False
        
            phone, url = line.split(" / ", 1)  # Separar en número y URL
            if not (phone_pattern.match(phone) and url_pattern.match(url)):
                return False  # Si no se cumple el formato, devolver False
            
        return True  # Todo es válido

    def save_info_to_json(self, country, phone_url_text):
        # Crear un diccionario con la información
        data = {
            "country": country,
            "phone_urls": phone_url_text.splitlines()  # Convertir el texto en una lista
        }

        # Guardar en un archivo JSON
        file_path = resource_path("ui//JSON_FILE//TelegramTool.json")
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
            
    def save_pass_to_json(self, oldPass, newPass):
        # Crear un diccionario con la información
        data = {
            "oldPassword": oldPass,
            "newPassword": newPass
        }

        # Guardar en un archivo JSON
        file_path = resource_path("ui//JSON_FILE//TelegramToolPasswords.json")
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
            
    def update_confirm_password_field(self):
        new_password = self.window_newPass_input.text().strip()
        confirm_password = self.window_confirmPass_input.text().strip()

        # Mostrar u ocultar el widget de Confirm Password basado en el input de New Password
        self.confirmPass_widget.setVisible(bool(new_password))  # Mostrar si hay texto en New Password

        # Comprobar si las contraseñas coinciden
        if new_password != confirm_password:
            self.confirmPass_error_label.setText("❌")  # Cruz roja
            self.password_button.setEnabled(False)  # Deshabilitar botón
            self.password_button.setStyleSheet("background-color: darkgray;")  # Cambiar a gris
        else:
            self.confirmPass_error_label.setText("✔️")  # Mostrar símbolo de verificación
            self.confirmPass_error_label.setStyleSheet("color: green;")
            self.password_button.setEnabled(True)  # Habilitar botón
            apply_button_style(self.password_button)  # Cambiar a estilo normal

    def get_selected_profiles(self):
        selected_profiles = []
        for row in range(self.profile_table.rowCount()):
            # Verificar si la primera columna contiene un QTableWidgetItem
            item = self.profile_table.item(row, 0)
            if item and item.isSelected():
                # Asumiendo que el ID del perfil está en la segunda columna
                profile_id = self.profile_table.item(row, 1).text()
                selected_profiles.append(profile_id)
        return selected_profiles
    
    def animate_button_color(self, button, colors):
        # Rotate through the colors
        color_index = (getattr(button, 'color_index', 0) + 1) % len(colors)
        button.setStyleSheet(f"background-color: {colors[color_index]}; color: black; border: 1px solid black; padding: 5px 10px; border-radius: 5px;")
        button.color_index = color_index
    
    def update_log_buttons(self, selected_profiles):
        farm_logs = self.load_farm_logs()
        for row in range(self.profile_table.rowCount()):
            item = self.profile_table.item(row, 0)
            if item:
                profile_id = self.profile_table.item(row, 1).text()
                if profile_id in selected_profiles:
                    log_button = self.profile_table.cellWidget(row, self.profile_table.columnCount() - 1)
                    profile_logs = next((log for log in farm_logs if log["farm_name"].endswith(profile_id)), None)
                    if profile_logs:
                        all_done = all(log["status"] == "DONE" for log in profile_logs["logs"])
                        any_failed = any(log["status"] == "FAILED" for log in profile_logs["logs"])
                        # Stop the animation timer for this button
                        timer = self.animation_timers.get(log_button)
                        if timer:
                            timer.stop()
                        if all_done:
                            log_button.setStyleSheet("""
                                QPushButton {
                                    background-color: green;
                                    color: white;
                                    border: 1px solid black;
                                    padding: 5px 10px;
                                    border-radius: 5px;
                                }
                                QPushButton:hover {
                                    background-color: #74b9ff;
                                }
                            """)
                        elif any_failed:
                            log_button.setStyleSheet("""
                                QPushButton {
                                    background-color: red;
                                    color: white;
                                    border: 1px solid black;
                                    padding: 5px 10px;
                                    border-radius: 5px;
                                }
                                QPushButton:hover {
                                    background-color: #74b9ff;
                                }
                            """)
                        else:
                            log_button.setStyleSheet("""
                                QPushButton {
                                    background-color: yellow;
                                    color: black;
                                    border: 1px solid black;
                                    padding: 5px 10px;
                                    border-radius: 5px;
                                }
                                QPushButton:hover {
                                    background-color: #74b9ff;
                                }
                            """)

    def show_log_window(self, row):
        profile_id = self.profile_table.item(row, 1).text()
        farm_logs = self.load_farm_logs()
        
        # Find the logs for the selected profile
        profile_logs = next((log for log in farm_logs if log["farm_name"].endswith(profile_id)), None)
        
        if profile_logs:
            log_window = QDialog(self)
            log_window.setWindowTitle(f"Log for Profile {profile_id}")
            layout = QVBoxLayout()
            
            for log in profile_logs["logs"]:
                task_name = log["task_name"]
                status = log["status"]
                color = "green" if status == "DONE" else "red"
                log_label = QLabel(f"{task_name}: <span style='color:{color}'>{status}</span>")
                layout.addWidget(log_label)
            
            log_window.setLayout(layout)
            log_window.exec_()
        else:
            QMessageBox.warning(self, "Advertencia", f"No logs found for profile {profile_id}")
            
    def load_farm_logs(self):
        file_path = resource_path("ui//JSON_FILE//farm_logs.json")
        with open(file_path, 'r') as file:
            farm_logs = json.load(file)
        return farm_logs

    def closeEvent(self, event):
        if hasattr(self, 'farming_thread') and self.farming_thread.isRunning():
            self.farming_thread.stop()
            self.farming_thread.wait()
        event.accept()
