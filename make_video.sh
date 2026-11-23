#!/bin/bash
# One-command guided pipeline: ./make_video.sh <project-name>
# Runs every step in order and pauses where you need to do something by hand.
set -e
cd "$(dirname "$0")"
[ -d .venv ] && . .venv/bin/activate
NAME="${1:?Usage: ./make_video.sh <project-name>}"
P="projects/$NAME"
export CWA_PROJECT="$P"
pause() { echo; echo "👉 $1"; read -r -p "   Ho jaye to Enter dabao... " _; }
step() { echo; echo "==================== $1 ===================="; }

step "1/9 Project folder"
if [ ! -d "$P" ]; then
  cp -r examples/mughal_panipat "$P"
  rm -f "$P/words_final.json" "$P/seg_starts.json"
  mkdir -p "$P/src"
  echo "Naya project bana: $P (Mughal example se copy)"
fi
pause "Apni narration .wav file(s) '$P/src/' mein rakho."

step "2/9 Timeline"
pause "'$P/scenes.py' mein SEGMENTS aur END set karo (GUIDE.md Step 3)."

step "3/9 Transcript"
python tools/transcribe.py
pause "Transcript padh kar facts check karo. Galat saal/naam ho to note karo (GUIDE.md Step 4)."

step "4/9 Beats"
pause "'$P/scenes.py' mein BEATS likho, ya Claude Code se likhwao (GUIDE.md Step 5)."

step "5/9 Preview"
while true; do
  python cwa/render_long.py frames "${PREVIEW_AT:-10,60,120,240,360,480}"
  echo "Preview bana: $P/out/sheet.jpg"
  (command -v open >/dev/null && open "$P/out/sheet.jpg") || true
  read -r -p "   Sab theek dikh raha hai? (y = aage chalo / n = scenes.py sudhaar ke dobara dekho) " ok
  [ "$ok" = "y" ] && break
done

step "6/9 Sound effects (optional)"
if [ -n "$ELEVENLABS_API_KEY" ]; then python tools/make_sfx.py; else echo "ELEVENLABS_API_KEY nahi mila: SFX skip (video bina SFX ke banegi)."; fi

step "7/9 Final render (1-1.5 ghanta)"
python cwa/render_long.py full
F="$P/out/final_raw.mp4"
echo "Duration: $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$F") sec"
ffmpeg -hide_banner -i "$F" -af ebur128 -f null - 2>&1 | grep -A1 Integrated | tail -1
echo "Black frames: $(ffmpeg -hide_banner -i "$F" -vf blackdetect=d=1:pix_th=0.05 -an -f null - 2>&1 | grep -c black_start)"
pause "Video ek baar poori dekh lo: $F"

step "8/9 Reels"
pause "'$P/reels_config.py' mein reels ke start/end aur hook text likho."
CWA_FINAL="$F" python cwa/reels.py

step "9/9 Quiz + thumbnails (optional)"
if [ -f "$P/voice_ref.wav" ] && python -c "import chatterbox" 2>/dev/null; then
  python cwa/tts.py && python cwa/quiz.py 0
else
  echo "Quiz skip: '$P/voice_ref.wav' aur 'pip install chatterbox-tts' chahiye (GUIDE.md Step 10)."
fi
if ls "$P"/out/thumbs/art*.png >/dev/null 2>&1; then python cwa/thumbs_16x9.py; else echo "Thumbnails skip: '$P/out/thumbs/art1.png' rakho (GUIDE.md Step 11)."; fi

echo; echo "✅ Ho gaya! Sab files: $P/out/"
