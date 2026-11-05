#!/usr/bin/env python3
import os
import glob
import subprocess
import tempfile
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Favourite Songs")
FFMPEG = "/opt/homebrew/bin/ffmpeg"

def optimize_file(path):
    orig_size = os.path.getsize(path)
    dirname, filename = os.path.split(path)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False, dir=dirname) as tmp:
        tmp_name = tmp.name

    cmd = [
        FFMPEG, "-y", "-v", "error",
        "-i", path,
        "-map", "0:a",
        "-map", "0:v?",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        "-c:v", "copy",
        "-id3v2_version", "3",
        tmp_name
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and os.path.exists(tmp_name) and os.path.getsize(tmp_name) > 0:
            new_size = os.path.getsize(tmp_name)
            os.replace(tmp_name, path)
            return True, orig_size, new_size, filename
        else:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)
            return False, orig_size, orig_size, f"{filename} (ffmpeg error: {res.stderr})"
    except Exception as e:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        return False, orig_size, orig_size, f"{filename} (exception: {e})"

def main():
    files = sorted(glob.glob(os.path.join(FOLDER, "*.mp3")))
    total_files = len(files)
    if not files:
        print("No MP3 files found.")
        return

    print(f"Starting 192k optimization on {total_files} files...")
    initial_total = sum(os.path.getsize(f) for f in files)
    final_total = 0
    success_count = 0

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(optimize_file, f): f for f in files}
        for future in as_completed(futures):
            ok, orig_sz, new_sz, name = future.result()
            if ok:
                success_count += 1
                final_total += new_sz
                print(f"✔ [{success_count}/{total_files}] {name}: {orig_sz/(1024*1024):.1f}MB -> {new_sz/(1024*1024):.1f}MB")
            else:
                final_total += orig_sz
                print(f"✘ Failed: {name}")

    saved_mb = (initial_total - final_total) / (1024 * 1024)
    print("\n" + "="*50)
    print(f"Successfully optimized: {success_count}/{total_files} files")
    print(f"Initial size: {initial_total/(1024*1024):.1f} MB")
    print(f"Final size:   {final_total/(1024*1024):.1f} MB")
    print(f"Space saved:  {saved_mb:.1f} MB ({(saved_mb/(initial_total/(1024*1024)))*100:.1f}% reduction)")
    print("="*50)

if __name__ == "__main__":
    main()
