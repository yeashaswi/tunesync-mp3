#!/usr/bin/env bash
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:$PATH"
.venv/bin/python3 download_playlist.py
