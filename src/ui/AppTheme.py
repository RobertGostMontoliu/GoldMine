import json
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

def apply_theme(window):
    palette = QPalette()
    if window.is_dark_mode:
        # Configuración para el tema oscuro
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        
        window.setStyleSheet("""
            QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }
            QWidget { background-color: #353535; color: #ffffff; }
            QPushButton { background-color: #2a82da; color: #ffffff; }
            QPushButton:hover { background-color: #2a82da; }
            QLineEdit { background-color: #252525; color: #ffffff; }
            QTextEdit { background-color: #252525; color: #ffffff; }
            QTableWidget { gridline-color: #5a5a5a; }
            QHeaderView::section { background-color: #252525; color: #ffffff; }
            QTableWidget { alternate-background-color: #3a3a3a; }
        """)
    else:
        # Configuración para el tema claro con gris al 50%
        gray_50 = QColor(127, 127, 127)
        gray_70 = QColor(179, 179, 179)
        gray_90 = QColor(230, 230, 230)
        
        palette.setColor(QPalette.Window, gray_50)
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, gray_70)
        palette.setColor(QPalette.AlternateBase, gray_90)
        palette.setColor(QPalette.ToolTipBase, gray_70)
        palette.setColor(QPalette.ToolTipText, Qt.black)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, gray_50)
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(0, 0, 255))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        
        window.setStyleSheet("""
            QToolTip { color: #000000; background-color: #9c9c9c; border: 1px solid black; }
            QWidget { background-color: #7f7f7f; color: #000000; }
            QPushButton { background-color: #7f7f7f; color: #000000; }
            QPushButton:hover { background-color: #6f6f6f; }
            QLineEdit { background-color: #9c9c9c; color: #000000; }
            QTextEdit { background-color: #9c9c9c; color: #000000; }
            QTableWidget { gridline-color: #c0c0c0; }
            QHeaderView::section { background-color: #7f7f7f; color: #000000; }
            QTableWidget { alternate-background-color: #bfbfbf; }
        """)
    
    window.setPalette(palette)