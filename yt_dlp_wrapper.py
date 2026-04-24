# Wrapper functions around yt-dlp
from yt_dlp import YoutubeDL


def get_info(url) -> dict:
    """Returns information about a video/playlist extracted with yt_dlp"""
    try:
        with YoutubeDL({'quiet': True}) as ydl:
            return ydl.extract_info(url, download=False)
    except:
        print(
            "Failed to fetch info from URL! This is probably caused by you being blocked due to the website thinking "
            "you are a bot or entering the incorrect URL. Are you using a VPN?")
        raise Exception("Failed to fetch info from URL")


def get_url(info) -> str:
    """Returns the video/playlist URL."""
    try:
        return info["webpage_url"]
    except KeyError:
        print("Error occurred while fetching the URL in yt_dlp_wrapper.get_url()")
        return ""


def get_title(info) -> str:
    """Returns the title of the video/playlist"""
    try:
        return info['title']
    except KeyError:
        print("Error occurred while fetching the title in yt_dlp_wrapper.get_title()")
        return ""


def get_duration(info) -> int:
    """Returns the duration of the video in seconds"""
    try:
        return int(info['duration'])
    except KeyError:
        print("Error occurred while fetching the duration in yt_dlp_wrapper.get_duration()")
        return 0


def get_id(info) -> str:
    """Returns the ID of the video/playlist"""
    try:
        return info['id']
    except KeyError:
        print("Error occurred while fetching the ID in yt_dlp_wrapper.get_id()")
        return ""


def get_uploader_id(info) -> str:
    """Returns the channel name that uploaded the video/playlist"""
    try:
        return info['uploader_id']
    except KeyError:
        print("Error occurred while fetching the uploader id in yt_dlp_wrapper.get_uploader_id()")
        return ""


def is_playlist(info) -> bool:
    """Returns True if the provided info is a playlist, and False if it is not."""
    return 'entries' in info


def download_video(url, settings, main_window) -> None:
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
            'format': f'bestvideo[height<={settings["video_quality"]}]+bestaudio/best',
            'merge_output_format': settings["file_format"],
            'outtmpl': f'{settings["output_directory"]}/%(title)s.%(ext)s',
            'quiet': True,
            'ratelimit': settings["bandwidth_limit"]*1000,
            "writesubtitles": settings["subtitles"] == "True",
            "writeautomaticsub": settings["subtitles"] == "True",
            "subtitleslangs": ["en"],
            "subtitlesformat": "vtt"
        },
        "gif": {
            'progress_hooks': [progress_hook],
            'format': f'bestvideo[height<={settings["video_quality"]}]',
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "gif",
            }],
            'merge_output_format': 'gif',
            'outtmpl': f'{settings["output_directory"]}/%(title)s.%(ext)s',
            'quiet': True,
            'ratelimit': settings["bandwidth_limit"]*1000
        },
        "generic_audio": {
            'progress_hooks': [progress_hook],
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': settings["file_format"],
                'preferredquality': settings["audio_bitrate"],
            }],
            'merge_output_format': settings["file_format"],
            'outtmpl': f'{settings["output_directory"]}/%(title)s.%(ext)s',
            'quiet': True,
            'ratelimit': settings["bandwidth_limit"]*1000
        },
        "generic_audio_no_preferred_quality": {
            'progress_hooks': [progress_hook],
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': settings["file_format"],
            }],
            'merge_output_format': settings["file_format"],
            'outtmpl': f'{settings["output_directory"]}/%(title)s.%(ext)s',
            'quiet': True,
            'ratelimit': settings["bandwidth_limit"]*1000
        },
        "vorbis": {
            'progress_hooks': [progress_hook],
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'vorbis',
            }],
            'merge_output_format': settings["file_format"],
            'outtmpl': f'{settings["output_directory"]}/%(title)s.%(ext)s',
            'quiet': True,
            'ratelimit': settings["bandwidth_limit"]*1000
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

        if ydl_opts_filetypes[settings["file_format"]]["ratelimit"] <= 0:
            ydl_opts_filetypes[settings["file_format"]]["ratelimit"] = None

        with YoutubeDL(ydl_opts_filetypes[settings["file_format"]]) as ydl:
            ydl.download([url])
        print(
            f"The video at {url} has successfully been downloaded as a .{settings["file_format"]} file in {settings["output_directory"]} at {settings["video_quality"]}p quality.")
    except:
        print(f"Uh oh! An error occurred downloading the video at {url}")
        raise Exception("An error occurred downloading the video")
