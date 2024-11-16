from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, QFrame, QGroupBox, QPushButton, QSpacerItem, QSizePolicy, QAbstractItemView, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.api_manager import GPMManager, ADSPowerManager, ChromeManager
from ui.components import ConfigManager

class PlantillaAirdrop(QWidget):
    def __init__(self, title="Airdrop Template"):
        super().__init__()
        self.title = title
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout(self)

        # Left section layout: profiles table and dropdowns
        left_layout = QVBoxLayout()

        # Title
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Arial', 35, QFont.Bold))
        left_layout.addWidget(title_label)

        # Dropdown container
        dropdown_container = QFrame()
        dropdown_container.setStyleSheet("""
            QFrame {
                background-color: #353535;
                padding: 10px;
            }
            QComboBox {
                background-color: #353535;
                color: white;
                border: 2px solid #2C3E50;
                padding: 5px;
                border-radius: 5px;
            }
            QLabel {
                background-color: #353535;
                color: white;
            }
        """)
        dropdown_layout = QVBoxLayout(dropdown_container)

        # Dropdown for selecting browser
        browser_layout = QHBoxLayout()
        browser_label = QLabel("Navegador:")
        self.browser_dropdown = QComboBox()
        self.browser_dropdown.addItems(["GPM", "ADS", "Chrome"])
        browser_layout.addWidget(browser_label)
        browser_layout.addWidget(self.browser_dropdown)
        browser_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        dropdown_layout.addLayout(browser_layout)

        # Dropdown for filtering by group
        group_layout = QHBoxLayout()
        group_label = QLabel("Filtrar por grupo:")
        self.group_filter = QComboBox()
        self.group_filter.addItem("Todos los grupos")
        group_layout.addWidget(group_label)
        group_layout.addWidget(self.group_filter)
        group_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        dropdown_layout.addLayout(group_layout)

        left_layout.addWidget(dropdown_container)
        
        # Add search bar
        search_layout = QHBoxLayout()
        search_box = QLineEdit()
        search_box.setPlaceholderText("Buscar perfil...")
        search_box.setStyleSheet("""
            QLineEdit {
                background-color: #2C3E50;
                color: white;
                border: 2px solid #2C3E50;
                padding: 5px;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #0984e3;
            }
        """)
        search_button = QPushButton("🔍")
        search_button.setStyleSheet("""
            QPushButton {
                background-color: #0984e3;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #74b9ff;
            }
        """)
        
        # Connect search button and Enter key to the search function
        search_button.clicked.connect(lambda: self.search_profiles(search_box.text()))
        search_box.returnPressed.connect(lambda: self.search_profiles(search_box.text()))
        
        search_layout.addWidget(search_box)
        search_layout.addWidget(search_button)
        left_layout.addLayout(search_layout)  # Add search layout to the left layout

        # Profiles table
        self.profile_table = QTableWidget()
        self.profile_table.setColumnCount(3)
        self.profile_table.setHorizontalHeaderLabels(["Nombre de Perfil", "ID del Perfil", "Grupo"])
        self.profile_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.profile_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.profile_table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Customize table style
        self.profile_table.setShowGrid(False)
        self.profile_table.setAlternatingRowColors(True)
        self.profile_table.setStyleSheet("""
            QTableWidget {
                background-color: #34495e;
                color: #dfe6e9;
                border: none;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: #ffffff;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item {
                background-color: #2d3436;
                color: #dfe6e9;
                border: none;
            }
            QTableWidget::item:alternate {
                background-color: #34495e;
            }
            QTableWidget::item:selected {
                background-color: grey; /* Blue highlight for selected rows */
                color: #ffffff; /* White text for selected rows */
            }
            QTableCornerButton::section {
                background-color: #34495e;
                border: none;
            }
            QHeaderView::section:vertical {
                background-color: #2d3436;
                color: #ffffff;
                font-weight: bold;
                border: none;
            }
        """)
        self.profile_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.profile_table.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)

        left_layout.addWidget(self.profile_table)

        # Connect dropdowns
        self.browser_dropdown.currentIndexChanged.connect(self.load_profiles_from_selected)
        self.group_filter.currentTextChanged.connect(lambda text: self.filter_profiles(text))

        # Right section layout for advanced settings
        right_layout = QVBoxLayout()
        self.advanced_layout = self.create_advanced_settings(right_layout)
        right_layout.addStretch()

        # Add left and right sections to main layout
        main_layout.addLayout(left_layout, 7)
        main_layout.addLayout(right_layout, 2)

    def create_advanced_settings(self, layout):
        advanced_group = QGroupBox("Script Settings")
        advanced_layout = QVBoxLayout()
        advanced_group.setLayout(advanced_layout)
        
        # Add spacing from the top
        layout.addSpacing(160)
        
        layout.addWidget(advanced_group)
        return advanced_layout
    
    def search_profiles(self, query):
        query = query.lower()
        for row in range(self.profile_table.rowCount()):
            name = self.profile_table.item(row, 0).text().lower()
            self.profile_table.setRowHidden(row, query not in name)

    def load_profiles_from_selected(self):
        selected_browser = self.browser_dropdown.currentText()
        if selected_browser == "GPM":
            self.load_gpm_profiles()
        elif selected_browser == "ADS":
            self.load_ads_profiles()
        elif selected_browser == "Chrome":
            self.load_chrome_profiles()
            
    def load_gpm_profiles(self):
        gpm_manager = GPMManager(ConfigManager.get_gpm_url())
        profiles = gpm_manager.fetch_profiles()
        for profile in profiles:
            profile["group_id"] = str(profile.get("group_id", "Sin Grupo"))
        self.display_profiles(profiles)

    def load_ads_profiles(self):
        ads_manager = ADSPowerManager(ConfigManager.get_ads_url())
        profiles = ads_manager.fetch_profiles()
        ads_profiles = [{"name": profile["name"], "id": profile["user_id"], "group_id": profile.get("group_name", "Sin Grupo")} for profile in profiles]
        self.display_profiles(ads_profiles)

    def load_chrome_profiles(self):
        chrome_manager = ChromeManager(ConfigManager.get_chrome_path())
        profiles = [{"name": profile, "id": "Chrome_" + profile, "group_id": "Sin Grupo"} for profile in chrome_manager.fetch_profiles()]
        self.display_profiles(profiles)
        
    def display_profiles(self, profiles):
        self.profile_table.setRowCount(len(profiles))
        groups = set()
        for i, profile in enumerate(profiles):
            self.profile_table.setItem(i, 0, QTableWidgetItem(profile["name"]))
            self.profile_table.setItem(i, 1, QTableWidgetItem(profile["id"]))
            self.profile_table.setItem(i, 2, QTableWidgetItem(profile["group_id"]))
            groups.add(profile["group_id"])
        self.update_group_filter(groups)

    def update_group_filter(self, groups):
        self.group_filter.clear()
        self.group_filter.addItem("Todos los grupos")
        self.group_filter.addItems(sorted(map(str, groups)))

    def filter_profiles(self, selected_group: str) -> None:
        """
        Filter profiles based on selected group
        Args:
            selected_group: Group name to filter by
        """
        for row in range(self.profile_table.rowCount()):
            group = self.profile_table.item(row, 2).text()
            self.profile_table.setRowHidden(
                row, 
                selected_group != "Todos los grupos" and group != selected_group
            )

    def load_profiles(self):
        profiles = [
            {"name": "Perfil 1", "id": "ID_001", "group_id": "Grupo 1"},
            {"name": "Perfil 2", "id": "ID_002", "group_id": "Grupo 2"}
        ]
        self.profile_table.setRowCount(len(profiles))
        self.profiles = profiles
        groups = set()

        for i, profile in enumerate(profiles):
            self.profile_table.setItem(i, 0, QTableWidgetItem(profile["name"]))
            self.profile_table.setItem(i, 1, QTableWidgetItem(profile["id"]))
            self.profile_table.setItem(i, 2, QTableWidgetItem(profile["group_id"]))
            groups.add(profile["group_id"])

        self.update_group_filter(groups)

    def toggle_schedule(self, state):
        if hasattr(self, 'schedule_widget'):
            self.schedule_widget.setVisible(state == Qt.Checked)

    def get_gpm_options(self):
        win_scale = float(self.scale_input.text() or "100") / 100
        win_pos = f"{self.pos_x_input.text() or '0'},{self.pos_y_input.text() or '0'}"
        win_size = f"{self.width_input.text() or '500'},{self.height_input.text() or '500'}"

        return {
            "win_scale": win_scale,
            "win_pos": win_pos,
            "win_size": win_size
        }

    def start_farming(self):
        print("Iniciando el proceso de farmeo")
        gpm_options = self.get_gpm_options()
        print(f"Opciones de GPM: {gpm_options}")

        gpm_manager = GPMManager(ConfigManager.get_gpm_url())
        print(f"URL de GPM: {ConfigManager.get_gpm_url()}")

        selected_profiles = []
        for row in range(self.profile_table.rowCount()):
            checkbox = self.profile_table.cellWidget(row, 0)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                profile_id = self.profile_table.item(row, 2).text()
                selected_profiles.append(profile_id)
                print(f"Perfil seleccionado para farmeo: {profile_id}")

        if not selected_profiles:
            print("No se seleccionaron perfiles. Por favor, selecciona al menos un perfil antes de iniciar el farmeo.")
            return

        print(f"Perfiles seleccionados: {selected_profiles}")
        for profile_id in selected_profiles:
            print(f"Abriendo perfil GPM: {profile_id} con opciones: {gpm_options}")
            driver = gpm_manager.open_profile(profile_id, **gpm_options)
            if driver:
                # Aquí iría el código para iniciar el farmeo con el driver
                pass
            else:
                print(f"No se pudo abrir el perfil GPM: {profile_id}")

    def on_checkbox_changed(self, state):
        sender = self.sender()
        if isinstance(sender, QCheckBox):
            row = self.profile_table.indexAt(sender.pos()).row()
            profile_id = self.profile_table.item(row, 2).text()
            if state == Qt.Checked:
                print(f"Perfil seleccionado: {profile_id}")
            else:
                print(f"Perfil deseleccionado: {profile_id}")