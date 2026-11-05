#!/usr/bin/env bash
set -e

# Change directory to script location
cd "$(dirname "$0")"

# Include common Homebrew and Termux paths
export PATH="/opt/homebrew/bin:/usr/local/bin:/data/data/com.termux/files/usr/bin:$PATH"

echo "🎵 TuneSync MP3 Downloader"
echo "--------------------------------------------------"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "Please install Python 3 (https://www.python.org/downloads/)"
    exit 1
fi

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️ Warning: ffmpeg not detected in PATH."
    echo "On macOS:   brew install ffmpeg"
    echo "On Ubuntu:  sudo apt install ffmpeg"
    echo "On Termux:  pkg install ffmpeg"
    echo ""
fi

# Setup Virtual Environment if missing
if [ ! -d ".venv" ]; then
    echo "📦 Initializing virtual environment (.venv)..."
    python3 -m venv .venv
fi

# Activate Virtual Environment
source .venv/bin/activate

# Install / update requirements quietly
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# Run app
python3 app.py "$@"
