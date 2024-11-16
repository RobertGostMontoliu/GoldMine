from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget,
    QHeaderView, QHBoxLayout, QRadioButton, QButtonGroup, QComboBox, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class PayPage(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.setup_ui()
    
    def setup_ui(self):
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignTop)
        
        # Title
        title_label = QLabel('Payment Page')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Arial', 24, QFont.Bold))
        layout.addWidget(title_label)
        
        # Subscription Options
        subscription_layout = QVBoxLayout()
        subscription_layout.setSpacing(10)
        subscription_title = QLabel('Subscription Options:')
        subscription_title.setFont(QFont('Arial', 18, QFont.Bold))
        subscription_layout.addWidget(subscription_title)
        
        self.radio_group = QButtonGroup(self)
        
        # Option 1: Free 30 Days
        free_option = QRadioButton('Free for 30 Days')
        self.radio_group.addButton(free_option, 1)
        subscription_layout.addWidget(free_option)
        
        # Option 2: 49.99 USDT/Month
        subscription_option = QRadioButton('49.99 USDT / Month')
        self.radio_group.addButton(subscription_option, 2)
        subscription_layout.addWidget(subscription_option)
        
        # Option 3: Purchase a Script
        script_option = QRadioButton('Purchase a Script')
        self.radio_group.addButton(script_option, 3)
        subscription_layout.addWidget(script_option)
        
        # Script List
        self.script_dropdown = QComboBox(self)
        self.script_dropdown.addItem('Select a Script', 0)
        self.script_dropdown.addItem('Metamask Script - 5 USDT', 5)
        self.script_dropdown.addItem('Blum Script - 10 USDT', 10)
        self.script_dropdown.setVisible(False)
        subscription_layout.addWidget(self.script_dropdown)
        
        layout.addLayout(subscription_layout)
        
        # Show Script Dropdown when "Purchase a Script" is selected
        script_option.toggled.connect(lambda: self.script_dropdown.setVisible(script_option.isChecked()))
        
        # Wallet Address
        wallet_label = QLabel('Wallet Address:')
        wallet_label.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(wallet_label)
        
        wallet_address = QLineEdit('8EzLaEtJA1VSddeci63oRJkbLDJ8cqPdLHb87HiE2yPF')
        wallet_address.setReadOnly(True)
        wallet_address.setStyleSheet("background-color: #f0f0f0; color: black;")
        layout.addWidget(wallet_address)
        
        # Payment Verification
        payment_layout = QHBoxLayout()
        payment_layout.setSpacing(10)
        
        verification_label = QLabel('Transaction Hash:')
        verification_label.setFont(QFont('Arial', 12))
        payment_layout.addWidget(verification_label)
        
        self.transaction_hash_input = QLineEdit(self)
        payment_layout.addWidget(self.transaction_hash_input)
        
        self.verify_button = QPushButton('Verify Payment')
        self.verify_button.setEnabled(False)
        self.verify_button.clicked.connect(self.verify_payment)
        payment_layout.addWidget(self.verify_button)
        
        layout.addLayout(payment_layout)
        
        # Key Display
        key_layout = QHBoxLayout()
        key_layout.setSpacing(10)
        
        key_label = QLabel('Your Key:')
        key_label.setFont(QFont('Arial', 12))
        key_layout.addWidget(key_label)
        
        self.key_display = QLineEdit(self)
        self.key_display.setReadOnly(True)
        key_layout.addWidget(self.key_display)
        
        layout.addLayout(key_layout)
        
        # Enable Verification Button only if Transaction Hash is entered
        self.transaction_hash_input.textChanged.connect(
            lambda: self.verify_button.setEnabled(bool(self.transaction_hash_input.text()))
        )
    
    def verify_payment(self):
        # Mock payment validation
        selected_option = self.radio_group.checkedId()
        amount_required = 0
        
        if selected_option == 1:  # Free Option
            amount_required = 0
        elif selected_option == 2:  # Subscription
            amount_required = 49.99
        elif selected_option == 3:  # Script Purchase
            amount_required = self.script_dropdown.currentData()
        
        if not amount_required:
            QMessageBox.warning(self, "Error", "Please select a valid option.")
            return
        
        # Mock: Check transaction hash validity and amount (replace with actual blockchain validation)
        if self.transaction_hash_input.text() and amount_required > 0:
            QMessageBox.information(self, "Success", "Payment verified successfully!")
            self.key_display.setText(self.generate_key(selected_option, amount_required))
            self.verify_button.setStyleSheet("background-color: green; color: white;")
        else:
            QMessageBox.warning(self, "Error", "Payment verification failed!")
    
    def generate_key(self, option, amount):
        # Generate a simple key (can be replaced with actual logic)
        from uuid import uuid4
        if option == 1:
            return f"FREE-{uuid4().hex[:8]}"
        elif option == 2:
            return f"NORMAL-{uuid4().hex[:8]}"
        elif option == 3:
            return f"SCRIPT-{amount}-{uuid4().hex[:8]}"


# For testing the widget standalone
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = PayPage()
    window.setWindowTitle("PayPage")
    window.show()
    sys.exit(app.exec_())
