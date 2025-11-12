from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QComboBox, QDialog, QApplication, QAbstractItemView)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os
from ui.TelegramTool.TelegramTool import TelegramToolPage
from ui.twitter.TwitterPage import TwitterToolPage
from ui.components import ConfigManager
from ui.api_manager import GPMManager, ADSPowerManager, ChromeManager
from ui.Wallets.Metamask import MetamaskWindow  
from ui.Wallets.Rabby import RabbyWindow        
from ui.Wallets.Phantom import PhantomWindow    
from ui.Wallets.TonKeeper import TonKeeperWindow 
from ui.Wallets.Ronin import RoninWindow
from ui.style_text import apply_text_input_style
from ui.style_box import apply_button_style
import json
from ui.json_path import resource_path

def create_home_page(window):
    page = QWidget()
    layout = QVBoxLayout(page)
    
    # Load the logo image
    logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
    logo_pixmap = QPixmap(logo_path)
    
    # Create a QLabel to display the logoclear
    
    logo_label = QLabel()
    logo_label.setPixmap(logo_pixmap)
    logo_label.setAlignment(Qt.AlignCenter)
    
    # Add the logo to the layout
    layout.addWidget(logo_label)
    
    # Título
    welcome_label = QLabel('Dashboard - Perfiles')
    welcome_label.setAlignment(Qt.AlignCenter)
    welcome_label.setFont(QFont('Arial', 24, QFont.Bold))
    layout.addWidget(welcome_label)
    
    # Layout para los botones de GPM, ADS y Chrome
    api_buttons_layout = QHBoxLayout()

    gpm_button = QPushButton("Cargar GPM")
    apply_button_style(gpm_button)  # Apply the common style
    gpm_button.clicked.connect(lambda: window.load_profiles_from_api("GPM", profile_table))
    api_buttons_layout.addWidget(gpm_button)

    ads_button = QPushButton("Cargar ADS")
    apply_button_style(ads_button)  # Apply the common style
    ads_button.clicked.connect(lambda: window.load_profiles_from_api("ADS", profile_table))
    api_buttons_layout.addWidget(ads_button)

    chrome_button = QPushButton("Cargar Google Chrome")
    apply_button_style(chrome_button)  # Apply the common style
    chrome_button.clicked.connect(lambda: window.load_profiles_from_api("Chrome", profile_table))
    api_buttons_layout.addWidget(chrome_button)

    layout.addLayout(api_buttons_layout)  # Añadir los botones de API al layout principal

    # Filtros
    filter_layout = QHBoxLayout()
    
    # Filtro 2: Filtro por grupo
    group_filter = QComboBox()
    group_filter.addItem("Todos los grupos")  # Añadir la opción inicial
    filter_layout.addWidget(group_filter)

    # Filtro 3: Buscar por nombre de perfil
    search_box = QLineEdit()
    apply_text_input_style(search_box)  # Apply the common style
    search_box.setPlaceholderText("Buscar perfil...")
    search_button = QPushButton("🔍")
    apply_button_style(search_button)  # Apply the common style
    search_button.clicked.connect(lambda: search_profiles(profile_table, search_box.text()))
    search_box.returnPressed.connect(lambda: search_profiles(profile_table, search_box.text()))
    filter_layout.addWidget(search_box)
    filter_layout.addWidget(search_button)

    layout.addLayout(filter_layout)

    # Profiles table
    profile_table = QTableWidget()
    profile_table.setColumnCount(3)
    profile_table.setHorizontalHeaderLabels(["Nombre de Perfil", "ID del Perfil", "Grupo"])
    profile_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    profile_table.setSelectionBehavior(QAbstractItemView.SelectRows)
    profile_table.setSelectionMode(QAbstractItemView.ExtendedSelection)

    # Customize table style
    profile_table.setShowGrid(False)
    profile_table.setAlternatingRowColors(True)
    profile_table.setStyleSheet("""
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
    profile_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
    profile_table.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)

    layout.addWidget(profile_table)

    # Pre-cargar los perfiles de GPM por defecto
    window.load_profiles_from_api("GPM", profile_table)

    return page

def load_profiles_from_api(window, source, profile_table):
    # Limpiar la tabla de perfiles antes de cargar nuevos datos
    profile_table.setRowCount(0)

    if source == "GPM":
        gpm_manager = GPMManager(ConfigManager.get_gpm_url())
        profiles = gpm_manager.fetch_profiles()
        setup_profile_table(profile_table, ["Nombre de Perfil", "ID", "Grupo"])
        for i, profile in enumerate(profiles):
            profile_table.insertRow(i)
            profile_table.setItem(i, 0, QTableWidgetItem(profile["name"]))
            profile_table.setItem(i, 1, QTableWidgetItem(profile["id"]))
            group_id = profile.get("group_id", "Sin Grupo")
            profile_table.setItem(i, 2, QTableWidgetItem(str(group_id)))  # Convertir a string si no lo es

    elif source == "ADS":
        adspower_manager = ADSPowerManager(ConfigManager.get_ads_url())
        profiles = adspower_manager.fetch_profiles()
        setup_profile_table(profile_table, ["Nombre de Perfil", "ID", "Grupo"])
        for i, profile in enumerate(profiles):
            profile_table.insertRow(i)
            profile_table.setItem(i, 0, QTableWidgetItem(profile["name"]))
            profile_table.setItem(i, 1, QTableWidgetItem(profile["user_id"]))
            profile_table.setItem(i, 2, QTableWidgetItem(profile["group_name"]))

    elif source == "Chrome":
        chrome_manager = ChromeManager(ConfigManager.get_chrome_path())
        profiles = chrome_manager.fetch_profiles()
        setup_profile_table(profile_table, ["Nombre de Perfil"])
        for i, profile in enumerate(profiles):
            profile_table.insertRow(i)
            profile_table.setItem(i, 0, QTableWidgetItem(profile))

def setup_profile_table(profile_table, headers):
    profile_table.clear()
    profile_table.setColumnCount(len(headers))
    profile_table.setHorizontalHeaderLabels(headers)
    profile_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

def search_profiles(table, query):
    query = query.lower()
    for row in range(table.rowCount()):
        name = table.item(row, 0).text().lower()
        if query in name:
            table.showRow(row)
        else:
            table.hideRow(row)
            
def create_telegram_tools_page():
    page = QWidget()
    return TelegramToolPage(page)

def create_Rabby_page():
    page = QWidget()
    return RabbyWindow(page)

def create_Metamask_page():
    page = QWidget()
    return MetamaskWindow(page)

def create_Phantom_page():
    page = QWidget()
    return PhantomWindow(page)

def create_TonKeeper_page():
    page = QWidget()
    return TonKeeperWindow(page)

def create_Ronin_page():
    page = QWidget()
    return RoninWindow(page)

def create_twitter_tools_page():
    page = QWidget()
    return TwitterToolPage(page)

def create_sonic_airdrop_page():
    page = QWidget()
    layout = QVBoxLayout(page)
    return page

def create_blum_airdrop_page():
    page = QWidget()
    layout = QVBoxLayout(page)
    return page

def create_imx_airdrop_page():
    page = QWidget()
    layout = QVBoxLayout(page)
    return page

def create_wolfgame_page(): 
    page = QWidget()
    layout = QVBoxLayout(page)
    return page

def create_wow_page():
    page = QWidget()
    layout = QVBoxLayout(page)
    return page

def create_pawns_page():
    page = QWidget()
    layout = QVBoxLayout(page)
    return page

def create_tronkeeper_page():
    page = QWidget()
    layout = QVBoxLayout(page)
    return page

def create_settings_page():
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(40)
    layout.setAlignment(Qt.AlignTop)  # Ensure the layout starts from the top
    
    title_label = QLabel('Configuraciones')
    title_label.setAlignment(Qt.AlignCenter)
    title_label.setFont(QFont('Arial', 24, QFont.Bold))
    layout.addWidget(title_label)
    
    # Crear formulario para opciones de API
    form_layout = QVBoxLayout()
    form_layout.setSpacing(15)
    
    # GPM_Login URL
    gpm_label = QLabel("GPM API URL")
    gpm_label.setFont(QFont('Arial', 14))
    gpm_api_url = QLineEdit(ConfigManager.get_gpm_url())  # Cargar el valor guardado
    apply_text_input_style(gpm_api_url)  # Apply the common style
    gpm_api_url.setFont(QFont('Arial', 12))
    form_layout.addWidget(gpm_label)
    form_layout.addWidget(gpm_api_url)
    
    # ADS_Power API URL
    adspower_label = QLabel("ADSPower API URL")
    adspower_label.setFont(QFont('Arial', 14))
    adspower_api_url = QLineEdit(ConfigManager.get_ads_url())
    apply_text_input_style(adspower_api_url)  # Apply the common style
    adspower_api_url.setFont(QFont('Arial', 12))
    form_layout.addWidget(adspower_label)
    form_layout.addWidget(adspower_api_url)
    
    # Ruta de perfiles de Google Chrome
    chrome_label = QLabel("Ruta de Perfiles de Google Chrome")
    chrome_label.setFont(QFont('Arial', 14))
    chrome_profiles_path = QLineEdit(ConfigManager.get_chrome_path())  # Cargar el valor guardado
    apply_text_input_style(chrome_profiles_path)  # Apply the common style
    chrome_profiles_path.setFont(QFont('Arial', 12))
    browse_button = QPushButton("🔍")
    apply_button_style(browse_button)  # Apply the common style
    browse_button.setFixedSize(30, 30)
    browse_button.clicked.connect(lambda: chrome_profiles_path.setText(QFileDialog.getExistingDirectory()))
    
    chrome_layout = QHBoxLayout()
    chrome_layout.addWidget(chrome_profiles_path)
    chrome_layout.addWidget(browse_button)
    form_layout.addWidget(chrome_label)
    form_layout.addLayout(chrome_layout)
    
    # Dropdown for screen selection
    screen_label = QLabel("Seleccionar Pantalla")
    screen_label.setFont(QFont('Arial', 14))
    screen_dropdown = QComboBox()
    screen_dropdown.setFont(QFont('Arial', 12))
    screens = get_screens()
    for screen in screens:
        screen_dropdown.addItem(screen)
    form_layout.addWidget(screen_label)
    form_layout.addWidget(screen_dropdown)
    
    layout.addLayout(form_layout)
    
    # Botón para guardar los enlaces configurados
    save_button = QPushButton("Guardar")
    apply_button_style(save_button)  # Apply the common style
    save_button.setFont(QFont('Arial', 14))
    save_button.setFixedHeight(40)
    save_button.clicked.connect(lambda: save_config(gpm_api_url.text(), adspower_api_url.text(), chrome_profiles_path.text(), screen_dropdown.currentText()))

    # Spacer to push the button to the bottom
    layout.addStretch()
    layout.addWidget(save_button)
    
    return page

def create_payment_page():
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(40)
    layout.setAlignment(Qt.AlignTop)  # Ensure the layout starts from the top
    
    title_label = QLabel('Billing')
    title_label.setAlignment(Qt.AlignCenter)
    title_label.setFont(QFont('Arial', 24, QFont.Bold))
    layout.addWidget(title_label)
    
    # Create a table to display the billing information
    billing_table = QTableWidget()
    billing_table.setColumnCount(3)
    billing_table.setHorizontalHeaderLabels(["Date", "Amount", "Status"])
    billing_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    billing_table.setShowGrid(False)
    billing_table.setAlternatingRowColors(True)
    billing_table.setStyleSheet("""
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
    
    layout.addWidget(billing_table)
    
    return page

def get_screens():
    screens = []
    for screen in QApplication.screens():
        screens.append(screen.name())
    return screens

def save_config(gpm_url, adspower_url, chrome_path, screen):
    ConfigManager.set_gpm_url(gpm_url)
    ConfigManager.set_ads_url(adspower_url)
    ConfigManager.set_chrome_path(chrome_path)
    screen_number = ''.join(filter(str.isdigit, screen))
    config = {
        "gpm_url": gpm_url,
        "adspower_url": adspower_url,
        "chrome_path": chrome_path,
        "screen_index": screen_number
    }
    config_path = resource_path("ui//JSON_FILE//config.json")
    with open(config_path, 'w') as config_file:
        json.dump(config, config_file, indent=4)
    print("Configuración guardada con éxito.")

def show_help_video():
    # Crea una ventana flotante pequeña para mostrar el video de YouTube
    video_dialog = QDialog()
    video_dialog.setWindowTitle("Video Tutorial")
    video_dialog.setFixedSize(960, 540)  # Tamaño de la ventana flotante
    
    # Crear un widget de navegador web para mostrar el video
    web_view = QWebEngineView()
    video_url = "https://www.youtube.com/embed/t0Ssz6AsEfs"  # URL del video en YouTube (modo embebido)
    web_view.setUrl(QUrl(video_url))
    
    # Layout para el video
    layout = QVBoxLayout()
    layout.addWidget(web_view)
    video_dialog.setLayout(layout)

    # Mostrar el dialogo de video
    video_dialog.exec_()