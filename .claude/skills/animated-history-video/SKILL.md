---
name: animated-history-video
description: Turn a narration audio (Hindi or any language) into a 2D animated story/history video with code-drawn characters, armies, maps and motion graphics, plus 9:16 Reels, quiz Shorts and thumbnails. Use when the user asks to make an animated video, reels, quiz or thumbnails with this repo.
---

# Animated history video from a narration

Everything is drawn in code (skia-python) and synced to the user's narration. No paid video generator.

## 0. Intake (ask only what you can't infer)
- Narration audio file(s). If the user has two half-stories, plan a merged story order.
- Channel name, language, how many Reels and quizzes.
- Never clone a voice unless it is the user's own or they have permission.

## 1. New project
```bash
cp -r examples/mughal_panipat projects/<name>
export CWA_PROJECT=projects/<name>
```
Put narration wavs in `projects/<name>/src/`. Delete the example's `words_final.json`, `seg_starts.json`.

## 2. Listen before you draw
- Transcribe with word times: first set `SEGMENTS` in `scenes.py`, then `python tools/transcribe.py`.
- Read the transcript. Write down every claim with its time. Fact-check dates and numbers; if the narration is wrong, fix it on screen (date badges) and tell the user to add a correction in the description.

## 3. scenes.py = the whole film
- `SEGMENTS = [(wav, start, end, position_in_final), ...]` glues narration pieces into one story.
- `BEATS = [(start, act_fn, bg_fn, ((x0,y0,zoom0),(x1,y1,zoom1)), grade_hex, particles, cards), ...]`, one beat per idea, usually 5–25 s.
- `act(cv, c)` draws the moving foreground; `c` has `t` (global s), `bt` (beat s), `bp` (0..1 progress), `bd` (beat length). World is 1920×1080.
- Cards: `('chapter', top, title)`, `('date', text, at, dur)`, `('name', name, subtitle, at)`, `('pop', text, at, dur, y)`, `('sub', text, at, dur, y)`.
- Add new characters with `LOOKS['name'] = Look(...)` in `cwa/mengine.py` (robe, hat: turban/helmet/fez/persian/redcoat/saffron, beard, mustache, tilak).

Toolbox (`cwa/mengine.py`, `cwa/engine.py`):
`draw_person(cv, look, x, y, t, scale, facing, mouth, gesture, look_dx, emotion)`, `rider`, `army(cv, x0, x1, y, rows, t, kind, facing, s, march, weapon, fall)`, `cavalry`, `draw_elephant`, `draw_cannon(... fire=seconds_since_shot)`, `wagon_wall`, `draw_flag`, `draw_throne`, `draw_crown2`, `draw_diamond`, `draw_tent`, `draw_chess`/`draw_pawn`, `draw_map(cv, t, route, empire, crack, shrink, highlight=[places])`, backgrounds `bg_land(kind)` (fergana/snow/kabul/dusk/battle/river/fire/night), `bg_court`, `bg_palace_night`, `parchment_bg`, effects `draw_flames`, `rays`, `glow`, `Particles(kind)`, `draw_text`.

## 4. Preview, look, fix
```bash
python cwa/render_long.py frames 12,40,95,210
```
Open `out/sheet.jpg` and actually look: heads cut off, armies hidden under the letterbox, text overlapping, empty sky. Fix framing with `FOCUS` points (per act) and `GROUNDY` (army scenes) in `cwa/render_long.py`. Pick caption keywords in `KEYS` (transcript spelling → clean display text).

## 5. Sound
- Optional realistic SFX: write `sfx_list.txt` (`name|seconds|prompt`), then `ELEVENLABS_API_KEY=... python tools/make_sfx.py`. Missing effects are skipped silently.
- Place effects per beat in `build_audio()` (`put(time, name, gain)`, `bed(t0, t1, name, gain)` for ambience). Keep narration on top (ducking is built in).

## 6. Render and verify
```bash
python cwa/render_long.py full      # ~70 min for 10 min on 2 workers; run in background
ffprobe -show_entries format=duration out/final_raw.mp4
ffmpeg -i out/final_raw.mp4 -af ebur128 -f null -           # aim near -14 LUFS
ffmpeg -i out/final_raw.mp4 -vf blackdetect=d=1 -an -f null -
```
Sample 6–8 frames and look at them before delivering.

## 7. Reels, quiz, thumbnails
- Reels: edit `reels_config.py` (cut at sentence boundaries, 45–65 s, strong hook text), run `CWA_FINAL=... python cwa/reels.py`.
- Quiz: write 5 fact-checked questions in `quiz_data.py`; put a clean 10–15 s narrator sample as `voice_ref.wav`; `python cwa/tts.py` then `python cwa/quiz.py 0`. Transcribe the generated lines to catch slurred words and regenerate those.
- Thumbnails: save art crops as `out/thumbs/art{N}.png` (upscale with `cwa/upscale.py`), set text in `thumbs_config.py`, run `python cwa/thumbs_16x9.py`.

## Optional extras
- Cut-paper animated hook: `examples/mughal_panipat/hook/` is a piece for the [Animate](https://github.com/cth9191/animate) skill.
- Cinematic grade: OpenMontage `color_grade` (cinematic_warm, 0.6).
- Silence trimming: auto-editor on your own recordings.
