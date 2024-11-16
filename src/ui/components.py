import os
from PyQt5.QtWidgets import (QMenu, QAction, QWidget, QVBoxLayout, QPushButton, QLabel, QToolButton, QFrame, QHBoxLayout, QTableWidget, QHeaderView, QInputDialog, QMessageBox)
from PyQt5.QtGui import QIcon, QPixmap, QCursor, QFont
from PyQt5.QtCore import Qt, QSize
import json
from ui.json_path import resource_path

CONFIG_FILE = resource_path("ui\\JSON_FILE\\config.json")

class ConfigManager:
    @staticmethod
    def load_config():
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {"gpm_url": "", "ads_url": "", "chrome_path": ""}

    @staticmethod
    def save_config(config_data):
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f)

    @staticmethod
    def set_gpm_url(url):
        config = ConfigManager.load_config()
        config["gpm_url"] = url
        ConfigManager.save_config(config)

    @staticmethod
    def set_ads_url(url):
        config = ConfigManager.load_config()
        config["ads_url"] = url
        ConfigManager.save_config(config)

    @staticmethod
    def set_chrome_path(path):
        config = ConfigManager.load_config()
        config["chrome_path"] = path
        ConfigManager.save_config(config)

    @staticmethod
    def get_gpm_url():
        config = ConfigManager.load_config()
        return config.get("gpm_url", "")

    @staticmethod
    def get_ads_url():
        config = ConfigManager.load_config()
        return config.get("ads_url", "")

    @staticmethod
    def get_chrome_path():
        config = ConfigManager.load_config()
        return config.get("chrome_path", "")

def create_sidebar(window, home_page, Blum_page, Wow_page, Pawns_page, TronKeeper_page, sonic_airdrop_page,
                   imx_airdrop_page, wolfgame_page, Metamask_page, Rabby_page, 
                   Phantom_page, TonKeeper_page, Ronin_page,  
                   telegram_tools_page, twitter_tools_page, settings_page):
    sidebar_widget = QWidget()
    sidebar_layout = QVBoxLayout(sidebar_widget)
    sidebar_layout.setContentsMargins(10, 10, 10, 10)

    # Logo
    logo_label = QLabel()
    logo_path = resource_path("ui\\media\\app_media\\logo.png")
    if os.path.exists(logo_path):
        logo_pixmap = QPixmap(logo_path)
        logo_label.setPixmap(logo_pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    else:
        logo_label.setText("Logo")
        logo_label.setAlignment(Qt.AlignCenter)
    
    sidebar_layout.addWidget(logo_label)
    sidebar_layout.addSpacing(0)

    # Function to create styled buttons
    def create_styled_button(text, page=None, callback=None, icon_path=None):
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #2C3E50;
                color: #ecf0f1;
                border: none;
                text-align: left;
                padding: 10px 10px;
                font-size: 17px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #34495E;
            }
        """)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        if icon_path:
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(24, 24))
        if callback:
            btn.clicked.connect(callback)
        elif page:
            btn.clicked.connect(lambda: window.show_page(page))
        return btn

    def create_styled_button2(text, page=None, callback=None, icon_path=None):
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #485f78;
                color: #ecf0f1;
                border: none;
                text-align: left;
                padding: 5px 5px;
                font-size: 13px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #34495E;
            }
        """)
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        if icon_path:
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(24, 24))
        if callback:
            btn.clicked.connect(callback)
        elif page:
            btn.clicked.connect(lambda: window.show_page(page))
        return btn

    # Category: General
    general_label = QLabel("🏠 General")
    general_label.setStyleSheet("font-weight: bold; color: #7F8C8D; padding: 5px 0;")
    sidebar_layout.addWidget(general_label)
    sidebar_layout.addWidget(create_styled_button("Dashboard", home_page, icon_path=resource_path("ui\\media\\app_media\\dashboard_logo.png")))
    sidebar_layout.addSpacing(10)

    # Category: Active Farms
    farmeos_label = QLabel("🌱 Farmeos activos")
    farmeos_label.setStyleSheet("font-weight: bold; color: #7F8C8D; padding: 5px 0;")
    sidebar_layout.addWidget(farmeos_label)
    
    # Toggle button for Telegram Farms
    telegram_farms_button = create_styled_button("Telegram Farms", None, icon_path=resource_path("ui\\media\\app_media\\Telegram_icon.png"))
    sidebar_layout.addWidget(telegram_farms_button)
    
    # Container for Telegram Farms sub-buttons
    telegram_farms_container = QWidget()
    telegram_farms_layout = QVBoxLayout(telegram_farms_container)
    telegram_farms_layout.setSpacing(5)
    telegram_farms_layout.setContentsMargins(20, 0, 0, 0)
    telegram_farms_container.setVisible(False)  # Initially hidden

    # Sub-buttons for Telegram Farms
    blum_btn = create_styled_button2("Blum", Blum_page, icon_path=resource_path("ui\\media\\app_media\\blum_logo.png"))
    Wow_btn = create_styled_button2("Wow", Wow_page, icon_path=resource_path("ui\\media\\app_media\\wow_logo.png"))
    pawns_btn = create_styled_button2("Pawns", Pawns_page, icon_path=resource_path("ui\\media\\app_media\\pawns_logo.png"))
    tronkeeper_btn = create_styled_button2("TronKeeper", TronKeeper_page, icon_path=resource_path("ui\\media\\app_media\\tronkeeper_logo.png"))

    telegram_farms_layout.addWidget(blum_btn)
    telegram_farms_layout.addWidget(Wow_btn)
    telegram_farms_layout.addWidget(pawns_btn)
    telegram_farms_layout.addWidget(tronkeeper_btn)

    sidebar_layout.addWidget(telegram_farms_container)

    # Toggle function for Telegram Farms
    def toggle_telegram_farms():
        telegram_farms_container.setVisible(not telegram_farms_container.isVisible())

    # Connect the toggle button to the function
    telegram_farms_button.clicked.connect(toggle_telegram_farms)
    
    # Other main options in the sidebar
    sidebar_layout.addWidget(create_styled_button("Sonic airdrop", sonic_airdrop_page, icon_path=resource_path("ui\\media\\app_media\\Sonic_logo.png")))
    sidebar_layout.addWidget(create_styled_button("IMX airdrop", imx_airdrop_page, icon_path=resource_path("ui\\media\\app_media\\IMX_logo.png")))
    sidebar_layout.addWidget(create_styled_button("Wolf Game", wolfgame_page, icon_path=resource_path("ui\\media\\app_media\\Wolf_logo.png")))
    sidebar_layout.addSpacing(10)

    # Category: Wallet Tools
    tools_label = QLabel("🛠️ Tools")
    tools_label.setStyleSheet("font-weight: bold; color: #7F8C8D; padding: 5px 0;")
    sidebar_layout.addWidget(tools_label)

    # Toggle button for Wallet Tools
    wallet_tools_button = create_styled_button("💼 Wallet tools", None, icon_path=resource_path("ui\\media\\app_media\\wallet_icon.png"))
    sidebar_layout.addWidget(wallet_tools_button)

    # Container for Wallet Tools sub-buttons
    wallet_tools_container = QWidget()
    wallet_tools_layout = QVBoxLayout(wallet_tools_container)
    wallet_tools_layout.setSpacing(5)
    wallet_tools_layout.setContentsMargins(20, 0, 0, 0)
    wallet_tools_container.setVisible(False)  # Initially hidden

    # Sub-buttons for Wallet Tools
    metamask_btn = create_styled_button2("Metamask", Metamask_page, icon_path=resource_path("ui\\media\\app_media\\metamask_icon.png"))
    rabby_btn = create_styled_button2("Rabby", Rabby_page, icon_path=resource_path("ui\\media\\app_media\\rabby_icon.png"))
    phantom_btn = create_styled_button2("Phantom", Phantom_page, icon_path=resource_path("ui\\media\\app_media\\solana_icon.png"))
    tonkeeper_btn = create_styled_button2("TonKeeper", TonKeeper_page, icon_path=resource_path("ui\\media\\app_media\\ton_icon.png"))
    ronin_btn = create_styled_button2("Ronin", Ronin_page, icon_path=resource_path("ui\\media\\app_media\\ronin_logo.png"))

    wallet_tools_layout.addWidget(metamask_btn)
    wallet_tools_layout.addWidget(rabby_btn)
    wallet_tools_layout.addWidget(phantom_btn)
    wallet_tools_layout.addWidget(tonkeeper_btn)
    wallet_tools_layout.addWidget(ronin_btn)

    sidebar_layout.addWidget(wallet_tools_container)

    # Toggle function for Wallet Tools
    def toggle_wallet_tools():
        wallet_tools_container.setVisible(not wallet_tools_container.isVisible())

    # Connect the toggle button to the function
    wallet_tools_button.clicked.connect(toggle_wallet_tools)

    # Other tools and settings
    sidebar_layout.addWidget(create_styled_button("Telegram tools", telegram_tools_page, icon_path=resource_path("ui\\media\\app_media\\Telegram_tools.png")))
    sidebar_layout.addWidget(create_styled_button("Twitter tools", twitter_tools_page, icon_path=resource_path("ui\\media\\app_media\\twitter_logo.png")))
    sidebar_layout.addSpacing(10)

    # Category: Settings
    otros_label = QLabel("🔧 Settings")
    otros_label.setStyleSheet("font-weight: bold; color: #7F8C8D; padding: 5px 0;")
    sidebar_layout.addWidget(otros_label)
    sidebar_layout.addWidget(create_styled_button("⚙️ Configuraciones", settings_page))

    sidebar_layout.addStretch(1)
    sidebar_widget.setFixedWidth(200)
    return sidebar_widget

def create_profile_button(window):
    profile_widget = QWidget(window)
    profile_layout = QHBoxLayout(profile_widget)
    profile_layout.setContentsMargins(0, 0, 10, 0)  # Añade un margen derecho

    # Botón de perfil
    profile_button = QToolButton()
    user_icon_path = resource_path("ui\\media\\app_media\\user_icon.png")
    if os.path.exists(user_icon_path):
        profile_button.setIcon(QIcon(user_icon_path))
    else:
        print(f"Error: No se pudo encontrar el archivo de icono de usuario en {user_icon_path}")
        profile_button.setText("👤")  # Emoji como fallback
    
    profile_button.setIconSize(QSize(50, 50))
    profile_button.setStyleSheet("""
        QToolButton {
            border: none;
            border-radius: 16px;
            padding: 5px;
            background-color: transparent;
        }
        QToolButton:hover {
            background-color: rgba(200, 200, 200, 50);
        }
    """)

    profile_menu = QMenu()
    profile_menu.setStyleSheet("""
        QMenu {
            background-color: #485f78;
            border: 1px solid #485f78;
            padding: 5px;
            font-size: 14px;
        }
        QMenu::item {
            padding: 5px 20px;
            border-radius: 3px;
            color: #ecf0f1;
        }
        QMenu::item:selected {
            background-color: #2980b9;
        }
    """)

    toggle_theme_action = QAction('Cambiar Tema', window)
    toggle_theme_action.triggered.connect(window.toggle_theme)
    profile_menu.addAction(toggle_theme_action)

    enter_key_action = QAction('Ingresar Key', window)
    profile_menu.addAction(enter_key_action)

    profile_button.setPopupMode(QToolButton.InstantPopup)
    profile_button.setMenu(profile_menu)

    # Agregar el botón de perfil al layout
    profile_layout.addWidget(profile_button)
    profile_widget.setFixedHeight(50)  # Ajusta la altura del widget

    return profile_widget

def create_horizontal_line():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    return line

def create_home_page(window):
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setAlignment(Qt.AlignTop)
    
    # Título
    welcome_label = QLabel('Dashboard - Perfiles')
    welcome_label.setAlignment(Qt.AlignCenter)
    welcome_label.setFont(QFont('Arial', 60, QFont.Bold))
    layout.setAlignment(Qt.AlignTop)
    layout.addWidget(welcome_label)

    # Tabla de perfiles
    profile_table = QTableWidget()
    profile_table.setColumnCount(3)  # Cambiamos a 2 columnas
    profile_table.setHorizontalHeaderLabels(["Nombre de Perfil", "ID del Perfil"])  # Actualizamos las etiquetas
    profile_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    layout.addWidget(profile_table)

    # Disable grid lines
    profile_table.setShowGrid(False)

    # Enable alternating row colors
    profile_table.setAlternatingRowColors(True)

    # Apply the custom stylesheet
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
            background-color: #2d3436;  /* Dark background for odd rows */
            color: #dfe6e9;
            border: none;
        }
        QTableWidget::item:alternate {
            background-color: #34495e;  /* Lighter background for even rows */
        }
        QTableCornerButton::section {
            background-color: #34495e;
            border: none;
        }
        QHeaderView::section:vertical {
            background-color: #2d3436;  /* Match header background */
            color: #ffffff;
            font-weight: bold;
            border: none;
        }
    """)

    # Center text in headers
    profile_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

    # Make rows resizable manually
    profile_table.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)

    layout.addWidget(profile_table)

    return page