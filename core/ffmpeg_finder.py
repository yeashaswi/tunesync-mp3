import os
import shutil
import sys

def get_ffmpeg_path():
    """
    Locates the ffmpeg binary across macOS, Windows, Linux, and Android (Termux).
    Returns the path to ffmpeg executable, or None if not found.
    """
    # 1. Check if ffmpeg is in system PATH
    found = shutil.which("ffmpeg")
    if found:
        return found

    # 2. Known common installation paths
    candidate_paths = []

    if sys.platform == "darwin":  # macOS
        candidate_paths = [
            "/opt/homebrew/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            os.path.expanduser("~/homebrew/bin/ffmpeg"),
            "/opt/local/bin/ffmpeg",
        ]
    elif sys.platform.startswith("win"):  # Windows
        candidate_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe"),
            os.path.expandvars(r"%USERPROFILE%\scoop\shims\ffmpeg.exe"),
            os.path.expandvars(r"%ProgramData%\chocolatey\bin\ffmpeg.exe"),
        ]
    else:  # Linux / Android (Termux)
        candidate_paths = [
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/data/data/com.termux/files/usr/bin/ffmpeg",  # Android Termux
            "/data/data/com.termux/files/usr/bin/ffmpeg.real",
            "/bin/ffmpeg",
        ]

    for path in candidate_paths:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path

    return None

def verify_ffmpeg():
    """
    Returns (True, path) if found, else (False, install_instruction)
    """
    path = get_ffmpeg_path()
    if path:
        return True, path

    instructions = {
        "darwin": "Install via Homebrew: brew install ffmpeg",
        "win32": "Install via WinGet: winget install Gyan.FFmpeg\nOr download from https://ffmpeg.org/download.html",
        "linux": "Install via package manager: sudo apt install ffmpeg (Debian/Ubuntu) or sudo dnf install ffmpeg (Fedora)",
    }
    help_text = instructions.get(sys.platform, "Please install ffmpeg from https://ffmpeg.org and add it to your PATH.")
    if "com.termux" in os.environ.get("PREFIX", ""):
        help_text = "Install in Termux: pkg install ffmpeg"

    return False, help_text
