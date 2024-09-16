from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette, QIcon
from .languages import get_messages, lang_code


class SplashScreen(QWidget):
    ready_signal = pyqtSignal()
    language_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.current_lang = "vi"
        self.messages = get_messages(self.current_lang)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.messages.splash_screen_title)
        self.setFixedSize(400, 300)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(128, 128, 128))
        self.setPalette(palette)

        layout = QVBoxLayout()

        self.language_dropdown = QComboBox()
        for code, lang_info in lang_code.items():
            icon = QIcon(lang_info["icon"])
            self.language_dropdown.addItem(icon, lang_info["name"], code)
        self.language_dropdown.currentIndexChanged.connect(self.switch_language)
        layout.addWidget(self.language_dropdown)

        self.status_label = QLabel(self.messages.loading_app)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.start_button = QPushButton(self.messages.open_app)
        self.start_button.clicked.connect(self.ready_signal.emit)
        self.start_button.hide()
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def switch_language(self):
        self.current_lang = self.language_dropdown.currentData()
        self.messages = get_messages(self.current_lang)
        self.updateUI()
        self.language_changed.emit(self.current_lang)

    def updateUI(self):
        self.setWindowTitle(self.messages.splash_screen_title)
        self.status_label.setText(self.messages.loading_app)
        self.status_label.setText(self.messages.ready_to_start)
        self.start_button.setText(self.messages.open_app)

    def show_start_button(self):
        self.status_label.setText(self.messages.ready_to_start)
        self.start_button.show()
