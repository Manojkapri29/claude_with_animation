# Antigravity se viral-style reels banwane ke prompts

Ye file Google Antigravity (IDE / App / CLI) ke liye hai. Skill `.agents/skills/reel-animation-styles/` mein hai. Antigravity use apne aap pakad leta hai, ya `/reel-animation-styles` likh kar zabardasti chalwa sakte ho.

---

## 0) Ek baar ka setup (copy karke Antigravity ko do)

```
Is repo (claude_with_animation) mein setup karo:
1. `npm init -y` aur `npm i -D playwright`, phir `npx playwright install chromium`.
2. Check karo ki `ffmpeg -version` chal raha hai. Nahi chal raha to Mac par `brew install ffmpeg`.
3. `.agents/skills/reel-animation-styles/SKILL.md` padho, aur `examples/globe-arcs.html` ko
   `node .agents/skills/reel-animation-styles/scripts/render.mjs .agents/skills/reel-animation-styles/examples/globe-arcs.html out/test.mp4 --preview 1,5,10`
   se test karo. Stills dikha do.
Kuch bhi delete mat karna. Har command chalane se pehle batana.
```

Skill har project mein chahiye to folder global jagah copy kar do:
`cp -r .agents/skills/reel-animation-styles ~/.gemini/config/skills/`

---

## 1) Kisi bhi style mein reel: master prompt

```
reel-animation-styles skill use karo.
Style: <01–10 ya "random">
Topic: <topic>
Lambai: 15–18 sec, 9:16, Hindi text.
Pehle 5–8 beat ka plan dikhao (time → screen par kya). Main OK bolun tab reel.html likho,
--preview 1,5,10,15 se stills dikhao, galti theek karo, phir poora MP4 render karo.
End mein YouTube title, description aur 5 hashtags Hindi mein do.
Facts galat nahi hone chahiye. Pakka na ho to "मान्यता है" likhna.
```

---

## 2) Har style ka ready prompt

**01 Globe Arcs**
```
Style 01 Globe Arcs. Topic: "बाबर का सफ़र: फ़रग़ना से पानीपत".
Ghoomti dotted dharti, shehar se shehar tak sunehri arcs, har stop par saal aur ek line.
Reference: examples/globe-arcs.html. Isse behtar banao: asli continents ke dots (Natural Earth
110m GeoJSON ko points mein badal kar), camera zoom jo har stop ko follow kare.
```

**02 Turntable**
```
Style 02 Turntable. Topic: "कोहिनूर हीरे का सफ़र".
Kaale studio mein ghoomta hua heera (Three.js, ExtrudeGeometry se facets, MeshPhysicalMaterial
with transmission). Leader lines ke saath 4 labels: वज़न, मूल खान, पहले मालिक, आज कहाँ.
Har 2.5 sec mein naya label.
```

**03 Hologram**
```
Style 03 Hologram. Topic: "कैलाश मंदिर का ब्लूप्रिंट".
Andhere kamre mein cyan wireframe mandir, scan-grid se manzil-dar-manzil uthta hua,
scanlines aur flicker. Aakhir mein ek hissa laal glow kare: "एक ही चट्टान से तराशा".
```

**04 Flat Cartoon**
```
Style 04 Flat Cartoon. Topic: "चाणक्य की 3 बातें जो आज भी काम करती हैं".
Flat vector SVG character (bade expression), office/gaon background, speech bubbles,
har baat par ek pop-in object. Mazedaar par izzat wala tone.
```

**05 3D Map Route**
```
Style 05 3D Map Route. Topic: "केदारनाथ यात्रा का रास्ता: गौरीकुंड से मंदिर".
Clay-style 3D pahadi terrain (heightmap), neeli route line khud banti hui, camera dot ko
follow kare, stops par pin + doori (km). Doori asli honi chahiye, web se check karo.
```

**06 Billboard**
```
Style 06 Billboard. Ye meri nayi video ka promo hai: "<video title>", "<release time>".
Raat ka highway, gaadiyon ki light trails, geeli sadak par reflection, bada glowing board
jisme 3 baar message badle; aakhri message CTA.
```

**07 Ink Doodle**
```
Style 07 Ink Doodle. Topic: "फ़ोन से पहले और बाद: पहाड़ी गाँव की शाम".
Haath se bana stick figure, kaanpti ink lines (12 fps boiling effect), har cheez stroke-by-stroke
banti hui, upar chhota sign board.
```

**08 Glow World**
```
Style 08 Glow World. Topic: "सुदर्शन चक्र की शक्ति".
Baingani-neeli jaadui isometric duniya, chamakte crystal, portal, tairte particles (bloom).
Chakra portal se uthe, ghoome, roshni phaile. Copyrighted design nahi, apna original design.
```

**09 3D Teardown**
```
Style 09 3D Teardown. Topic: "मंदिर के शिखर की परतें" (ya "तलवार कैसे बनती थी").
Object kaale background par, parat-dar-parat upar-neeche khulta hua (exploded view),
har parat ke saath right side mein Hindi label, aakhir mein wapas jud jaye.
```

**10 Iceberg Dive**
```
Style 10 Iceberg Dive. Topic: "भारत के रहस्यों का आइसबर्ग".
Barf ki chotti se camera paani mein neeche jaye, har gehraai par ek rahasya (5 levels),
gehraai meter, bubbles, sabse neeche wala peela. Reference: reel_styles/iceberg.py.
```

---

## 3) Random daily reel (roz ke liye)

```
reel-animation-styles skill se aaj ki reel banao.
Style random chuno, par kal wala style nahi (out/ folder dekh kar pata karo).
Topic khud chuno: कथा और रहस्य channel (pauranik katha, Uttarakhand, itihaas, rahasya).
Pehle 3 topic idea do, main ek chununga, phir plan → preview → render.
```

## 4) Ek reel ko alag style mein dobara

```
out/<slug>.mp4 wali reel ka content same rakho, style badal kar <style> mein banao.
```

## 5) Galti theek karwane ke prompts

- `Preview mein text kat raha hai / takra raha hai. Safe area (x 60–1020, y 140–1560) mein lao.`
- `Movement robotic lag raha hai. Har move par easeInOutCubic lagao, aur 2–3 sec mein kuch naya aaye.`
- `Hindi akshar toot rahe hain. Rozha One / Yatra One / Noto Sans Devanagari local font se load karo, aur document.fonts.ready ka wait karo.`
- `Three.js kaala screen de raha hai. renderer mein preserveDrawingBuffer: true lagao aur renderAt ke andar hi render() call karo.`

---

## Dhyan rakhne ki baatein
- Ye sab **code se** banta hai, isliye koi credit nahi lagta aur reel kitni bhi baar dobara render ho sakti hai.
- Ek reel render hone mein ~2–6 min lagte hain (Three.js wali styles thodi slow hain).
- Asli logo, copyrighted characters aur real logon ki photo kabhi mat daalna.
