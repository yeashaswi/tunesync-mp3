#!/usr/bin/env python3
import os
import sys
import json
import zipfile
import threading
import io
import socket
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.parse

from core.downloader import PlaylistDownloader

# Global state for download process
DOWNLOAD_STATE = {
    "status": "idle",       # "idle", "running", "completed", "error"
    "current_track": "",
    "progress": {},
    "logs": [],
    "error": "",
    "last_folder": "",
}
STATE_LOCK = threading.Lock()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

class TuneSyncHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress noisy HTTP request logging in terminal
        return

    def send_json(self, data, status_code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/" or parsed.path == "/index.html":
            template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
            if os.path.exists(template_path):
                with open(template_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "Template index.html not found.")

        elif parsed.path == "/api/status":
            with STATE_LOCK:
                data = dict(DOWNLOAD_STATE)
            self.send_json(data)

        elif parsed.path == "/api/zip":
            with STATE_LOCK:
                folder = DOWNLOAD_STATE.get("last_folder", "")
            if not folder or not os.path.isdir(folder):
                self.send_error(404, "No downloaded music folder found to ZIP.")
                return

            # Create in-memory zip
            folder_name = os.path.basename(os.path.abspath(folder)) or "Music"
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(folder):
                    for file in files:
                        if file.endswith(".mp3"):
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(full_path, folder)
                            zf.write(full_path, rel_path)

            zip_data = zip_buffer.getvalue()
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", f'attachment; filename="{folder_name}.zip"')
            self.send_header("Content-Length", str(len(zip_data)))
            self.end_headers()
            self.wfile.write(zip_data)

        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/api/download":
            length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(length).decode("utf-8")
            try:
                body = json.loads(raw_body)
            except json.JSONDecodeError:
                self.send_json({"started": False, "error": "Invalid JSON"}, 400)
                return

            url = body.get("url", "").strip()
            if not url:
                self.send_json({"started": False, "error": "URL is required"}, 400)
                return

            bitrate = body.get("bitrate", "192k")
            folder_name = body.get("folder_name", "My Music").strip() or "My Music"
            clean_names = body.get("clean_names", True)
            embed_art = body.get("embed_art", True)

            output_dir = os.path.join(os.getcwd(), folder_name)

            with STATE_LOCK:
                if DOWNLOAD_STATE["status"] == "running":
                    self.send_json({"started": False, "error": "A download is already in progress"}, 400)
                    return

                DOWNLOAD_STATE["status"] = "running"
                DOWNLOAD_STATE["current_track"] = "Starting..."
                DOWNLOAD_STATE["progress"] = {}
                DOWNLOAD_STATE["logs"] = ["Connected to server. Initializing download engine..."]
                DOWNLOAD_STATE["error"] = ""
                DOWNLOAD_STATE["last_folder"] = output_dir

            def run_worker():
                def on_progress(p):
                    with STATE_LOCK:
                        DOWNLOAD_STATE["progress"] = p
                        if p.get("filename"):
                            DOWNLOAD_STATE["current_track"] = p["filename"]

                def on_log(msg):
                    with STATE_LOCK:
                        DOWNLOAD_STATE["logs"].append(msg)
                        # Keep last 50 logs
                        if len(DOWNLOAD_STATE["logs"]) > 50:
                            DOWNLOAD_STATE["logs"].pop(0)

                downloader = PlaylistDownloader(
                    output_dir=output_dir,
                    bitrate=bitrate,
                    clean_names=clean_names,
                    embed_art=embed_art,
                    progress_callback=on_progress,
                    log_callback=on_log,
                )

                res = downloader.download(url)
                with STATE_LOCK:
                    if res.get("success"):
                        DOWNLOAD_STATE["status"] = "completed"
                    else:
                        DOWNLOAD_STATE["status"] = "error"
                        DOWNLOAD_STATE["error"] = res.get("error", "Download failed")

            threading.Thread(target=run_worker, daemon=True).start()
            self.send_json({"started": True, "output_dir": output_dir})

        else:
            self.send_error(404, "Not Found")

def start_server(port: int = 5000, open_browser: bool = False):
    local_ip = get_local_ip()
    server_address = ("0.0.0.0", port)
    httpd = ThreadingHTTPServer(server_address, TuneSyncHandler)

    print("=" * 60)
    print("🎵 TuneSync MP3 Downloader - Web Interface")
    print(f"👉 Local Access:   http://localhost:{port}")
    print(f"📱 Mobile Access:  http://{local_ip}:{port}  (iOS Safari / Android)")
    print("=" * 60)
    print("Press Ctrl+C to stop the server.")

    if open_browser:
        import webbrowser
        threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{port}")).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 5000
    start_server(port=port)
