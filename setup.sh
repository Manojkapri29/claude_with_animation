#!/bin/bash
# One-time setup (macOS or Linux). Needs Python 3.10+, ffmpeg and git.
set -e
cd "$(dirname "$0")"
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
echo "==> Optional: Real-ESRGAN weights for thumbnail upscaling"
mkdir -p models && curl -fsSL -o models/RealESRGAN_x4plus.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth || true
echo "Done. Activate with: . .venv/bin/activate"
