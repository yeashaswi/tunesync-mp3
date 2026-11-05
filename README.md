# 🎵 TuneSync MP3

> **The ultimate YouTube & YouTube Music downloader designed specifically for hardware MP3 players, iPods, car stereos, and MicroSD cards.**

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux%20%7C%20Android%20%7C%20iOS-orange.svg)]()

---

## 💡 Why TuneSync?

Most YouTube downloaders produce files that fail on dedicated MP3 players and microSD cards:
- **Corrupted Filenames:** Illegal characters (`:`, `?`, `*`, `|`) cause FAT32/exFAT memory card write errors.
- **Unreadable Tags:** Modern ID3v2.4 tags and huge PNG images cause vintage players (SanDisk Clip, iPods, Ruizu, FiiO, car stereos) to freeze or fail to display metadata.
- **Cluttered Titles:** Video titles like `Song Name (Official Music Video) [HD]` and `001 - Song` clutter your library.
- **Inflated File Sizes:** Transcoding YouTube's 128–160 kbps Opus stream to 320 kbps wastes 40% of your SD card storage with zero improvement in acoustic quality.

**TuneSync MP3 fixes all of this automatically.**

---

## ✨ Features

- 🎧 **Universal MP3 Player Compatibility:** Embeds strict **ID3v2.3 tags** and baseline **JPEG cover art** so title, artist, album, and artwork render cleanly on any player.
- 🧹 **Automatic Title Cleaning:** Strips YouTube video clutter (`[Official Music Video]`, `(Lyrics)`, `Prod. @...`, `| 4K`) and removes track number prefixes.
- 💾 **MicroSD & FAT32 Safe:** Automatically sanitizes filenames to guarantee 100% compatibility with FAT32 and exFAT memory cards.
- 🎚️ **Smart Bitrate Encoding:** Encodes at **192 kbps MP3** by default — capturing 100% of YouTube's native audio stream while saving **~40% storage space** (320k, 160k, and 128k options also available).
- 🌐 **Built-in Web Interface:** Run `python app.py --web` to access a sleek dark-mode web UI. On mobile (iOS / Android), connect to the local IP address and tap **"Download as ZIP"** to export playlists directly to your phone's Files app!
- ⚡ **Resumable Playlist Syncing:** Remembers downloaded tracks so you can re-run the tool anytime to sync newly added songs without re-downloading existing ones.
- 🛡️ **Graceful Skip:** Automatically ignores deleted or private YouTube tracks without aborting the playlist.

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yeashaswi/tunesync-mp3.git
cd tunesync-mp3
```

### 2. Launch
#### On macOS / Linux / Android (Termux):
```bash
./run.sh
```
*(Or launch the Web UI directly: `./run.sh --web`)*

#### On Windows:
Double-click **`run.bat`** or run:
```cmd
run.bat
```

---

## 🖥️ Usage

### Option A: Modern Web UI (Recommended for Mobile / iOS / Android)
```bash
python app.py --web
```
- Open `http://localhost:5000` in your computer's browser.
- **On iOS / Android:** Open Safari or Chrome on your phone and go to `http://<your-computer-ip>:5000`.
- Paste any playlist or track URL, click **Download**, and tap **"Download as ZIP"** when finished to save all MP3s directly to your mobile device!

---

### Option B: Interactive Terminal Wizard
Simply run without arguments to start the step-by-step interactive prompt:
```bash
python app.py
```

---

### Option C: CLI Mode
```bash
# Download a playlist at recommended 192 kbps
python app.py "https://music.youtube.com/playlist?list=..."

# Download at 320 kbps to a custom folder
python app.py "https://www.youtube.com/watch?v=..." -b 320k -o "Workout Mix"

# Download without cleaning titles
python app.py "https://music.youtube.com/playlist?list=..." --no-clean
```

#### CLI Options Reference:
| Flag | Description | Default |
| :--- | :--- | :--- |
| `url` | YouTube or YouTube Music playlist/track URL | Prompted if omitted |
| `-b, --bitrate` | Audio bitrate (`128k`, `160k`, `192k`, `320k`) | `192k` |
| `-o, --output` | Output folder directory | `downloads` |
| `--web` | Launch the local web browser UI | `False` |
| `--port` | Port for the web UI server | `5000` |
| `--no-clean` | Skip title and filename cleaning | `False` |
| `--no-art` | Do not embed album cover art | `False` |
| `--no-archive` | Re-download all tracks even if previously downloaded | `False` |

---

## 📦 OS-Specific Installation Guide

### macOS
1. Install [Homebrew](https://brew.sh/) if not already installed.
2. Install Python 3 and FFmpeg:
   ```bash
   brew install python ffmpeg
   ```
3. Run `./run.sh`

---

### Windows
1. Install [Python 3](https://www.python.org/downloads/) *(Check "Add Python to PATH" during setup)*.
2. Install FFmpeg using Windows Package Manager:
   ```cmd
   winget install Gyan.FFmpeg
   ```
3. Double-click `run.bat`

---

### Linux (Ubuntu / Debian / Fedora / Arch)
```bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y python3 python3-pip python3-venv ffmpeg

# Fedora
sudo dnf install -y python3 ffmpeg

# Arch Linux
sudo pacman -S python python-pip ffmpeg

./run.sh
```

---

### Android (Termux)
You can run TuneSync completely natively on your Android device without a PC:
1. Install [Termux from F-Droid](https://f-droid.org/en/packages/com.termux/).
2. Open Termux and install dependencies:
   ```bash
   pkg update && pkg install -y python ffmpeg git
   ```
3. Clone and run:
   ```bash
   git clone https://github.com/yeashaswi/tunesync-mp3.git
   cd tunesync-mp3
   pip install -r requirements.txt
   python app.py
   ```

---

### iOS (iPhone & iPad)
Because iOS does not allow raw terminal execution, use the **Web UI method**:
1. Run `python app.py --web` on any computer on your Wi-Fi network.
2. In your terminal, note the **Mobile Access URL** (e.g. `http://192.168.1.100:5000`).
3. Open **Safari** on your iPhone/iPad and navigate to that address.
4. Paste your playlist link and tap **Download Playlist**.
5. Once complete, tap **Download as ZIP**. Safari will save the entire folder directly to your **Files** app!

---

## 🛠️ Transferring to Your MicroSD Card / MP3 Player

1. Insert your MicroSD card into your computer.
2. Open your downloaded folder (or extract the `.zip` archive).
3. Drag and drop the MP3 files into your MicroSD card's `Music/` folder.
4. Safely eject the card, insert it into your player, and enjoy!

---

## 📄 License

Distributed under the [MIT License](LICENSE). Free for personal and commercial use.
