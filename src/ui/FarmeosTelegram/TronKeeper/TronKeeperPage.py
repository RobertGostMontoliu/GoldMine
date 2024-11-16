from PyQt5.QtWidgets import (QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QGroupBox, QCheckBox, QAbstractItemView, QMessageBox,QTableWidgetItem)
from ui.PlantillaAirdrop import PlantillaAirdrop
from ui.style_text import apply_text_input_style
from ui.style_box import apply_button_style
from ui.LogWindow import LogWindow
from ui.MultiThreadFarming import iniciar_farmeo_multiple
import os
from ui.json_path import resource_path

class TronKeeperPage(PlantillaAirdrop): 
    def __init__(self, window):
        super().__init__(title="TronKeeper Airdrop") 
        self.window = window

        # Cargar la tabla de perfiles
        self.load_gpm_profiles()
        
        # Añadir Window Settings
        self.add_window_settings()
        
        # Añadir opciones específicas de TronKeeper
        self.add_tronkeeper_settings()
        
        # Añadir botón de ejecución
        self.add_execution_button()

        # Modificar la configuración de selección de la tabla de perfiles
        self.profile_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.profile_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
    def add_tronkeeper_settings(self):
        # Agregar el checkbox para activar o desactivar el TronKeeperClicker 
        self.checkbox_tronkeeper_clicker = QCheckBox("Play the game")
        self.advanced_layout.addWidget(self.checkbox_tronkeeper_clicker)
        
    def is_tronkeeper_clicker_activated(self): 
        # Retorna el estado del checkbox
        return self.checkbox_tronkeeper_clicker.isChecked()
        
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
        
    def add_execution_button(self):
        button_layout = QHBoxLayout()
        farm_button = QPushButton("Farm TronKeeper") 
        apply_button_style(farm_button)  # Apply the common style 
        farm_button.clicked.connect(self.button_farm)
        button_layout.addWidget(farm_button)
        self.advanced_layout.addLayout(button_layout)
            
    def button_farm(self):
        import json

        # Create the JSON file path
        json_path = resource_path("ui\\JSON_FILE\\farm_logs.json")
        
        # Ensure the directory exists
        json_dir = os.path.dirname(json_path)
        os.makedirs(json_dir, exist_ok=True)
        
        # Clear the log file
        with open(json_path, 'w') as file:
            json.dump([], file)

        selected_profiles = self.get_selected_profiles()

        if not selected_profiles:
            QMessageBox.warning(self, "Advertencia", "No se seleccionaron perfiles. Por favor, selecciona al menos un perfil antes de iniciar el farmeo.")
            return

        num_concurrent = int(self.multithread_input.text())
    
        # Obtener configuraciones de la ventana
        window_settings = self.get_window_settings()

        # Actualizar el valor del checkbox para TronKeeper Clicker 
        window_settings["tronkeeper_clicker_activado"] = self.checkbox_tronkeeper_clicker.isChecked()

        # Iniciar farmeo
        self.farming_thread = iniciar_farmeo_multiple(selected_profiles, num_concurrent, "tronkeeper", window_settings) 
        
        # Remove the previous Log column if it exists
        log_column_index = self.profile_table.columnCount() - 1
        if self.profile_table.horizontalHeaderItem(log_column_index).text() == "Log":
            self.profile_table.removeColumn(log_column_index)
        
        # Add a new column for logs
        self.profile_table.setColumnCount(self.profile_table.columnCount() + 1)
        self.profile_table.setHorizontalHeaderItem(self.profile_table.columnCount() - 1, QTableWidgetItem("Log"))

        # Add log buttons to each selected profile row
        for row in range(self.profile_table.rowCount()):
            item = self.profile_table.item(row, 0)
            if item and item.isSelected():
                log_button = QPushButton("View Log")
                log_button.setStyleSheet("""
                    QPushButton {
                        background-color: #0984e3;
                        color: white;
                        border: 1px solid black;
                        padding: 5px 10px;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #74b9ff;
                    }
                """)  # Add grey border
                log_button.clicked.connect(lambda _, r=row: self.show_log_window(r))
                self.profile_table.setCellWidget(row, self.profile_table.columnCount() - 1, log_button)

    def show_log_window(self, row):
        profile_id = self.profile_table.item(row, 1).text()
        log_window = LogWindow(profile_id)
        log_window.show()

    def get_selected_profiles(self):
        selected_profiles = []
        for row in range(self.profile_table.rowCount()):
            item = self.profile_table.item(row, 0)
            if item and item.isSelected():
                profile_id = self.profile_table.item(row, 1).text()
                selected_profiles.append(profile_id)
        return selected_profiles

    def closeEvent(self, event):
        if hasattr(self, 'farming_thread') and self.farming_thread.isRunning():
            self.farming_thread.stop()
            self.farming_thread.wait()
        event.accept()