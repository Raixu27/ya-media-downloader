from PySide6.QtWidgets import (QApplication, QMainWindow, QLineEdit, QPushButton, QFormLayout, QVBoxLayout, QWidget,
                               QLabel, QMessageBox, QComboBox, QProgressBar, QListWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import (QIcon, QPixmap)
import constants


class MainWindow(QMainWindow):
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
        self.form_layout = QFormLayout()
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
        self.quality_combo.addItems(
            ["UHD (2160p)", "QHD (1440p)", "FHD (1080p)", "HD (720p)", "480p", "360p", "240p", "144p"])
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

        # | -- Progress bar -- | #
        self.download_progress_bar = QProgressBar()
        self.download_progress_bar.setMinimum(0)
        self.download_progress_bar.setMaximum(100)
        self.download_progress_bar.setValue(0)

        self.form_layout.addRow(self.download_progress_bar)

        # | -- Download button -- | #

        self.download_button = QPushButton("Download items")
        self.main_layout.addWidget(self.download_button)

        # | -- Menu bar -- | #
        self.menu_bar = self.menuBar()

        self.file_menu = self.menu_bar.addMenu("File")
        self.import_url_list = self.file_menu.addAction("Import URL list")
        self.export_url_list = self.file_menu.addAction("Export URL list")
        self.file_exit = self.file_menu.addAction("Exit")

        self.file_exit.triggered.connect(self.close)

        self.help_menu = self.menu_bar.addMenu("Help")
        self.about_action = self.help_menu.addAction("About")

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def show_info(self, message):
        QMessageBox.information(self, "Information", message)

    def update_progress_bar(self, value):
        self.download_progress_bar.setValue(value)

    def closeEvent(self, event):
        for window in QApplication.topLevelWidgets():
            window.close()
        event.accept()


class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'About {constants.APP_NAME}')
        self.setWindowIcon(QIcon('assets/icon.png'))
        self.setFixedSize(500, 250)
        self.w = None

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.app_icon_label = QLabel(self)
        self.app_icon_label.setFixedSize(80, 80)
        self.app_icon_label.setScaledContents(True)
        self.app_icon_pixmap = QPixmap('assets/icon.png')
        self.app_icon_label.setPixmap(self.app_icon_pixmap)
        self.main_layout.addWidget(self.app_icon_label,
                                   alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.app_name_label = QLabel(constants.APP_NAME)
        self.main_layout.addWidget(self.app_name_label)

        self.app_version_label = QLabel(f"Version {constants.APP_VERSION}")
        self.main_layout.addWidget(self.app_version_label)

        self.app_description_label = QLabel(
            "A stupid, simple Pyside6 app that downloads videos from websites\nwith quality and file format settings using yt-dlp.")
        self.main_layout.addWidget(self.app_description_label)

        self.github_button = QPushButton("View on GitHub")
        self.main_layout.addWidget(self.github_button)

        self.github_releases_button = QPushButton("View releases on GitHub")
        self.main_layout.addWidget(self.github_releases_button)