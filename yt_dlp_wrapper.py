# Wrapper functions around yt-dlp
from yt_dlp import YoutubeDL


def get_info(url) -> dict:
    """Returns information about a video/playlist extracted with yt_dlp"""
    try:
        with YoutubeDL({'quiet': True}) as ydl:
            return ydl.extract_info(url, download=False)
    except:
        print(
            "Failed to fetch info from URL! This is probably caused by you being blocked due to the website thinking you are a bot or entering the incorrect URL. Are you using a VPN?")
        raise Exception("Failed to fetch info from URL")


def get_url(info) -> str:
    """Returns the video/playlist URL."""
    try:
        return info["webpage_url"]
    except:
        print("Error occurred while fetching the URL in yt_dlp_wrapper.get_url()")
        return ""


def get_title(info) -> str:
    """Returns the title of the video/playlist"""
    try:
        return info['title']
    except:
        print("Error occurred while fetching the title in yt_dlp_wrapper.get_title()")
        return ""


def get_duration(info) -> int:
    """Returns the duration of the video in seconds"""
    try:
        return int(info['duration'])
    except:
        print("Error occurred while fetching the duration in yt_dlp_wrapper.get_duration()")
        return 0


def get_id(info) -> str:
    """Returns the ID of the video/playlist"""
    try:
        return info['id']
    except:
        print("Error occurred while fetching the ID in yt_dlp_wrapper.get_id()")
        return ""


def get_uploader_id(info) -> str:
    """Returns the channel name that uploaded the video/playlist"""
    try:
        return info['uploader_id']
    except:
        print("Error occurred while fetching the uploader id in yt_dlp_wrapper.get_uploader_id()")
        return ""


def is_playlist(info) -> bool:
    """Returns True if the provided info is a playlist, and False if it is not."""
    try:
        return 'entries' in info
    except:
        print("Error occurred in yt_dlp_wrapper.is_playlist()")
        return False


def download_video(url, output_directory, video_quality, file_format, main_window) -> None:
    """Downloads a video from the URL."""

    def progress_hook(d) -> None:
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)

            if total:
                percent = downloaded / total * 100
                main_window.update_progress_bar(percent)

    # | -- Set options -- | #
    ydl_opts = {
        "generic_video": {
            'progress_hooks': [progress_hook],
            'format': f'bestvideo[height<={video_quality}]+bestaudio/best',
            'merge_output_format': file_format,
            'outtmpl': f'{output_directory}/%(title)s.%(ext)s',
            'quiet': True
        },
        "gif": {
            'progress_hooks': [progress_hook],
            'format': f'bestvideo[height<={video_quality}]',
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "gif",
            }],
            'merge_output_format': 'gif',
            'outtmpl': f'{output_directory}/%(title)s.%(ext)s',
            'quiet': True
        },
        "generic_audio": {
            'progress_hooks': [progress_hook],
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': file_format,
                'preferredquality': '320',
            }],
            'merge_output_format': file_format,
            'outtmpl': f'{output_directory}/%(title)s.%(ext)s',
            'quiet': True
        },
        "generic_audio_no_preferred_quality": {
            'progress_hooks': [progress_hook],
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': file_format,
            }],
            'merge_output_format': file_format,
            'outtmpl': f'{output_directory}/%(title)s.%(ext)s',
            'quiet': True
        },
        "vorbis": {
            'progress_hooks': [progress_hook],
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'vorbis',
            }],
            'merge_output_format': file_format,
            'outtmpl': f'{output_directory}/%(title)s.%(ext)s',
            'quiet': True
        }
    }

    ydl_opts_filetypes = {
        "mp4": ydl_opts["generic_video"],
        "webm": ydl_opts["generic_video"],
        "mkv": ydl_opts["generic_video"],
        "gif": ydl_opts["gif"],
        "mp3": ydl_opts["generic_audio"],
        "wav": ydl_opts["generic_audio_no_preferred_quality"],
        "opus": ydl_opts["generic_audio_no_preferred_quality"],
        "ogg": ydl_opts["vorbis"],
        "flac": ydl_opts["generic_audio_no_preferred_quality"]
    }

    # | -- Download the video :) -- | #
    try:
        print(f"Downloading video {url}")
        with YoutubeDL(ydl_opts_filetypes[file_format]) as ydl:
            ydl.download([url])
        print(
            f"The video at {url} has successfully been downloaded as a .{file_format} file in {output_directory} at {video_quality}p quality.")
    except:
        print(f"Uh oh! An error occurred downloading the video at {url}")
        raise Exception