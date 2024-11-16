from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QInputDialog, QMessageBox, QDesktopWidget, QApplication)
from PyQt5.QtCore import Qt
from ui.components import create_sidebar, create_profile_button
from ui.pages import (create_home_page, create_telegram_tools_page, create_settings_page, load_profiles_from_api, create_twitter_tools_page, create_payment_page)
from ui.AppTheme import apply_theme
from ui.Sonic.SonicPage import SonicPage
from ui.Blum.BlumPage import BlumPage
from ui.FarmeosTelegram.Pawns.PawnsPage import PawnsPage
from ui.FarmeosTelegram.TronKeeper.TronKeeperPage import TronKeeperPage
from ui.Imx.ImxPage import ImxPage
from ui.Wallets.Metamask import MetamaskWindow
from ui.Wallets.Rabby import RabbyWindow
from ui.Wallets.Phantom import PhantomWindow
from ui.Wallets.TonKeeper import TonKeeperWindow
from ui.WolfGame.WolfPage import WolfGamePage
from ui.Wow.WowPage import WowPage
from ui.Wallets.Ronin import RoninWindow
from ui.PaymentPage.PayPage import PayPage
from ui.key_manager import KeyManager
from datetime import datetime

class AdministradorPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Administrador Principal')
        self.center_and_resize()
        self.is_dark_mode = True
        self.init_pages()  # Inicializamos las páginas primero
        self.initUI()
        self.check_version()  # Verificar la versión al iniciar

    def center_and_resize(self):
        screen = QDesktopWidget().screenGeometry()
        width = int(screen.width() * 0.75)
        height = int(screen.height() * 0.8)
        left = int((screen.width() - width) / 2)
        top = int((screen.height() - height) / 2)
        self.setGeometry(left, top, width, height)

    def initUI(self):
        # Main central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(30)

        # Sidebar on the left with logo and menu options
        self.sidebar = create_sidebar(self, self.home_page, self.blum_airdrop_page, self.wow_page, self.Pawns_page, 
                                      self.tronkeeper_page, self.sonic_airdrop_page, self.imx_airdrop_page, self.wolfgame_page,
                                      self.Metamask_page, self.Rabby_page, self.Phantom_page, self.TonKeeper_page, 
                                      self.Ronin_page, self.telegram_tools_page, self.twitter_tools_page, self.payment_page, self.settings_page)
        main_layout.addWidget(self.sidebar)

        # Create the main vertical layout for content and top bar
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(30)

        # Top bar layout containing the profile button on the right
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(10, 10, 10, 10)
        top_layout.addStretch()  # Add space to push profile button to the right

        # Profile button in the top-right corner
        self.profile_button = create_profile_button(self)
        self.profile_button.setStyleSheet("position: absolute; top: 10px; right: 10px;")
        top_layout.addWidget(self.profile_button)

        # Add top bar layout to the main right layout
        right_layout.addLayout(top_layout)

        # Content area below the top bar
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)  # Add margin to separate from sidebar and top
        content_layout.setSpacing(30)

        # Main content (e.g., dashboard content) in the center
        content_layout.addWidget(self.stack_widget, stretch=0)
    
        # Add the content layout to the right main layout
        right_layout.addLayout(content_layout)

        # Add the right layout (top bar + content) to the main layout
        main_layout.addLayout(right_layout, stretch=2)

        # Apply initial theme
        self.apply_theme()
    
    def init_pages(self):
        self.stack_widget = QStackedWidget()
        self.home_page = create_home_page(self)
        self.Rabby_page = RabbyWindow(self)
        self.Metamask_page = MetamaskWindow(self)
        self.Phantom_page = PhantomWindow(self)
        self.TonKeeper_page = TonKeeperWindow(self)
        self.Ronin_page = RoninWindow(self)
        self.telegram_tools_page = create_telegram_tools_page()
        self.twitter_tools_page = create_twitter_tools_page()
        self.sonic_airdrop_page = SonicPage(self)
        self.blum_airdrop_page = BlumPage(self)
        self.imx_airdrop_page = ImxPage(self)
        self.wolfgame_page = WolfGamePage(self)
        self.wow_page = WowPage(self)
        self.Pawns_page = PawnsPage(self)
        self.tronkeeper_page = TronKeeperPage(self)
        self.payment_page = PayPage(self)
        self.settings_page = create_settings_page()

        self.stack_widget.addWidget(self.home_page)
        self.stack_widget.addWidget(self.Rabby_page)
        self.stack_widget.addWidget(self.Metamask_page)
        self.stack_widget.addWidget(self.Phantom_page)
        self.stack_widget.addWidget(self.TonKeeper_page)
        self.stack_widget.addWidget(self.Ronin_page)
        self.stack_widget.addWidget(self.telegram_tools_page)
        self.stack_widget.addWidget(self.twitter_tools_page)
        self.stack_widget.addWidget(self.sonic_airdrop_page)
        self.stack_widget.addWidget(self.wolfgame_page)
        self.stack_widget.addWidget(self.wow_page)
        self.stack_widget.addWidget(self.blum_airdrop_page)
        self.stack_widget.addWidget(self.Pawns_page)
        self.stack_widget.addWidget(self.tronkeeper_page)
        self.stack_widget.addWidget(self.imx_airdrop_page)
        self.stack_widget.addWidget(self.payment_page)      
        self.stack_widget.addWidget(self.settings_page)

    def show_page(self, page):
        self.stack_widget.setCurrentWidget(page)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def apply_theme(self):
        apply_theme(self)
    
    def load_profiles_from_api(self, source, profile_table):
        load_profiles_from_api(self, source, profile_table)

    def check_version(self):
        key, ok = QInputDialog.getText(self, 'Ingresar Key', 'Ingrese su key:')
        if ok and key:
            valid, expiration_date = KeyManager.validate_key(key)
            if valid:
                days_left = (expiration_date - datetime.now()).days
                QMessageBox.information(self, 'Key válida', f'Key válida. Días restantes: {days_left}')
                self.set_version(key)
            else:
                QMessageBox.warning(self, 'Key inválida', 'La key ingresada es inválida o ha expirado.')
                QApplication.quit()  # Cerrar la aplicación si la clave es inválida o ha expirado
        else:
            self.close()  # Cerrar la aplicación si no se ingresa una clave

    def set_version(self, key):
        if key == 'free_key':
            self.version = 'free'
            self.disable_farming_buttons()
        elif key.startswith('medium_key'):
            self.version = 'medium'
            self.enable_limited_features()
        elif key.startswith('vip_key'):
            self.version = 'vip'
            self.enable_all_features()

    def disable_farming_buttons(self):
        # Deshabilitar botones de farmeo y evitar abrir páginas específicas
        for page in [self.sonic_airdrop_page, self.blum_airdrop_page, self.imx_airdrop_page, self.wolfgame_page, self.Pawns_page, self.tronkeeper_page,
                     self.telegram_tools_page, self.twitter_tools_page, self.Metamask_page, self.Rabby_page, self.Phantom_page, self.TonKeeper_page, self.Ronin_page, 
                     self.wow_page]:
            page.setDisabled(True)
        self.payment_page.setEnabled(True)
        self.settings_page.setEnabled(True)

    def enable_limited_features(self):
        # Habilitar solo 2 herramientas: Twitter y Telegram
        self.twitter_tools_page.setEnabled(True)
        self.telegram_tools_page.setEnabled(True)
        
        # Deshabilitar otras herramientas
        self.Metamask_page.setDisabled(True)
        self.Rabby_page.setDisabled(True)
        self.Phantom_page.setDisabled(True)
        self.TonKeeper_page.setDisabled(True)
        self.Ronin_page.setDisabled(True)

        # Habilitar solo el farmeo de Telegram
        self.blum_airdrop_page.setEnabled(True)
        self.Pawns_page.setEnabled(True)
        self.wow_page.setEnabled(True)
        self.tronkeeper_page.setEnabled(True)
        
        # Deshabilitar otros farmeos
        self.sonic_airdrop_page.setDisabled(True)
        self.imx_airdrop_page.setDisabled(True)
        self.wolfgame_page.setDisabled(True)
        self.wow_page.setDisabled(True)

    def enable_all_features(self):
        # Habilitar todas las características
        self.sidebar.setEnabled(True)
        for page in [self.sonic_airdrop_page, self.blum_airdrop_page, self.imx_airdrop_page, self.wolfgame_page, self.Pawns_page, self.tronkeeper_page,
                     self.telegram_tools_page, self.twitter_tools_page, self.Metamask_page, self.Rabby_page, self.Phantom_page, self.TonKeeper_page, self.Ronin_page, 
                     self.wow_page]:
            page.setEnabled(True)