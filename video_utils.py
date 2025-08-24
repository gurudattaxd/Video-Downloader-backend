import yt_dlp
import os
from moviepy.video.io.VideoFileClip import VideoFileClip

def download_and_trim(url, start, end, output_folder):
    ydl_opts = {
        'format': 'mp4/bestaudio/best',
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    if start is not None and end is not None:
        trimmed_file = os.path.join(output_folder, f"trimmed_{os.path.basename(filename)}")
        with VideoFileClip(filename) as clip:
            trimmed_clip = clip.subclip(start, end)
            trimmed_clip.write_videofile(trimmed_file, codec='libx264', audio_codec='aac')
        return trimmed_file

    return filename
