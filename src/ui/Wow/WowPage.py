from PyQt5.QtWidgets import (QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QGroupBox, QCheckBox, QAbstractItemView)
from ui.PlantillaAirdrop import PlantillaAirdrop
from selenium.webdriver.support import expected_conditions as EC
from ui.MultiThreadFarming import iniciar_farmeo_multiple
from ui.style_text import apply_text_input_style
from ui.style_box import apply_button_style

class WowPage(PlantillaAirdrop): 
    def __init__(self, window):
        # Llamamos al constructor de la plantilla base con el título específico de Wow
        super().__init__(title="Wow")
        self.window = window

        # Cargar la tabla de perfiles
        self.load_gpm_profiles()  # Por ejemplo, cargar perfiles desde GPM al inicio
        
        # **Añadir Window Settings**
        self.add_window_settings()
        
        # Añadir opciones específicas de Wow  
        self.add_wow_settings()
        
        # Añadir botones de ejecución en la parte derecha e inferior
        self.add_execution_buttons()

        # Modificar la configuración de selección de la tabla de perfiles
        self.profile_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.profile_table.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def add_wow_settings(self):
        # Aqu puedes agregar cualquier configuración o widgets específicos para Wow

        # Añadir red de testnet a la wallet
        self.testnet_option = QCheckBox("Añadir red de testnet a la wallet")
        self.advanced_layout.addWidget(self.testnet_option)
        
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
        play_button = QPushButton("Play Wow") 
        apply_button_style(play_button)  # Apply the common style 
        
        # Conectar el botón de Play Wow con la nueva función
        play_button.clicked.connect(self.button_farm_two)

        # Añadir los botones al layout
        buttons_layout.addWidget(play_button)

        # Añadir el layout de botones directamente al advanced_layout
        self.advanced_layout.addLayout(buttons_layout)

    def button_farm_two(self):
        selected_profiles = self.get_selected_profiles()

        if not selected_profiles:
            QMessageBox.warning(self, "Advertencia", "No se seleccionaron perfiles. Por favor, selecciona al menos un perfil antes de iniciar el farmeo.")
            return

        num_concurrent = int(self.multithread_input.text())
        window_settings = self.get_window_settings()

        self.farming_thread = iniciar_farmeo_multiple(selected_profiles, num_concurrent, "Wow", window_settings)

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

    def closeEvent(self, event):
        if hasattr(self, 'farming_thread') and self.farming_thread.isRunning():
            self.farming_thread.stop()
            self.farming_thread.wait()
        event.accept()

