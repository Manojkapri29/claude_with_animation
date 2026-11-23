# 📖 Poori Guide: shuru se end tak animated video kaise banaye

Ye guide bilkul naye user ke liye hai. Har step ke saath bataya hai **kya karna hai**, **kaunsi command** chalani hai aur **kaise check karna hai ki sahi hua**.

Short raasta: sab steps ek saath chalane ke liye `./make_video.sh <project-name>` chalao. Script har step par rukegi aur batayegi aage kya karna hai.

---

## Step 0 — Ek baar ki tayyari (15–20 min)

**Chahiye:** Mac ya Linux, Python 3.10+, `ffmpeg`, `git`. (Mac par: `brew install python ffmpeg git`)

```bash
git clone https://github.com/Manojkapri29/claude_with_animation
cd claude_with_animation
./setup.sh
. .venv/bin/activate
```
✅ Check: `python -c "import skia, faster_whisper; print('ok')"` → `ok` aana chahiye.

Claude se karwana ho to: folder ko **Claude Code** (terminal ya VS Code extension) mein kholo. `CLAUDE.md` aur skill apne aap load ho jayenge.

---

## Step 1 — Narration taiyaar karo (10–30 min)

Video ki jaan narration hai. Teen raaste:
1. **Apni aawaz mein record karo** (phone par bhi chalega, shaant kamre mein).
2. **NotebookLM / Gemini Audio Overview** jaisi tool se audio banao.
3. **TTS** (jaise Chatterbox) se. Voice clone sirf apni ya ijazat wali aawaz ka.

Tips:
- 8–10 min ki narration YouTube ke liye accha hai.
- Agar do aadhi-aadhi audio hain, to pehle socho kahani ka kram kya hoga (kaunsa hissa pehle, kaunsa hissa dohraya ja raha hai).
- Audio ko `.wav` mein badlo: `ffmpeg -i voice.mp3 -ac 1 -ar 24000 voice.wav`

---

## Step 2 — Naya project banao (1 min)

```bash
cp -r examples/mughal_panipat projects/my_video
rm projects/my_video/words_final.json projects/my_video/seg_starts.json
mkdir -p projects/my_video/src
cp ~/Downloads/voice.wav projects/my_video/src/
export CWA_PROJECT=projects/my_video
```

---

## Step 3 — Narration ka timeline (SEGMENTS) likho (5 min)

`projects/my_video/scenes.py` kholo. Sabse upar `SEGMENTS` mein batao ki audio ke kaunse hisse final video mein kahan aayenge:

```python
def TA(s): return s                      # ek hi audio ho to itna kaafi
END = 600.0                              # final video kitne second ki hogi (narration + 2 sec)
SEGMENTS = [('voice.wav', 0.0, 598.0, 0.0)]   # (file, start, end, final video mein kahan)
```
Do audio jodni ho to Mughal example dekho: usme 3 tukde jode gaye hain.

---

## Step 4 — Transcript nikalo (5–10 min)

```bash
python tools/transcribe.py
```
Ye `words_final.json` (har shabd ka time) aur `seg_starts.json` (har vaakya kahan shuru hota hai) banata hai.

✅ Check: file khol kar dekho ki shabdon ke saath time aa raha hai.

⚠️ **Facts check karo.** Narration mein galat saal ya galat naam ho to screen par sahi likhna (date badge) aur YouTube description mein correction daalna.

---

## Step 5 — Kahani ko "beats" mein todo (30–60 min, sabse creative step)

Transcript padh kar har 5–25 second ke idea ka ek **beat** banao. Har beat ka:
- **start time** (transcript se)
- **act function** (us waqt screen par kya hil raha hai)
- **background** (`bg_land('battle')`, `bg_court()`, `parchment_bg()` ...)
- **camera** (start aur end: x, y, zoom)
- **color grade**, **particles** (dust, rain, embers, sparkle)
- **cards** (chapter, date, naam, pop text)

Example beat:
```python
def a_battle(cv, c):
    t, p = c['t'], c['bp']                 # bp = 0..1 beat progress
    army(cv, 1100, 2300, 1010, 5, t, 'lodi', facing=-1, march=1.0)
    wagon_wall(cv, -100, 760, 1010, t, link=1.0, gunners=True, fire_t=c['bt'])

BEATS = [
  (TA(120.0), a_battle, lambda: bg_land('battle'), ((900,780,1.1),(1000,760,1.2)), '#ff7043', 'dust',
   [('date', 'अप्रैल 1526 • पानीपत', 1.0, 5.0)]),
]
```

Sabse aasaan tareeka: **Claude Code se bolo** "transcript padh kar 40 beats wala scenes.py likho, Mughal example jaisa". Uske baad har beat check karo.

Naye character chahiye to `cwa/mengine.py` mein `LOOKS` mein jodo (rang, pagdi/helmet, dadhi, robe).

---

## Step 6 — Preview dekho aur sudhaaro (15–30 min)

```bash
python cwa/render_long.py frames 10,45,90,150,240,330
open projects/my_video/out/sheet.jpg      # Mac
```
Har frame dhyaan se dekho:
- character ka sir ya pair kat raha hai? → `cwa/render_long.py` mein `FOCUS` points theek karo
- fauj neeche kaali patti mein chhup rahi hai? → act ka naam `GROUNDY` set mein daalo
- text upar-neeche takra raha hai? → card ka time ya position badlo
- frame mein sirf khaali aasmaan hai? → camera ka y/zoom badlo

Keyword captions ke liye `cwa/render_long.py` mein `KEYS` list badlo (transcript ki spelling → screen par dikhne wala saaf shabd).

---

## Step 7 — Sound effects (optional, 5 min)

```bash
export ELEVENLABS_API_KEY=apni_key        # key kabhi git mein mat daalna
python tools/make_sfx.py                  # sfx_list.txt ki har line se ek aawaz
```
Fir `cwa/render_long.py` ke `build_audio()` mein batao kaunsi aawaz kis beat par aaye: `put(time, 'cannon', 0.4)`. Ambience ke liye `bed(start, end, 'wind', 0.1)`.
Key nahi hai? Koi baat nahi, video bina SFX ke banegi (music aur narration rahenge).

---

## Step 8 — Final render (1–1.5 ghanta)

```bash
nohup python cwa/render_long.py full > render.log 2>&1 &
tail -f render.log                        # progress: out/progress_*.txt
```
✅ Check (bahut zaroori):
```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 projects/my_video/out/final_raw.mp4
ffmpeg -i projects/my_video/out/final_raw.mp4 -af ebur128 -f null - 2>&1 | grep -A1 Integrated   # ~ -14 LUFS
ffmpeg -i projects/my_video/out/final_raw.mp4 -vf blackdetect=d=1 -an -f null - 2>&1 | grep black
```
Video poori ek baar khud dekho.

---

## Step 9 — Reels (10 min)

`reels_config.py` mein 3 dumdaar hisse chuno (45–65 sec, vaakya ki shuruaat se):
```python
REELS = [('reel1-hook', 46.4, 105.6, ['12 साल का बादशाह', 'रगों में तैमूर और चंगेज़ का ख़ून'])]
```
```bash
CWA_FINAL=projects/my_video/out/final_raw.mp4 python cwa/reels.py
```

---

## Step 10 — Quiz (20–40 min)

1. `quiz_data.py` mein 5 sawaal likho. **Har jawab Google se double-check karo.**
2. Narrator ki 10–15 sec ki saaf awaaz `projects/my_video/voice_ref.wav` mein rakho (sirf apni ya ijazat wali).
3. Chatterbox install karo: `pip install chatterbox-tts` (3 GB, ek baar).
```bash
python cwa/tts.py          # har sawaal-jawab ki aawaz
python cwa/quiz.py 0       # quiz video (1 = doosra quiz)
```
✅ Har line sun kar dekho. Koi shabd ladkhadaye to uski wav delete karke `tts.py` dobara chalao.

---

## Step 11 — Thumbnails (10 min, bilkul free)

**Option A — AI art apne aap (sabse aasaan):** `thumbs_config.py` mein `ART` mein har thumbnail ka English prompt likho (log + scene, **koi text nahi**), aur `SPEC` mein Hindi text.
```bash
python tools/thumb_art.py          # free FLUX.1 Krea (Hugging Face) se art -> out/thumbs/art1.png ...
python cwa/thumbs_9x16.py          # Shorts ke liye 9:16
python tools/thumb_art.py --wide   # 16:9 ke liye landscape art
python cwa/thumbs_16x9.py          # lambi video ke liye 16:9
```
**Mac (M1/M2/M3/M4, 16 GB RAM, ~20 GB free disk) hai?** `tools/install_mflux_mac.command` double-click karo: mflux + Z-Image Turbo install ho jayega, phir `thumb_art.py` apne aap local chalega — **unlimited, offline, free**.
Nahi to Hugging Face ka free GPU quota roz ka hota hai. Zyada chahiye to free HF account ka token: `export HF_TOKEN=hf_...`
Pasand nahi aaya? Prompt badlo ya sirf wahi number dobara: `python tools/thumb_art.py 3`

**Option B — apni image:** Gemini/koi bhi image `out/thumbs/art1.png` naam se rakho (chhoti ho to `python cwa/upscale.py in.png art1.png`), phir upar wali do commands.

Tip: AI se image mein text mat likhwao, Hindi galat aati hai. Text scripts khud lagati hain.

## Step 12 — Upload (10 min)

- Title: hook wala, 60–70 characters. Description: chapters (0:00 ...), sudhaar (agar koi), sawaal for comments, hashtags.
- Lambi video aur Shorts alag-alag din schedule karo (jaise roz 1 baje).
- Shorts ke "Related video" mein lambi video link karo.

---

## Kitna time lagega? (pehli video)

| Kaam | Time |
|---|---|
| Setup (ek baar) | 20 min |
| Narration + transcript | 30–40 min |
| Beats likhna + preview | 1–2 ghanta |
| Render | 1–1.5 ghanta (aap doosra kaam karo) |
| Reels + Quiz + Thumbnails | 45–60 min |

Doosri video se aadha time lagta hai, kyunki characters aur backgrounds pehle se bane hote hain.

## Aam galtiyan

| Dikkat | Hal |
|---|---|
| Hindi akshar toote hue | `fonts/` folder ki files hain ya nahi check karo; Pillow 10+ chahiye (RAQM) |
| Render beech mein band | memory kam hai, ek saath doosra bhaari kaam mat chalao |
| Aawaz chhoti | final file par `ffmpeg -af loudnorm=I=-14` |
| Quiz ki aawaz robotic | `voice_ref.wav` saaf aur 10–15 sec ka rakho, background music ke bina |
