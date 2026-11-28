---
name: reel-animation-styles
description: Make 9:16 Hindi YouTube Shorts / Instagram Reels in 10 viral code-animation styles (globe arcs, turntable, hologram, flat cartoon, 3D map route, billboard, ink doodle, glow world, 3D teardown, iceberg dive) as a single HTML/Three.js page rendered frame-by-frame to MP4. Use when the user asks for a reel/short "in X style", an animated explainer reel, or a random viral-style reel for the channel कथा और रहस्य.
---

# Reel Animation Styles (कथा और रहस्य)

Every reel = ONE self-contained `reel.html` (HTML + CSS + Canvas/Three.js) whose picture depends ONLY on time `t`.
`scripts/render.mjs` opens it headless, calls `window.renderAt(t)` for every frame, screenshots, and ffmpeg joins the frames into an MP4.
No paid API, no AI video model, no credits.

## When to use
- "Iceberg wali reel bana do", "globe style mein Babur ka safar", "koi bhi viral style mein reel".
- If no style is named, pick the one that fits the topic best (table below). If the user says "random", pick randomly, but never the same style twice in a row.

## Output contract (never break)
- 1080×1920, 30 fps, 12–25 s, H.264 MP4 + AAC, file `out/<slug>.mp4`.
- Hindi (Devanagari) text only on screen. Fonts: `Rozha One` (headings), `Yatra One` (labels), `Noto Sans Devanagari` (small text). Load them locally from `resources/fonts/` or the repo `fonts/` folder. Never use a font without Devanagari support.
- Brand strip "कथा और रहस्य" at the top, small, every frame.
- First 1 s = hook question in big text (e.g. "क्या आप जानते हैं…?"). Last 2 s = CTA ("पूरी कहानी चैनल पर 👆" or a comment question).
- Keep all text inside the safe area: x 60–1020, y 140–1560 (bottom is covered by the YouTube UI).
- Something must move every 2–3 s: a new label, a camera move, or a new object.
- Facts must be correct. If a fact is uncertain, phrase it as "मान्यता है…" or leave it out. Never invent numbers.

## The page contract
```html
<script>
  const DURATION = 18;              // seconds
  window.DURATION = DURATION;
  window.renderAt = async (t) => {  // MUST be deterministic: same t → same picture
    // draw everything for time t (no Date.now(), no requestAnimationFrame loops, no Math.random() without a seed)
  };
  window.ready = true;              // set after fonts/textures load: await document.fonts.ready
</script>
```
- Use a seeded random (mulberry32) for particles.
- Three.js: import from a local copy or `https://unpkg.com/three@0.160.0/build/three.module.js`, create the renderer with `preserveDrawingBuffer: true`, and in `renderAt` set object/camera state from `t`, then call `renderer.render(scene, camera)` once.
- Ease every movement (easeInOutCubic). No linear, robotic moves.

## Steps
1. Read `resources/styles.md` and choose a style. Write a 5–8 beat plan (time → what is on screen) and show it to the user in 5 lines.
2. Write `reels/<slug>/reel.html` following the page contract and the style recipe.
3. Preview: `node scripts/render.mjs reels/<slug>/reel.html out/<slug>.mp4 --preview 1,5,10,15` (saves PNG stills). Look at the stills and fix overlapping text, cut-off labels, empty frames.
4. Full render: `node scripts/render.mjs reels/<slug>/reel.html out/<slug>.mp4`.
5. Sound (optional): `--audio music.mp3` mixes music at -18 dB. Whoosh on each beat if `sfx/whoosh.wav` exists.
6. Check: `ffprobe` duration, every frame has text inside the safe area, nothing is blank. Give the user the MP4 path and a Hindi title + description + 5 hashtags.

## Style picker
| Topic | Best style |
|---|---|
| Journey, war route, trade route | 01 Globe Arcs / 05 3D Map Route |
| One object (Kohinoor, trishul, sword) | 02 Turntable / 09 3D Teardown |
| Fort, temple, city plan | 03 Hologram |
| Funny fact, everyday science | 04 Flat Cartoon / 07 Ink Doodle |
| Promo of the next video | 06 Billboard |
| Myth, magic, divine weapon | 08 Glow World |
| "Levels" of mystery, deep facts | 10 Iceberg Dive |

## Do not
- Do not use copyrighted characters, logos or real people's photos.
- Do not put text on the bottom 360 px.
- Do not let the agent "screen record" in real time. Always render frame by frame with `renderAt(t)`.
