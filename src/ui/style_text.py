from PyQt5.QtWidgets import QLineEdit

def apply_text_input_style(widget: QLineEdit):
    widget.setStyleSheet("""
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