# | ---- Imports ---- | #

import sys
import subprocess
from re import sub
from yt_dlp import YoutubeDL
from PySide6.QtWidgets import (QApplication, QMainWindow, QLineEdit, QPushButton, QFormLayout, QVBoxLayout, QWidget, QLabel, QFileDialog, QMessageBox, QComboBox, QProgressBar, QListWidget)
from PySide6.QtCore import QThread, QObject, Signal, Slot
import constants
import ui
import yt_dlp_wrapper

# | ---- Variables ---- | #

main_window = None
added_videos = {}
url = ""
output_directory = ""
video_quality = "1080"
file_format = "mp4"

# | ---- Classes ---- | #

class AddItem(QObject):
    """Adds an item to added_videos and adds it to the UI list."""
    finished = Signal()
    add_item_to_list = Signal(str)
    update_items_label = Signal(int)
    clear_item_list = Signal()
    error_message = Signal(str)
    info_message = Signal(str)
    update_progress_bar = Signal(int)

    @Slot()
    def run(self):
        global url, added_videos
        try:
            info = yt_dlp_wrapper.get_info(url)
        except:
            self.error_message.emit(f"The URL ({url}) couldn't be added. This could be caused by your IP being blocked by the website. Did you enter the correct URL?")
            self.finished.emit()
            return
        
        _id = yt_dlp_wrapper.get_id(info)

        print(_id)

        index = len(added_videos)
        added_videos[index] = info

        self.update_items_label.emit(len(added_videos))
        
        if yt_dlp_wrapper.is_playlist(info) == False:
            self.add_item_to_list.emit(f"{yt_dlp_wrapper.get_title(info)} — By {yt_dlp_wrapper.get_uploader_id(info)} — Type: Video")
            print(f"Added {yt_dlp_wrapper.get_title(info)} — By {yt_dlp_wrapper.get_uploader_id(info)} — Type: Video")
        elif yt_dlp_wrapper.is_playlist(info) == True:
            self.add_item_to_list.emit(f"{yt_dlp_wrapper.get_title(info)} — By {yt_dlp_wrapper.get_uploader_id(info)} — Type: Playlist")
            print(f"Added {yt_dlp_wrapper.get_title(info)} — By {yt_dlp_wrapper.get_uploader_id(info)} — Type: Playlist")

        self.clear_item_list.emit()
    
        self.finished.emit()

class DownloadItems(QObject):
    """Checks for potential errors then loops through added_videos and downloads them all with the selected options."""
    finished = Signal()
    add_item_to_list = Signal(str)
    update_items_label = Signal(int)
    clear_item_list = Signal()
    error_message = Signal(str)
    info_message = Signal(str)
    update_progress_bar = Signal(int)

    @Slot()
    def run(self):  
        global added_videos, output_directory, video_quality, file_format

        total_items = len(added_videos)
        downloaded_items = 0

        if total_items == 0:
            self.error_message.emit("You need to add videos before you try to download them.")
            self.finished.emit()
            return

        if output_directory == "":
            self.error_message.emit("No output directory was selected. Please select an output directory.")
            self.finished.emit()
            return

        if file_format == "gif" and (video_quality == "240" or video_quality == "144"):
            self.error_message.emit(".gif file format must be at least 360p. Please set your video quality to 360p or higher.")
            self.finished.emit()
            return

        for i in range(total_items):
            info = added_videos[i]
            _url = yt_dlp_wrapper.get_url(info)
            try:
                yt_dlp_wrapper.download_video(_url, output_directory, video_quality, file_format, main_window)
                downloaded_items += 1
            except:
                self.error_message.emit(f"{yt_dlp_wrapper.get_title(info)} couldn't be downloaded. This item will be skipped and the others will still attempt to download.")
            remove_item(i, True)
        self.clear_item_list.emit()
        self.update_progress_bar.emit(0)
        self.info_message.emit(f"{downloaded_items}/{total_items} downloaded successfully.")
        self.finished.emit()

# | ---- Functions ---- | #

def install_ffmpeg() -> None:
    """Hideous disgrace of a function that tries many package managers to install FFmpeg. Yikes!!!"""
    # Supports windows (winget), macOS (homebrew), arch linux (pacman), debian/ubuntu.. (apt), fedora.. (dnf), void (xbps-install), alpine (apk), openSUSE (zypper)
    try: # Windows
        subprocess.check_call(['winget', 'install', 'ffmpeg', '--accept-source-agreements', '--accept-package-agreements', '--disable-interactivity'])
        main_window.show_info("FFmpeg successfully installed.")
        return
    except Exception:
        pass
    try: # MacOS
        subprocess.check_call(['brew', 'install', '-y', 'ffmpeg'])
        main_window.show_info("FFmpeg successfully installed.")
        return
    except Exception:
        pass
    try: # Arch Linux
        subprocess.check_call(['pkexec', 'pacman', '--noconfirm', '-S', 'ffmpeg'])
        main_window.show_info("FFmpeg successfully installed.")
        return
    except Exception:
        pass
    try: # Debian Linux/Ubuntu
        subprocess.check_call(['pkexec', 'apt', '-y', 'install', 'ffmpeg'])
        main_window.show_info("FFmpeg successfully installed.")
        return
    except Exception:
        pass
    try: # Fedora Linux
        subprocess.check_call(['pkexec', 'dnf', '--assumeyes', 'install', 'ffmpeg'])
        main_window.show_info("FFmpeg successfully installed.")
        return
    except Exception:
        pass
    try: # Void Linux
        subprocess.check_call(['pkexec', 'xbps-install', '-y', 'ffmpeg'])
        main_window.show_info("FFmpeg successfully installed.")
        return
    except Exception:
        pass
    try: # Alpine Linux
        subprocess.check_call(['pkexec', 'apk', '-y', 'add', 'ffmpeg'])
        main_window.show_info("FFmpeg successfully installed.")
        return
    except Exception:
        pass
    try: # openSUSE
        subprocess.check_call(['pkexec', 'zypper', '-n', 'install', 'ffmpeg'])
        main_window.show_info("FFmpeg successfully installed.")
        return
    except Exception:
        pass

    ui.show_error("FFmpeg failed to install. Your files may not download in the correct file format!")
def ffmpeg_prompt() -> None:
    result = QMessageBox.critical(
        None,
        "FFmpeg not installed",
        "FFmpeg is required for this program's functionality. FFmpeg is not installed, do you want to try to automatically install FFmpeg with your package manager?",
        QMessageBox.Yes | QMessageBox.No
    )

    if result == QMessageBox.Yes:
        print("Yup, I want to install FFmpeg!")
        try:
            install_ffmpeg()
        except:
            print("Oh dear, I failed to install FFmpeg!")
            main_window.show_error("FFmpeg failed to install. Your files may not download in the correct file format!")
    else:
        print("Nope, I don't want to install FFmpeg!")

# | -- Manage items -- | #
    
def remove_item(index, remove_highest) -> None:
    """Removes the item from added_videos with the given index, also removes the item from the UI list."""
    global added_videos

    if remove_highest == True:
        item = main_window.item_list.takeItem(0)
    elif remove_highest == False:
        item = main_window.item_list.takeItem(index)
        
    del item
    del added_videos[index]

    on_update_items_label(len(added_videos))

def remove_item_on_activate(item) -> None:
    """Removes an item when it is activated in the GUI."""
    remove_item(main_window.item_list.row(item), False)
    
# | -- Updating variables -- | #

def update_output_directory() -> None:
    """Lets the user choose where to output downloaded videos."""
    global output_directory
    directory = QFileDialog.getExistingDirectory(main_window, main_window.tr("Open Directory"))
    if directory != "":
        output_directory = directory
        main_window.output_label.setText(f"Output directory: {output_directory}")

def update_file_format(text) -> None:
    """Sets the file_format variable from the chosen option in the dropdown menu."""
    global file_format
    file_format = text.replace('.', '')

def update_video_quality(text) -> None:
    """Sets the video_quality variable from the chosen option in the dropdown menu."""
    global video_quality
    video_quality = sub("[^0-9]", "", text)
    
def update_url(text) -> None:
    """Used for setting the url variable to the text in the UI."""
    global url
    url = text

# | -- Checks -- | #

def check_for_ffmpeg() -> None:
    """Returns True if FFmpeg is installed and returns False otherwise."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            return True
        else:
            return False
    except FileNotFoundError:
        return False

# | ---- UI Signals ---- | #

def on_add_item_to_list(result) -> None:
    main_window.item_list.addItem(result)

def on_update_items_label(result) -> None:
    if result != 1:
        main_window.items_label.setText(f"{result} items")
    else:
        main_window.items_label.setText(f"{result} item")

# | ---- Threading ---- | #

threads = []
workers = []

def start_thread(worker) -> None:
    thread = QThread()

    worker.moveToThread(thread)

    thread.started.connect(worker.run)

    worker.add_item_to_list.connect(on_add_item_to_list)
    worker.update_items_label.connect(on_update_items_label)
    worker.clear_item_list.connect(main_window.url_editor.clear)
    worker.error_message.connect(main_window.show_error)
    worker.info_message.connect(main_window.show_info)
    worker.update_progress_bar.connect(main_window.update_progress_bar)

    # Cleanup
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    thread.finished.connect(lambda: threads.remove(thread))

    threads.append(thread)
    workers.append(worker)

    thread.start()

# | ---- Main Function ---- | #

def main() -> None:
    """Main function, called from main.py"""
    global url, added_videos, output_directory, video_quality, file_format, main_window

    app = QApplication(sys.argv)
    main_window = ui.MainWindow()
    main_window.show()

    if check_for_ffmpeg() == False:
        ffmpeg_prompt()

    main_window.url_editor.textChanged.connect(update_url)
    main_window.url_button.clicked.connect(lambda: start_thread(AddItem()))
    main_window.browse_button.clicked.connect(update_output_directory)
    main_window.quality_combo.currentTextChanged.connect(update_video_quality)
    main_window.file_format_combo.currentTextChanged.connect(update_file_format)
    main_window.download_button.clicked.connect(lambda: start_thread(DownloadItems()))
    main_window.item_list.itemActivated.connect(remove_item_on_activate)

    sys.exit(app.exec())