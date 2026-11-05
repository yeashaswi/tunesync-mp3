@echo off
setlocal
cd /d "%~dp0"

echo ==================================================
echo   TuneSync MP3 Downloader for Windows
echo ==================================================

:: Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3 from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Check FFmpeg
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg was not found in PATH.
    echo If downloads fail, please install FFmpeg using:
    echo   winget install Gyan.FFmpeg
    echo.
)

:: Create virtual environment if missing
if not exist ".venv" (
    echo [INFO] Setting up virtual environment...
    python -m venv .venv
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Install dependencies
pip install -r requirements.txt --quiet

:: Run App
python app.py %*

pause
