from PyQt5.QtWidgets import QLineEdit, QTextEdit

def apply_text_input_style(widget):
    widget.setStyleSheet("""
        QLineEdit, QTextEdit {
            background-color: #2C3E50;
            color: white;
            border: 2px solid #2C3E50;
            padding: 5px;
            border-radius: 5px;
        }
        QLineEdit:focus, QTextEdit:focus {
            border: 2px solid #0984e3;
        }
    """)
    
def apply_button_style(widget):
    widget.setStyleSheet("""
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
    
def apply_button_grey_style(widget):
    widget.setStyleSheet("""
        QPushButton {
            background-color: darkgray;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #74b9ff;
        }
    """)