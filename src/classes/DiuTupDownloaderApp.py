# -*- coding: utf-8 -*-
import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QProgressBar,
    QMessageBox,
    QTextEdit,
    QRadioButton,
)
from PyQt6.QtGui import QFont
from .Utils import Utils
from .DownloaderThread import DownloaderThread
from .languages import get_messages


class DiuTupDownloaderApp(QWidget):
    def __init__(self, messages, splash_screen):
        super().__init__()
        self.messages = messages
        self.splash_screen = splash_screen
        self.splash_screen.language_changed.connect(self.update_language)
        self.download_dir = str(Utils.get_download_dir())
        self.ffmpeg_path = self.find_ffmpeg()
        self.initUI()
        self.downloader = None
        self.is_paused = False
        self.center()

    def check_dependencies(self):
        self.ffmpeg_path = self.find_ffmpeg()
        return True

    def initUI(self):
        self.setWindowTitle(self.messages.app_name)
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        url_layout = QHBoxLayout()
        logs_layout = QHBoxLayout()
        self.exit_button = QPushButton(self.messages.exit_button)
        self.exit_button.clicked.connect(self.close)
        layout.addWidget(self.exit_button)
        self.download_location_label = QLabel(
            self.messages.download_location_label(self.download_dir)
        )
        self.download_location_label.setWordWrap(True)
        layout.addWidget(self.download_location_label)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(self.messages.url_input_placeholder)
        url_layout.addWidget(self.url_input)
        self.clear_button = QPushButton(self.messages.clear_button)
        self.clear_button.clicked.connect(self.clear_url)
        url_layout.addWidget(self.clear_button)
        layout.addLayout(url_layout)
        radio_layout = QHBoxLayout()
        self.audio_only_radio = QRadioButton(self.messages.radio_audio_only)
        self.audio_only_radio.setChecked(True)
        radio_layout.addWidget(self.audio_only_radio)
        self.video_radio = QRadioButton(self.messages.radio_video)
        radio_layout.addWidget(self.video_radio)
        layout.addLayout(radio_layout)
        self.status_label = QLabel(self.messages.instruction)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        self.url_input.textChanged.connect(self.check_url_input)
        self.playlist_progress_label = QLabel("")
        self.playlist_progress_label.setWordWrap(True)
        layout.addWidget(self.playlist_progress_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        self.logs_label = QLabel(self.messages.logs_label)
        logs_layout.addWidget(self.logs_label)
        self.copy_button = QPushButton(self.messages.copy_button)
        self.copy_button.clicked.connect(self.copy_logs)
        self.copy_button.setFixedWidth(80)
        logs_layout.addWidget(self.copy_button)
        logs_layout.addStretch()
        layout.addLayout(logs_layout)
        self.logs_area = QTextEdit()
        self.logs_area.setReadOnly(True)
        self.logs_area.setFixedHeight(100)
        layout.addWidget(self.logs_area)
        self.start_button = QPushButton(self.messages.start_button)
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_download)
        start_font = QFont()
        start_font.setPointSize(self.font().pointSize() + 2)
        start_font.setBold(True)
        self.start_button.setFont(start_font)
        button_layout.addWidget(self.start_button)
        self.pause_button = QPushButton(self.messages.pause_button)
        self.pause_button.clicked.connect(self.pause_download)
        self.pause_button.hide()
        button_layout.addWidget(self.pause_button)
        self.continue_button = QPushButton(self.messages.continue_button)
        self.continue_button.clicked.connect(self.continue_download)
        self.continue_button.hide()
        continue_font = QFont()
        continue_font.setPointSize(14)
        continue_font.setBold(True)
        self.continue_button.setFont(continue_font)
        self.continue_button.setMinimumSize(150, 50)
        button_layout.addWidget(self.continue_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def center(self):
        qr = self.frameGeometry()
        screen = QApplication.primaryScreen()
        if screen is not None:
            screen_geometry = screen.geometry()
            cp = screen_geometry.center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())

    def check_url_input(self):
        url = self.url_input.text().strip()
        if url:
            self.status_label.setText(self.messages.check_url_input_ok)
            self.start_button.setEnabled(True)
        else:
            self.status_label.setText(self.messages.instruction)
            self.start_button.setEnabled(False)

    def find_ffmpeg(self):
        is_ffmpeg_vendors_exists, ffmpeg_vendors_path = Utils.check_ffmpeg()
        if not is_ffmpeg_vendors_exists:
            ffmpeg_vendors_path.mkdir(parents=True, exist_ok=True)
        ffmpeg_path = Utils.get_base_path(path="src/vendors/ffmpeg/ffmpeg")
        if sys.platform == "win32":
            ffmpeg_path += ".exe"
        if os.path.exists(ffmpeg_path):
            return ffmpeg_path
        else:
            return None

    def start_download(self):
        if not self.ffmpeg_path:
            self.set_status(self.messages.ffmpeg_warning_message)
            return
        url = self.url_input.text().strip()
        if (not url) and ("youtube.com" not in url) and ("youtu.be" not in url):
            # TODO: support shortened link youtu.be
            self.set_status(self.messages.invalid_url_message)
            return
        self.url_input.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.downloader = DownloaderThread(
            url=url, ffmpeg_path=self.ffmpeg_path, messages=self.messages, app=self
        )
        self.downloader.progress.connect(self.update_progress)
        self.downloader.playlist_progress.connect(self.update_playlist_progress)
        self.downloader.finished.connect(self.download_finished)
        self.downloader.error.connect(self.download_error)
        self.downloader.start()
        self.start_button.hide()
        self.pause_button.show()
        self.progress_bar.show()
        self.playlist_progress_label.show()
        self.set_status(self.messages.scanning_videos)
        self.is_paused = False

    def pause_download(self):
        if self.downloader and self.downloader.isRunning():
            self.downloader.cancel()
            self.set_status(self.messages.pause_download_message)
            self.start_button.setEnabled(False)
            self.pause_button.hide()
            self.continue_button.show()
            self.progress_bar.hide()
            self.is_paused = True

    def continue_download(self):
        if self.is_paused:
            self.start_download()
            self.continue_button.hide()
            self.pause_button.show()

    def update_progress(self, message):
        txt_playlist_progress = ""
        if self.downloader is not None:
            if self.downloader.playlists:
                txt_playlist_progress = f"[{self.downloader.current_playlist + 1}/{len(self.downloader.playlists)}]"
            progress = f"Playlist: {txt_playlist_progress} {self.downloader.current_playlist_name}"
            self.playlist_progress_label.setText(progress)
            self.set_status(message)
            self.logs_area.append(message)

    def update_playlist_progress(self, message):
        current_status = self.status_label.text()
        new_status = f"{message}\n{current_status}"
        self.status_label.setText(new_status)
        self.logs_area.append(message)

    # TODO: update hiển thị mess báo thành công khi tải xong cả kênh playlists
    def download_finished(self):
        if self.downloader is not None:
            total_videos = self.downloader.total_videos
            original_total_videos = self.downloader.original_total_videos
            private_videos = original_total_videos - total_videos
            private_detached_message = ""
            if private_videos > 0:
                private_detached_message = self.messages.detached_private_videos(
                    private_videos
                )
            finished_message = self.messages.finished_message(
                total_videos, original_total_videos, private_detached_message
            )
            self.set_status(finished_message)
            self.start_button.show()
            self.pause_button.hide()
            self.progress_bar.hide()
            self.playlist_progress_label.hide()
            self.is_paused = False
            self.url_input.setEnabled(True)
            self.clear_button.setEnabled(True)

    def download_error(self, error_message):
        if "ffprobe and ffmpeg not found" in error_message:
            self.set_status(self.messages.ffmpeg_error_message)
            QMessageBox.warning(
                self,
                self.messages.ffmpeg_error_title,
                self.messages.ffmpeg_error_message,
                QMessageBox.StandardButton.Ok,
            )
        else:
            self.set_status(f"{self.messages.error}: {error_message}")
        self.start_button.show()
        self.pause_button.hide()
        self.progress_bar.hide()
        self.is_paused = False
        self.url_input.setEnabled(True)

    def set_status(self, message):
        current_playlist_progress = (
            self.status_label.text().split("\n")[0]
            if "\n" in self.status_label.text()
            else ""
        )
        new_status = f"{current_playlist_progress}\n{message}"
        self.status_label.setText(new_status)
        self.logs_area.append(message)

    def clear_url(self):
        self.url_input.clear()

    def copy_logs(self):
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(self.logs_area.toPlainText())
            QMessageBox.information(
                self, self.messages.copy_logs_title, self.messages.copy_logs_message
            )

    def update_language(self, lang):
        self.messages = get_messages(lang)
        self.updateUI()

    def updateUI(self):
        self.setWindowTitle(self.messages.app_name)
        self.download_location_label.setText(
            self.messages.download_location_label(self.download_dir)
        )
        self.url_input.setPlaceholderText(self.messages.url_input_placeholder)
        self.clear_button.setText(self.messages.clear_button)
        self.status_label.setText(self.messages.instruction)
        self.logs_label.setText(self.messages.logs_label)
        self.copy_button.setText(self.messages.copy_button)
        self.start_button.setText(self.messages.start_button)
        self.pause_button.setText(self.messages.pause_button)
        self.continue_button.setText(self.messages.continue_button)
        self.exit_button.setText(self.messages.exit_button)
