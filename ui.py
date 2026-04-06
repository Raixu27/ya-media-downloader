# | ---- Imports ---- | #

import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QLineEdit, QPushButton, QFormLayout, QVBoxLayout, QWidget, QLabel, QFileDialog, QMessageBox, QComboBox, QProgressBar, QListWidget, QScrollArea)
from PySide6.QtCore import (QThread, Qt)
from PySide6.QtGui import (QIcon)
import constants

# | ---- Classes ---- | #

class MainWindow(QMainWindow):
    """The main window obviously..."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'{constants.APP_NAME} {constants.APP_VERSION}')
        self.setWindowIcon(QIcon('assets/icon.png'))
        self.resize(800, 600)
        self.w = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # | -- Layouts -- | #

        self.main_layout = QVBoxLayout(self.central_widget)
        self.central_widget.setLayout(self.main_layout)

        self.form_layout = QFormLayout(self.central_widget)

        self.main_layout.addLayout(self.form_layout)

        # | -- URL Editor -- | #

        self.url_editor = QLineEdit()
        self.url_editor.setPlaceholderText("Input URL here...")

        self.url_button = QPushButton("Add URL")

        self.form_layout.addRow(self.url_button, self.url_editor)

        # | -- Browse directory -- | #

        self.output_label = QLabel("No output directory set!")

        self.browse_button = QPushButton("Browse")

        self.form_layout.addRow(self.browse_button, self.output_label)

        # | -- Video quality -- | #

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["UHD (2160p)", "QHD (1440p)", "FHD (1080p)", "HD (720p)", "480p", "360p", "240p", "144p"])
        self.quality_combo.setCurrentIndex(2)

        self.quality_info_label = QLabel("Video quality")

        self.form_layout.addRow(self.quality_info_label)
        self.form_layout.addRow(self.quality_combo)

        # | -- File format -- | #

        self.file_format_combo = QComboBox()
        self.file_format_combo.addItems([".mp4", ".mkv", ".webm", ".gif", ".mp3", ".wav", ".opus", ".ogg", ".flac"])

        self.file_format_info_label = QLabel("File format")

        self.form_layout.addRow(self.file_format_info_label)
        self.form_layout.addRow(self.file_format_combo)

        # | -- Video list -- | #

        self.items_label = QLabel("0 items added")
        self.form_layout.addRow(self.items_label)

        self.item_list = QListWidget()
        self.form_layout.addRow(self.item_list)

        def add_label_to_scroller(label) -> None:
            self.item_scrolling_layout.addWidget(label)

        # | -- Progress bar -- | #
        self.download_progress_bar = QProgressBar()
        self.download_progress_bar.setMinimum(0)
        self.download_progress_bar.setMaximum(100)
        self.download_progress_bar.setValue(0)

        self.form_layout.addRow(self.download_progress_bar)

        # | Download button -- | #

        self.download_button = QPushButton("Download items")
        self.main_layout.addWidget(self.download_button)

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
    
    def show_info(self, message):
        QMessageBox.information(self, "Information", message)
    
    def update_progress_bar(self, value):
        self.download_progress_bar.setValue(value)