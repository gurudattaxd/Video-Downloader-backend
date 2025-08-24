import yt_dlp
import os
from moviepy.video.io.VideoFileClip import VideoFileClip


def download_and_trim(url, start, end, output_folder, quality="720p"):
    """
    Download and optionally trim a video from the provided URL
    
    Args:
        url: Video URL to download
        start: Start time in seconds (optional)
        end: End time in seconds (optional)  
        output_folder: Directory to save the video
        quality: Video quality preference (720p, 1080p, 4k, audio)

    Returns:
        str: Path to the downloaded/trimmed video file
    """
    
    # Configure quality format based on user selection
    if quality == "audio":
        format_selector = 'bestaudio/best'
        ext = 'mp3'
    elif quality == "4k":
        format_selector = 'bestvideo[height<=2160]+bestaudio/best[height<=2160]'
        ext = 'mp4'
    elif quality == "1080p":
        format_selector = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
        ext = 'mp4'
    else:  # Default to 720p
        format_selector = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
        ext = 'mp4'
    
    ydl_opts = {
        'format': format_selector,
        'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'merge_output_format': ext,
        'postprocessors': [],
    }
    
    # Add audio extraction postprocessor for audio-only downloads
    if quality == "audio":
        ydl_opts['postprocessors'].append({
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if quality == "audio":
                filename = filename.rsplit('.', 1)[0] + '.mp3'

        # Trim video only if start and end specified and not audio
        if start is not None and end is not None and quality != "audio":
            trimmed_file = os.path.join(output_folder, f"trimmed_{os.path.basename(filename)}")
            try:
                with VideoFileClip(filename) as clip:
                    trimmed_clip = clip.subclip(start, end)
                    trimmed_clip.write_videofile(trimmed_file, codec='libx264', audio_codec='aac')
                    trimmed_clip.close()

                # Remove original file and return trimmed version
                if os.path.exists(filename):
                    os.remove(filename)
                return trimmed_file
            except Exception as e:
                print(f"Trimming failed: {e}")
                return filename

        return filename
        
    except Exception as e:
        print(f"Download failed: {e}")
        raise Exception(f"Failed to download video: {str(e)}")
