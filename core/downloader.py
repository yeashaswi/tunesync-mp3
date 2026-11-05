import os
import sys
import glob
from typing import Callable, Optional
import yt_dlp
from mutagen.easyid3 import EasyID3

from .ffmpeg_finder import get_ffmpeg_path, verify_ffmpeg
from .cleaner import clean_title

class PlaylistDownloader:
    def __init__(
        self,
        output_dir: str = "downloads",
        bitrate: str = "192k",
        clean_names: bool = True,
        embed_art: bool = True,
        use_archive: bool = True,
        progress_callback: Optional[Callable[[dict], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
    ):
        self.output_dir = os.path.abspath(output_dir)
        self.bitrate = bitrate.lower().replace("kbps", "").replace("k", "")
        self.clean_names = clean_names
        self.embed_art = embed_art
        self.use_archive = use_archive
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.is_cancelled = False

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def log(self, message: str):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def cancel(self):
        self.is_cancelled = True

    def _post_process_file(self, file_path: str) -> str:
        """Cleans filename and ID3 tags for MP3 player compatibility."""
        if not os.path.exists(file_path):
            return file_path

        dirname, old_filename = os.path.split(file_path)
        base_name, ext = os.path.splitext(old_filename)

        if ext.lower() != ".mp3":
            return file_path

        clean_base = clean_title(base_name) if self.clean_names else base_name
        new_filename = clean_base + ext
        new_path = os.path.join(dirname, new_filename)

        # Update ID3 tags
        try:
            tags = EasyID3(file_path)
            if "title" in tags and tags["title"]:
                tags["title"] = clean_title(tags["title"][0]) if self.clean_names else tags["title"][0]
            tags.save()
        except Exception:
            pass

        # Safely rename if different
        if new_path != file_path:
            if os.path.exists(new_path):
                # Avoid collision by removing temporary duplicate
                try:
                    os.remove(new_path)
                except OSError:
                    pass
            try:
                os.rename(file_path, new_path)
                return new_path
            except OSError as e:
                self.log(f"⚠️ Could not rename {old_filename}: {e}")

        return file_path

    def download(self, url: str) -> dict:
        """
        Downloads a single track or playlist from YouTube / YouTube Music.
        Returns a summary dictionary with counts and status.
        """
        ffmpeg_ok, ffmpeg_res = verify_ffmpeg()
        if not ffmpeg_ok:
            self.log(f"❌ FFmpeg missing: {ffmpeg_res}")
            return {"success": False, "error": f"FFmpeg not found. {ffmpeg_res}"}

        archive_file = os.path.join(self.output_dir, ".download_archive.txt") if self.use_archive else None

        postprocessors = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": self.bitrate,
            }
        ]

        if self.embed_art:
            postprocessors.extend([
                {"key": "FFmpegThumbnailsConvertor", "format": "jpg"},
                {"key": "EmbedThumbnail", "already_have_thumbnail": False},
            ])

        postprocessors.append({"key": "FFmpegMetadata", "add_metadata": True})

        def ytdl_progress_hook(d):
            if self.is_cancelled:
                raise Exception("Download cancelled by user.")

            status = d.get("status")
            if status == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes") or 0
                pct = (downloaded / total * 100) if total > 0 else 0
                speed = d.get("speed") or 0
                eta = d.get("eta") or 0

                payload = {
                    "status": "downloading",
                    "filename": os.path.basename(d.get("filename", "")),
                    "percent": round(pct, 1),
                    "speed_str": f"{speed / 1024 / 1024:.2f} MB/s" if speed else "N/A",
                    "eta_str": f"{eta}s" if eta else "N/A",
                }
                if self.progress_callback:
                    self.progress_callback(payload)

            elif status == "finished":
                payload = {
                    "status": "converting",
                    "filename": os.path.basename(d.get("filename", "")),
                    "percent": 100.0,
                }
                if self.progress_callback:
                    self.progress_callback(payload)

        ydl_opts = {
            "format": "bestaudio/best",
            "ffmpeg_location": ffmpeg_res,
            "outtmpl": os.path.join(self.output_dir, "%(title)s.%(ext)s"),
            "windowsfilenames": True,
            "ignoreerrors": True,
            "nooverwrites": True,
            "writethumbnail": self.embed_art,
            "postprocessors": postprocessors,
            "postprocessor_args": {
                "ExtractAudio": ["-id3v2_version", "3"],
            },
            "progress_hooks": [ytdl_progress_hook],
            "quiet": True,
            "no_warnings": False,
        }

        if archive_file:
            ydl_opts["download_archive"] = archive_file

        self.log(f"🎵 Connecting to YouTube / YouTube Music...")
        self.log(f"📁 Target Folder: {self.output_dir}")
        self.log(f"⚡ Audio Quality: {self.bitrate} kbps MP3 (ID3v2.3, JPEG Artwork)")

        count_before = len(glob.glob(os.path.join(self.output_dir, "*.mp3")))

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "Download") if info else "Download"

            # Post-clean files in output directory
            all_mp3s = glob.glob(os.path.join(self.output_dir, "*.mp3"))
            for mp3_path in all_mp3s:
                self._post_process_file(mp3_path)

            # Clean any leftover .webp or temp images
            for junk in glob.glob(os.path.join(self.output_dir, "*.webp")) + glob.glob(os.path.join(self.output_dir, "*.webm")):
                try:
                    os.remove(junk)
                except OSError:
                    pass

            count_after = len(glob.glob(os.path.join(self.output_dir, "*.mp3")))
            newly_added = count_after - count_before

            self.log(f"✅ Finished! {count_after} total tracks in folder ({newly_added} newly downloaded).")
            return {
                "success": True,
                "title": title,
                "total_tracks": count_after,
                "newly_downloaded": newly_added,
                "output_dir": self.output_dir,
            }

        except Exception as e:
            err_msg = str(e)
            self.log(f"❌ Error during download: {err_msg}")
            return {"success": False, "error": err_msg}
