#!/bin/bash
# Free, unlimited, offline AI images on your Mac (mflux + Z-Image Turbo). Double-click to run.
cd "$(dirname "$0")"
echo "== Mac check =="
RAM=$(( $(sysctl -n hw.memsize) / 1073741824 )); DISK=$(df -g ~ | awk 'NR==2{print $4}')
echo "RAM: ${RAM} GB   Free disk: ${DISK} GB   Chip: $(uname -m)"
[ "$(uname -m)" != "arm64" ] && { echo "Apple Silicon (M1/M2/M3/M4) chahiye. Ruk raha hun."; read; exit 1; }
[ "$RAM" -lt 16 ] && echo "⚠️  16 GB se kam RAM: chalega par slow hoga (6-bit/4-bit use karenge)."
[ "$DISK" -lt 20 ] && { echo "⚠️  Kam se kam 20 GB free disk chahiye. Jagah banao phir dobara chalao."; read; exit 1; }
command -v uv >/dev/null || { echo "== uv install =="; curl -LsSf https://astral.sh/uv/install.sh | sh; export PATH="$HOME/.local/bin:$PATH"; }
export PATH="$HOME/.local/bin:$PATH"
echo "== mflux install =="; uv tool install --upgrade mflux --with hf_transfer
Q=8; [ "$RAM" -lt 16 ] && Q=4
echo "== Test image (pehli baar model download hoga, 10-30 min) =="
mflux-generate-z-image-turbo --prompt "cinematic historical film still, young Timurid prince in jeweled turban, golden hour rim light, 85mm, no text" \
  --width 768 --height 1344 --steps 9 --seed 7 -q $Q --output test-thumb-art.png && echo "✅ Ho gaya: $(pwd)/test-thumb-art.png" && open test-thumb-art.png
echo "$Q" > .quant; echo; echo "Claude ko bolo: 'local ho gaya'"; read -p "Enter dabao band karne ke liye..."
