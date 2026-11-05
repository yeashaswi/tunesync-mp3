# TuneSync MP3 🎵

A Python utility to download YouTube audio and playlists formatted, tagged, and sanitized for older hardware MP3 players, iPods, car stereos, and FAT32 SD cards.

---

## Why This Exists

Most modern downloaders produce files that choke older portable music hardware:
- **FAT32 Filename Errors:** Characters like `:`, `?`, `*`, or `|` cause write errors on FAT32/exFAT formatted microSD cards.
- **Unsupported Metadata:** Modern ID3v2.4 tags or oversized embedded PNG cover art cause vintage players (SanDisk Sansa, older iPods, Ruizu, FiiO, factory car stereos) to freeze or fail to display song info.
- **Cluttered Titles:** Video titles often include junk like `[Official Music Video]`, `(Lyrics 4K)`, or track number prefixes that ruin sorted albums.
- **Inflated Bitrates:** Re-encoding YouTube's audio stream (which is typically ~128–160 kbps Opus) to 320 kbps MP3 inflates file size on small SD cards without any real acoustic improvement.

TuneSync automates cleaning titles, writing standard ID3v2.3 tags with baseline JPEG art, sanitizing filenames, and transcoding to a sensible 192 kbps MP3 default.

---

## Features

- 🎧 **ID3v2.3 & JPEG Art:** Writes standard ID3v2.3 tags and resizes album covers to baseline JPEGs that older portable players can actually parse.
- 🧹 **Title Cleaning:** Strips common YouTube video noise (`[Official Video]`, `(Lyrics)`, `Prod. by...`) and trims leading track numbers.
- 💾 **FAT32 Filename Sanitization:** Removes illegal characters (`/ \ : * ? " < > |`) so files write cleanly to FAT32 SD cards without corruption errors.
- 🎚️ **Practical Default Bitrate:** Encodes at **192 kbps MP3** by default (customizable to 128k, 160k, or 320k) to preserve audio fidelity without wasting storage on small memory cards.
- 🌐 **Local Web UI (Optional):** Run with `--web` to launch a simple local browser interface, or connect from a phone on the same Wi-Fi network and download playlists as a `.zip`.
- ⚡ **Archive / Resume Support:** Keeps a download history text file so running the script on a growing playlist only downloads newly added songs.

---

## ⚠️ Caveats & Known Flaws

1. **Depends on `yt-dlp` staying current:** YouTube frequently updates its player APIs and anti-bot checks. If downloads start failing with HTTP 403 or signature errors, run `pip install -U yt-dlp` to update to the latest release.
2. **Lossy-to-Lossy Transcoding:** YouTube streams audio in Opus or AAC (around 128–160 kbps). Converting that to MP3 is lossy-to-lossy transcoding. It is done strictly for compatibility with hardware players that cannot decode Opus, not to improve sound quality.
3. **Rate Limits / Captchas:** Downloading massive playlists (hundreds of tracks) too quickly from a single IP can trigger YouTube's bot detection. Using cookies (`--cookies`) helps if you run into temporary blocks.
4. **"Mobile Support" is local only:** Mobile access requires running `python app.py --web` on a computer connected to your local Wi-Fi, then opening the computer's local IP in your phone's browser.

---

## Prerequisites

- **Python 3.9+**
- **FFmpeg** installed and accessible in your system's `PATH`.
  - **macOS:** `brew install ffmpeg`
  - **Windows:** `winget install Gyan.FFmpeg`
  - **Linux (Ubuntu/Debian):** `sudo apt install ffmpeg`

---

## Usage

### 1. Interactive Terminal Wizard
Run without arguments for an interactive step-by-step prompt:
```bash
python app.py
```

### 2. Command Line (CLI)
```bash
# Download a playlist or track at default 192 kbps
python app.py "https://music.youtube.com/playlist?list=..."

# Download to a specific folder at 320 kbps
python app.py "https://www.youtube.com/watch?v=..." -b 320k -o "Workout Mix"

# Download without cleaning title strings
python app.py "https://www.youtube.com/watch?v=..." --no-clean
```

| Flag | Description | Default |
| :--- | :--- | :--- |
| `url` | YouTube / YouTube Music playlist or track URL | Prompted if omitted |
| `-b, --bitrate` | Audio bitrate (`128k`, `160k`, `192k`, `320k`) | `192k` |
| `-o, --output` | Output folder directory | `downloads` |
| `--web` | Launch the local web UI | `False` |
| `--port` | Port for the local web UI | `5000` |
| `--no-clean` | Skip title sanitization | `False` |
| `--no-art` | Do not embed cover art | `False` |
| `--no-archive` | Re-download all tracks even if previously downloaded | `False` |

### 3. Local Web Interface
```bash
python app.py --web
```
Open `http://localhost:5000` on your desktop, or `http://<your-computer-ip>:5000` from your phone on the same Wi-Fi.

---

## License

MIT
