import json
from PyQt5.QtWidgets import QVBoxLayout, QFileDialog, QAbstractItemView, QWidget, QMessageBox, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QGroupBox, QTableWidgetItem, QDialog
from PyQt5.QtCore import QTimer
from ui.PlantillaAirdrop import PlantillaAirdrop
from ui.MultiThreadFarming import iniciar_farmeo_multiple
import os
from openpyxl import Workbook
from ui.style_text import apply_text_input_style
from ui.style_box import apply_button_style
from ui.json_path import resource_path

class RabbyWindow(PlantillaAirdrop):
    def __init__(self, window):
        super().__init__(title="Rabby Wallet Creation")
        self.window = window

        # Cargar la tabla de perfiles
        self.load_gpm_profiles()  # Por ejemplo, cargar perfiles desde GPM al inicio

        # Añadir ajustes de ventana
        self.add_window_settings()
        
        # Añadir opciones específicas de Rabby
        self.add_wallet_settings()
        
        # Añadir botones de ejecución
        self.add_execution_buttons()

        # Modificar la configuración de selección de la tabla de perfiles
        self.profile_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.profile_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
    
    def add_wallet_settings(self):       
        # Campo para seleccionar el directorio para guardar el archivo Excel
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Directorio para guardar Excel:")
        self.excel_dir_input = QLineEdit()
        apply_text_input_style(self.excel_dir_input)  # Apply the common style
        dir_button = QPushButton("Seleccionar Directorio")
        apply_button_style(dir_button)  # Apply the common style
        dir_button.clicked.connect(self.select_directory)

        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.excel_dir_input)
        dir_layout.addWidget(dir_button)
        
        # Añadir el layout de directorio al layout avanzado
        self.advanced_layout.addLayout(dir_layout)
        
    def select_directory(self):
        # Abrir un diálogo para seleccionar el directorio
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio")
        if directory:
            self.excel_dir_input.setText(directory)
        
    def add_window_settings(self):
        window_settings_group = QGroupBox("Window Settings")
        window_layout = QVBoxLayout()
        
        multithread_layout = QHBoxLayout()
        multithread_label = QLabel("Multithread:")
        self.multithread_input = QLineEdit("1")
        apply_text_input_style(self.multithread_input)  # Apply the common style
        multithread_layout.addWidget(multithread_label)
        multithread_layout.addWidget(self.multithread_input)
        window_layout.addLayout(multithread_layout)

        size_layout = QHBoxLayout()
        size_label = QLabel("Window Size:")
        self.window_width_input = QLineEdit("500")
        apply_text_input_style(self.window_width_input)  # Apply the common style
        self.window_height_input = QLineEdit("500")
        apply_text_input_style(self.window_height_input)  # Apply the common style
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.window_width_input)
        size_layout.addWidget(QLabel("x"))
        size_layout.addWidget(self.window_height_input)
        window_layout.addLayout(size_layout)

        scale_layout = QHBoxLayout()
        scale_label = QLabel("Window Scale (%):")
        self.window_scale_input = QLineEdit("100")
        apply_text_input_style(self.window_scale_input)  # Apply the common style
        scale_layout.addWidget(scale_label)
        scale_layout.addWidget(self.window_scale_input)
        window_layout.addLayout(scale_layout)

        position_layout = QHBoxLayout()
        position_label = QLabel("Window Position:")
        self.window_pos_x_input = QLineEdit("0")
        apply_text_input_style(self.window_pos_x_input)  # Apply the common style
        self.window_pos_y_input = QLineEdit("0")
        apply_text_input_style(self.window_pos_y_input)  # Apply the common style
        position_layout.addWidget(position_label)
        position_layout.addWidget(self.window_pos_x_input)
        position_layout.addWidget(QLabel(","))
        position_layout.addWidget(self.window_pos_y_input)
        window_layout.addLayout(position_layout)
        
        zoom_layout = QHBoxLayout()
        zoom_label = QLabel("Zoom (%):")
        self.window_zoom_input = QLineEdit("100")
        apply_text_input_style(self.window_zoom_input)  # Apply the common style
        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(self.window_zoom_input)
        window_layout.addLayout(zoom_layout)

        window_settings_group.setLayout(window_layout)
        self.advanced_layout.addWidget(window_settings_group)
        
    def add_execution_buttons(self):
        # Crear un layout horizontal para los botones
        buttons_layout = QHBoxLayout()

        # Crear los botones de ejecución
        claim_button = QPushButton("Farm Rabby")
        apply_button_style(claim_button)  # Apply the common style
        
        # Conectar el botón de Claim Tokens con la función que ejecuta el script
        claim_button.clicked.connect(self.button_farm_one)

        # Añadir los botones al layout
        buttons_layout.addWidget(claim_button)

        # Añadir el layout de botones directamente al advanced_layout
        self.advanced_layout.addLayout(buttons_layout)
            
    def button_farm_one(self):
        # Clear the content of farm_logs.json
        json_path = resource_path("ui\\JSON_FILE\\farm_logs.json")
        with open(json_path, 'w') as file:
            json.dump([], file)
        
        # Obtener el directorio seleccionado para guardar el Excel
        directorio_excel = self.excel_dir_input.text()

        if not directorio_excel:
            QMessageBox.warning(self, "Advertencia", "Por favor selecciona un directorio para guardar el archivo Excel.")
            return

        # Verificar si el directorio es válido
        if not os.path.exists(directorio_excel):
            QMessageBox.warning(self, "Advertencia", "El directorio no existe. Por favor selecciona un directorio válido.")
            return

        # Crear la ruta del archivo Excel
        archivo_excel = os.path.join(directorio_excel, 'seed_phrases.xlsx')

        # Verificar si el archivo Excel ya existe
        if not os.path.exists(archivo_excel):
            # Crear el archivo Excel vacío si no existe
            wb = Workbook()
            ws = wb.active
            ws.append(['# de perfil', 'Nombre de perfil', 'Dirección de billetera', 'Seed phrase', 'Estado'])
            wb.save(archivo_excel)
            print(f"Archivo Excel creado: {archivo_excel}")
        else:
            print(f"Archivo Excel ya existe: {archivo_excel}")

        # Guardar el directorio del archivo Excel en un archivo JSON
        self.guardar_directorio_json(archivo_excel)

        # Obtener los perfiles seleccionados
        selected_profiles = self.get_selected_profiles()
    
        if not selected_profiles:
            QMessageBox.warning(self, "Advertencia", "No se seleccionaron perfiles. Por favor, selecciona al menos un perfil antes de iniciar el farmeo.")
            return

        # Obtener las configuraciones de la ventana
        num_concurrent = int(self.multithread_input.text())
        window_settings = self.get_window_settings()

        # Llamar a RabbyScript con el archivo Excel
        self.farming_thread = iniciar_farmeo_multiple(selected_profiles, num_concurrent, "rabby", window_settings)
        
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
        file_path = resource_path("ui\\JSON_FILE\\farm_logs.json")
        with open(file_path, 'r') as file:
            farm_logs = json.load(file)
        return farm_logs

    def guardar_directorio_json(self, archivo_excel):
        # Ruta del archivo JSON
        json_path = resource_path("ui\\JSON_FILE\\UrlRabbyAccounts.json")
        
        # Crear un diccionario con el directorio del archivo Excel
        data = {
            "archivo_excel": archivo_excel
        }
        
        # Guardar el directorio en el archivo JSON
        with open(json_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        
        print(f"Directorio del archivo Excel guardado en {json_path}")

    def get_selected_profiles(self):
        selected_profiles = []
        for row in range(self.profile_table.rowCount()):
            item = self.profile_table.item(row, 0)
            if item and item.isSelected():
                profile_id = self.profile_table.item(row, 1).text()
                selected_profiles.append(profile_id)
        return selected_profiles
    
    def get_window_settings(self):
        win_size = f"{self.window_width_input.text()},{self.window_height_input.text()}"
        win_scale = float(self.window_scale_input.text()) / 100
        win_pos = f"{self.window_pos_x_input.text()},{self.window_pos_y_input.text()}"
        zoom = float(self.window_zoom_input.text()) / 100
        return {
            "win_size": win_size,
            "win_scale": win_scale,
            "win_pos": win_pos,
            "zoom": zoom,
        }

    def closeEvent(self, event):
        if hasattr(self, 'farming_thread') and self.farming_thread.isRunning():
            self.farming_thread.stop()
            self.farming_thread.wait()
        event.accept()
