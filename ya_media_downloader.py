# | ---- Imports ---- | #

import sys
import subprocess
import webbrowser
from re import sub
from time import time
from PySide6.QtWidgets import (QApplication, QFileDialog, QMessageBox)
from PySide6.QtCore import (QThread, QObject, Signal, Slot, QEventLoop)
import constants
import ui
import yt_dlp_wrapper

# | ---- Global Variables ---- | #

main_window = None
about_window = None
added_videos = {}
num_of_added_items = 0
url = ""
output_directory = ""
video_quality = "1080"
file_format = "mp4"
downloading = False
adding = False


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
    remove_item_signal = Signal(int, bool)

    @Slot()
    def run(self):
        global url, added_videos, downloading, num_of_added_items, adding
        _url = url
        url = ""
        adding = True
        if downloading:
            adding = False
            self.error_message.emit(
                "Cannot add an item to the list because you are downloading items! Please wait for the items to finish downloading.")
            self.finished.emit()
            return

        try:
            info = yt_dlp_wrapper.get_info(_url)
        except:
            adding = False
            self.error_message.emit(
                f"The URL ({_url}) couldn't be added. This could be caused by your IP being blocked by the website. Did you enter the correct URL?")
            self.finished.emit()
            return

        _id = yt_dlp_wrapper.get_id(info)

        index = len(added_videos)
        added_videos[index] = info

        self.update_items_label.emit(len(added_videos))

        if yt_dlp_wrapper.is_playlist(info):
            self.add_item_to_list.emit(
                f"{yt_dlp_wrapper.get_title(info)} — By {yt_dlp_wrapper.get_uploader_id(info)} — Type: Playlist")
            print(
                f"Added {yt_dlp_wrapper.get_title(info)} — By {yt_dlp_wrapper.get_uploader_id(info)} — Type: Playlist")
        else:
            self.add_item_to_list.emit(
                f"{yt_dlp_wrapper.get_title(info)} — By {yt_dlp_wrapper.get_uploader_id(info)} — Type: Video")
            print(f"Added {yt_dlp_wrapper.get_title(info)} — By {yt_dlp_wrapper.get_uploader_id(info)} — Type: Video")

        num_of_added_items += 1
        adding = False
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
    remove_item_signal = Signal(int, bool)

    @Slot()
    def run(self):
        global added_videos, output_directory, video_quality, file_format, downloading, adding
        if downloading:
            self.finished.emit()
            return
        if adding:
            self.error_message.emit("Wait for the item(s) to finish adding before you try to download them.")
            self.finished.emit()
            return
        downloading = True

        total_items = len(added_videos)
        downloaded_items = 0

        if total_items == 0:
            self.error_message.emit("You need to add videos before you try to download them.")
            downloading = False
            self.finished.emit()
            return

        if output_directory == "":
            self.error_message.emit("No output directory was selected. Please select an output directory.")
            downloading = False
            self.finished.emit()
            return

        if file_format == "gif" and (video_quality == "240" or video_quality == "144"):
            self.error_message.emit(
                ".gif file format must be at least 360p. Please set your video quality to 360p or higher.")
            downloading = False
            self.finished.emit()
            return

        for i in range(total_items):
            info = added_videos[i]
            _url = yt_dlp_wrapper.get_url(info)
            try:
                self.update_progress_bar.emit(0)
                yt_dlp_wrapper.download_video(_url, output_directory, video_quality, file_format, main_window)
                downloaded_items += 1
            except:
                self.error_message.emit(
                    f"{yt_dlp_wrapper.get_title(info)} couldn't be downloaded. The other items will still attempt to download.")
            self.remove_item_signal.emit(i, True)
        self.clear_item_list.emit()
        self.update_progress_bar.emit(0)
        self.info_message.emit(f"{downloaded_items}/{total_items} downloaded successfully.")
        added_videos.clear()
        downloading = False
        self.finished.emit()


# | ---- Functions ---- | #

def install_ffmpeg() -> None:
    """Hideous disgrace of a function that tries many package managers to install FFmpeg. Yikes!!!"""
    # Supports windows (winget), macOS (homebrew), arch linux (pacman), debian/ubuntu.. (apt), fedora.. (dnf), void (xbps-install), alpine (apk), openSUSE (zypper)
    global main_window
    try:  # Windows
        subprocess.check_call(
            ['winget', 'install', 'ffmpeg', '--accept-source-agreements', '--accept-package-agreements',
             '--disable-interactivity'])
        main_window.show_info("FFmpeg successfully installed.")
        return
    except:
        pass
    try:  # MacOS
        subprocess.check_call(['brew', 'install', '-y', 'ffmpeg'])
        main_window.show_info("FFmpeg successfully installed.")
        return
    except:
        pass
    try:  # Arch Linux
        subprocess.check_call(['pkexec', 'pacman', '--noconfirm', '-S', 'ffmpeg'])
        main_window.show_info("FFmpeg successfully installed.")
        return
    except:
        pass
    try:  # Debian Linux/Ubuntu
        subprocess.check_call(['pkexec', 'apt', '-y', 'install', 'ffmpeg'])
        main_window.show_info("FFmpeg successfully installed.")
        return
    except:
        pass
    try:  # Fedora Linux
        subprocess.check_call(['pkexec', 'dnf', '--assumeyes', 'install', 'ffmpeg'])
        main_window.show_info("FFmpeg successfully installed.")
        return
    except:
        pass
    try:  # Void Linux
        subprocess.check_call(['pkexec', 'xbps-install', '-y', 'ffmpeg'])
        main_window.show_info("FFmpeg successfully installed.")
        return
    except:
        pass
    try:  # Alpine Linux
        subprocess.check_call(['pkexec', 'apk', '-y', 'add', 'ffmpeg'])
        main_window.show_info("FFmpeg successfully installed.")
        return
    except:
        pass
    try:  # openSUSE
        subprocess.check_call(['pkexec', 'zypper', '-n', 'install', 'ffmpeg'])
        main_window.show_info("FFmpeg successfully installed.")
        return
    except:
        pass

    main_window.show_error("FFmpeg failed to install. Your files may not download in the correct file format!")


def ffmpeg_prompt() -> None:
    result = QMessageBox.critical(
        main_window,
        "FFmpeg not installed",
        "FFmpeg is required for this program's functionality. FFmpeg is not installed, do you want to try to automatically install FFmpeg with your package manager?",
        QMessageBox.Yes | QMessageBox.No
    )

    if result == QMessageBox.Yes:
        try:
            install_ffmpeg()
        except:
            main_window.show_error("FFmpeg failed to install. Your files may not download in the correct file format!")


# | -- Manage items -- | #

def remove_item(index, remove_highest, delete_item_from_added_videos) -> None:
    """Removes the item from added_videos with the given index, also removes the item from the UI list."""
    global added_videos, num_of_added_items, main_window

    if remove_highest:
        item = main_window.item_list.takeItem(0)
    else:
        item = main_window.item_list.takeItem(index)

    del item
    num_of_added_items -= 1
    if delete_item_from_added_videos:
        del added_videos[index]

    on_update_items_label(num_of_added_items)


def remove_item_on_activate(item) -> None:
    """Removes an item when it is activated in the GUI."""
    global downloading, main_window

    if downloading:
        main_window.show_error(
            "Cannot remove an item from the list because you are downloading items! Please wait for the items to finish downloading.")
        return
    if adding:
        main_window.show_error(
            "Cannot remove an item from the list because you are adding item(s)! Please wait for the item(s) to finish adding.")
        return

    remove_item(main_window.item_list.row(item), False, True)


# | -- Updating variables -- | #

def update_output_directory() -> None:
    """Lets the user choose where to output downloaded videos."""
    global output_directory, downloading, main_window

    if downloading:
        main_window.show_error(
            "Cannot change the output directory because you are downloading items! Please wait for the items to finish downloading.")
        return

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


# | -- Menu bar actions -- | #

def export_url_list() -> None:
    global downloading, main_window

    if downloading:
        main_window.show_error(
            "Cannot export the URL list because you are downloading items! Please wait for the items to finish downloading.")
        return

    directory = QFileDialog.getExistingDirectory(main_window, main_window.tr("Open Directory"))
    if directory == "":
        main_window.show_error(
            "The URL list was not exported because you did not select a directory to export the URL list to.")
        return

    with open(f"{directory}/YA_url_list_{str(round(time()))}.txt", 'w') as exported_url_list:
        url_string = ""

        for i in range(len(added_videos)):
            url_string = f"{url_string}{yt_dlp_wrapper.get_url(added_videos[i])}\n"

        exported_url_list.write(url_string.strip())
        main_window.show_info(f"The URL list was successfully exported at {exported_url_list.name}")


def import_url_list() -> None:
    global url, downloading, adding, main_window

    if downloading:
        main_window.show_error(
            "Cannot import the URL list because you are downloading items! Please wait for the items to finish downloading.")
        return
    if adding:
        main_window.show_error(
            "Cannot import the URL list because you are already adding item(s). Please wait for the item(s) to finish adding.")
        return
    exported_url_list = QFileDialog.getOpenFileName(main_window, main_window.tr("Open File"), "",
                                                    main_window.tr("Text files (*.txt)"))

    if exported_url_list[0] == "":
        main_window.show_error("No URL list was imported because you didn't select a file to import.")
        return

    url = ""
    main_window.item_list.clear()
    added_videos.clear()
    with open(exported_url_list[0], "r") as file:
        lines = sum(1 for line in file)
        if lines >= 10:
            result = QMessageBox.warning(
                main_window,
                "Warning",
                f"There are {lines} URLs to be imported. It is recommended to use a VPN or proxy when downloading this many items at the same time! Do you want to proceed?",
                QMessageBox.Yes | QMessageBox.No
            )
            if result == QMessageBox.No:
                main_window.show_info("The URL list was not imported.")
                return

        file.seek(0)
        for i, line in enumerate(file):
            url = line.strip()
            loop = QEventLoop()
            worker = start_thread(AddItem())
            worker.finished.connect(loop.quit)

            loop.exec()

        main_window.show_info(f"The URL list was successfully imported.")


# | -- Checks -- | #

def check_for_ffmpeg() -> bool:
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
    global main_window
    main_window.item_list.addItem(result)


def on_update_items_label(result) -> None:
    global main_window
    if result != 1:
        main_window.items_label.setText(f"{result} items")
    else:
        main_window.items_label.setText(f"{result} item")


# | ---- Threading ---- | #

threads = []
workers = []


def start_thread(worker):
    global main_window
    thread = QThread()

    worker.moveToThread(thread)

    thread.started.connect(worker.run)

    worker.add_item_to_list.connect(on_add_item_to_list)
    worker.update_items_label.connect(on_update_items_label)
    worker.clear_item_list.connect(main_window.url_editor.clear)
    worker.error_message.connect(main_window.show_error)
    worker.info_message.connect(main_window.show_info)
    worker.update_progress_bar.connect(main_window.update_progress_bar)
    worker.remove_item_signal.connect(lambda i, remove_highest: remove_item(i, remove_highest, False))

    # Cleanup
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    thread.finished.connect(lambda: threads.remove(thread))

    threads.append(thread)
    workers.append(worker)

    thread.start()

    return worker


# | ---- Main Function ---- | #

def main() -> None:
    """Main function, called from main.py"""
    global url, added_videos, output_directory, video_quality, file_format, main_window, about_window

    app = QApplication(sys.argv)
    main_window = ui.MainWindow()
    about_window = ui.AboutWindow()
    main_window.show()

    if not check_for_ffmpeg():
        ffmpeg_prompt()

    main_window.url_editor.textChanged.connect(update_url)
    main_window.url_button.clicked.connect(lambda: start_thread(AddItem()))
    main_window.browse_button.clicked.connect(update_output_directory)
    main_window.quality_combo.currentTextChanged.connect(update_video_quality)
    main_window.file_format_combo.currentTextChanged.connect(update_file_format)
    main_window.download_button.clicked.connect(lambda: start_thread(DownloadItems()))
    main_window.item_list.itemActivated.connect(remove_item_on_activate)
    main_window.export_url_list.triggered.connect(export_url_list)
    main_window.import_url_list.triggered.connect(import_url_list)
    main_window.about_action.triggered.connect(about_window.show)

    about_window.github_button.clicked.connect(
        lambda: webbrowser.open("https://github.com/Raixu27/ya-media-downloader"))
    about_window.github_releases_button.clicked.connect(
        lambda: webbrowser.open("https://github.com/Raixu27/ya-media-downloader/releases"))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()