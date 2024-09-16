from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QPalette, QIcon, QPixmap
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

        background = QPixmap("src/assets/images/splash_background.jpg")
        self.setFixedSize(background.width(), background.height())

        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(background))
        self.setPalette(palette)

        # Tạo overlay tối màu nhưng vẫn trong suốt
        overlay = QWidget(self)
        overlay.setStyleSheet("background-color: rgba(0, 0, 0, 100);")
        overlay.setFixedSize(self.size())

        layout = QVBoxLayout(overlay)
        layout.setContentsMargins(20, 20, 20, 20)

        # Tạo một frame để chứa các widget
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background-color: rgba(30, 30, 30, 200);
                border-radius: 10px;
            }
        """
        )
        frame_layout = QVBoxLayout(frame)

        self.language_dropdown = QComboBox()
        for code, lang_info in lang_code.items():
            icon = QIcon(lang_info["icon"])
            self.language_dropdown.addItem(icon, lang_info["name"], code)
        self.language_dropdown.currentIndexChanged.connect(self.switch_language)
        self.language_dropdown.setStyleSheet(
            """
            QComboBox {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #3a3a3a;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(src/assets/images/dropdown_arrow.png);
                width: 12px;
                height: 12px;
            }
        """
        )
        frame_layout.addWidget(self.language_dropdown)

        self.status_label = QLabel(self.messages.loading_app)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: white; font-size: 16px;")
        frame_layout.addWidget(self.status_label)

        self.start_button = QPushButton(self.messages.open_app)
        self.start_button.clicked.connect(self.ready_signal.emit)
        self.start_button.hide()
        self.start_button.setStyleSheet(
            """
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """
        )
        frame_layout.addWidget(self.start_button)

        layout.addWidget(frame)

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
