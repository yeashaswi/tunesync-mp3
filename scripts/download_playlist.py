#!/usr/bin/env python3
import os
import sys
import subprocess

PLAYLIST_URL = "https://music.youtube.com/playlist?list=PLXUywPFrGxWQxTYTXyJxN6oqFUIPkAhcW"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Favourite Songs")
ARCHIVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloaded_archive.txt")
VENV_YTDLP = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "bin", "yt-dlp")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Ensure PATH includes Homebrew for ffmpeg
env = os.environ.copy()
env["PATH"] = f"/opt/homebrew/bin:{env.get('PATH', '')}"

cmd = [
    VENV_YTDLP,
    "--ffmpeg-location", "/opt/homebrew/bin/ffmpeg",
    "--extract-audio",
    "--audio-format", "mp3",
    "--audio-quality", "192K",
    "--embed-thumbnail",
    "--convert-thumbnails", "jpg",
    "--embed-metadata",
    "--windows-filenames",
    "--ignore-errors",
    "--no-overwrites",
    "--download-archive", ARCHIVE_FILE,
    "-o", os.path.join(OUTPUT_DIR, "%(title)s.%(ext)s"),
    "--postprocessor-args", "ExtractAudio:-id3v2_version 3",
    PLAYLIST_URL
]

print(f"Starting download to: {OUTPUT_DIR}")
print("Settings: MP3 (ID3v2.3, high quality, JPEG cover art, microSD safe filenames)")
sys.stdout.flush()

process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

for line in iter(process.stdout.readline, ''):
    print(line, end='', flush=True)

process.stdout.close()
return_code = process.wait()

if return_code == 0:
    print("\nDownload complete! All songs are ready in 'Favourite Songs' folder.")
else:
    print(f"\nProcess finished with exit code {return_code}.")
sys.exit(return_code)
