from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel

class LogWindow(QDialog):
    def __init__(self, profile_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Log for Profile {profile_id}")
        layout = QVBoxLayout()
        log_label = QLabel(f"Logs for profile {profile_id} will be displayed here.")
        layout.addWidget(log_label)
        self.setLayout(layout)