# claude_with_animation — instructions for Claude

This repo turns a narration audio into a 2D animated video (plus Reels, quiz Shorts, thumbnails) with code only.
When the user asks for a video, follow `.claude/skills/animated-history-video/SKILL.md`.

House rules:
- Talk to the user in Hinglish if they write Hinglish.
- Never commit audio, voice references, API keys or rendered videos (see .gitignore).
- Preview with `python cwa/render_long.py frames ...` and look at `out/sheet.jpg` before any full render.
- Full renders are slow (~70 min for 10 min of video on 2 CPU workers); run them in the background.
- Verify output: duration, loudness (`ffmpeg -af ebur128`), black frames, and a few sampled frames.
