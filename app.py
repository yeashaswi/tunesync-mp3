#!/usr/bin/env python3
import os
import sys
import argparse

from core.downloader import PlaylistDownloader
from core.ffmpeg_finder import verify_ffmpeg

def interactive_mode():
    print("\n" + "=" * 60)
    print("🎵 TuneSync MP3 - Universal Playlist & Song Downloader")
    print("=" * 60)

    ffmpeg_ok, ffmpeg_res = verify_ffmpeg()
    if not ffmpeg_ok:
        print(f"\n❌ Error: FFmpeg is not installed or not in PATH.")
        print(f"👉 {ffmpeg_res}\n")
        sys.exit(1)

    try:
        url = input("\n🔗 Enter YouTube or YouTube Music URL: ").strip()
        while not url:
            url = input("URL cannot be empty. Please enter a valid URL: ").strip()

        print("\n🎚️ Select Audio Quality:")
        print("  1) 192 kbps (Recommended — ~40% smaller, indistinguishable from source)")
        print("  2) 320 kbps (Maximum MP3 bitrate)")
        print("  3) 160 kbps (Compact — ~50% smaller)")
        print("  4) 128 kbps (Ultra Light)")
        quality_choice = input("Choice [default 1]: ").strip()
        bitrate_map = {"1": "192k", "2": "320k", "3": "160k", "4": "128k"}
        bitrate = bitrate_map.get(quality_choice, "192k")

        default_folder = "My Music"
        folder = input(f"\n📁 Output folder name [default: {default_folder}]: ").strip()
        if not folder:
            folder = default_folder

        clean_titles = input("\n✨ Clean song titles (remove video noise & numbers)? [Y/n]: ").strip().lower() != "n"
        embed_art = input("🖼️ Embed JPEG cover art & ID3v2.3 tags? [Y/n]: ").strip().lower() != "n"

        print("\n" + "-" * 60)
        print("Starting download...")
        print("-" * 60)

        downloader = PlaylistDownloader(
            output_dir=folder,
            bitrate=bitrate,
            clean_names=clean_titles,
            embed_art=embed_art,
        )

        res = downloader.download(url)
        if res.get("success"):
            print("\n🎉 All done! You can now copy the folder directly to your MicroSD card or MP3 player.")
            print(f"📂 Location: {os.path.abspath(folder)}")
        else:
            print(f"\n❌ Download failed: {res.get('error')}")

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description="TuneSync MP3: Download YouTube & YouTube Music tracks/playlists formatted cleanly for hardware MP3 players & MicroSD cards.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py "https://music.youtube.com/playlist?list=..."
  python app.py "https://www.youtube.com/watch?v=..." -b 320k -o "Rock Playlist"
  python app.py --web
  python app.py (launches interactive wizard)
        """
    )
    parser.add_argument("url", nargs="?", help="YouTube or YouTube Music playlist or track URL")
    parser.add_argument("-b", "--bitrate", default="192k", choices=["128k", "160k", "192k", "320k"], help="Audio bitrate (default: 192k)")
    parser.add_argument("-o", "--output", default="downloads", help="Output directory path (default: downloads)")
    parser.add_argument("--no-clean", action="store_true", help="Do not clean video titles or strip numbering")
    parser.add_argument("--no-art", action="store_true", help="Do not embed album cover artwork")
    parser.add_argument("--no-archive", action="store_true", help="Do not use download archive for resuming")
    parser.add_argument("--web", action="store_true", help="Launch local Web UI")
    parser.add_argument("--port", type=int, default=5000, help="Web UI port (default: 5000)")

    args = parser.parse_args()

    if args.web:
        from web_app import start_server
        start_server(port=args.port, open_browser=True)
        return

    if not args.url:
        interactive_mode()
        return

    downloader = PlaylistDownloader(
        output_dir=args.output,
        bitrate=args.bitrate,
        clean_names=not args.no_clean,
        embed_art=not args.no_art,
        use_archive=not args.no_archive,
    )

    res = downloader.download(args.url)
    if not res.get("success"):
        sys.exit(1)

if __name__ == "__main__":
    main()
