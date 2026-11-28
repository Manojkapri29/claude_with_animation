# 10 style recipes

Each recipe covers the look, the engine, the beats, and an example topic for कथा और रहस्य.

## 01 Globe Arcs
- **Look:** dark navy space, a glowing dotted Earth slowly rotating, golden arcs flying from city to city, a big counter at the top ("25 देश").
- **Engine:** Three.js sphere with a points texture (or a canvas orthographic globe). Arcs are QuadraticBezier tubes whose drawRange grows with t. Cities are pulsing dots with Hindi labels as HTML overlays positioned by projecting 3D → 2D.
- **Beats:** 0–1 s hook · 1–3 s globe spins to the start city · then 1 arc every 2 s with a label · last 2 s the full path plus CTA.
- **Example:** "बाबर का सफ़र: फ़रग़ना → काबुल → पानीपत".

## 02 Turntable
- **Look:** black studio, the object on a round pedestal slowly turning 360°, thin leader lines pointing to parts with small stat labels ("105 कैरेट", "मूल: गोलकुंडा").
- **Engine:** Three.js. Build the object from primitives (Lathe/Extrude) with a studio light rig: key + rim + soft floor reflection. `rotation.y = t * 0.6`.
- **Beats:** name fades in · a new label every 2.5 s · final full spin with the title.
- **Example:** "कोहिनूर हीरे का सफ़र", "त्रिशूल के तीन शूल का अर्थ".

## 03 Hologram
- **Look:** a dark room, a cyan wireframe model of a building rising out of a scan grid, scanlines and flicker, one part glowing red for a "secret".
- **Engine:** Three.js EdgesGeometry plus an additive cyan material with a scanline shader. The model is built layer by layer (`scale.y` grows with t).
- **Beats:** grid · the building grows floor by floor · the camera orbits · the red highlight reveal with a label.
- **Example:** "कैलाश मंदिर का ब्लूप्रिंट", "गोलकुंडा किले की गुप्त सुरंग".

## 04 Flat Cartoon
- **Look:** flat-vector office or village scene, bold outlines, one character with big expressions, a chart or object popping in.
- **Engine:** SVG or Canvas 2D. Animate the character's limbs with sin(t) rigs. Text arrives in speech bubbles.
- **Beats:** problem · reaction · twist · punchline.
- **Example:** "चाणक्य की 3 बातें जो आज भी काम करती हैं".

## 05 3D Map Route
- **Look:** white or clay-style 3D city or mountain blocks seen from a tilted top view, a thick blue route line drawing itself, the camera following the moving dot, pins with labels.
- **Engine:** Three.js. Make a block grid or a heightmap terrain. The route is a CatmullRom curve; the camera follows `curve.getPoint(p)` with a lag.
- **Beats:** start pin · route draws · stops pop up · the final destination zooms out.
- **Example:** "केदारनाथ यात्रा का पूरा रास्ता", "कैलाश मानसरोवर परिक्रमा".

## 06 Billboard
- **Look:** a night highway with car light trails, a big glowing billboard showing the message, reflections on a wet road.
- **Engine:** Three.js road plane plus streak particles moving toward the camera. The billboard is a plane with a CanvasTexture of Hindi text that changes per beat.
- **Beats:** the camera dollies toward the billboard · the message changes 3 times · the last one is the CTA.
- **Example:** promo: "नई कहानी: हवेली नंबर 13, आज रात 8 बजे".

## 07 Ink Doodle
- **Look:** a hand-drawn stick figure on a light background, wobbly ink lines, a small sign above the head, objects drawn stroke by stroke.
- **Engine:** Canvas 2D. Each stroke is a path drawn by `dashOffset` progress. Jitter lines with seeded noise for a boiling-line effect at 12 fps (hold each frame for 2–3 frames).
- **Beats:** "पहले" · "फिर" · twist · lesson.
- **Example:** "फ़ोन से पहले / बाद में: पहाड़ी गाँव की शाम".

## 08 Glow World
- **Look:** a purple-blue dreamy isometric world, glowing crystals and a portal, floating particles, a cute or divine object with a face.
- **Engine:** Three.js with UnrealBloomPass, emissive materials, fog. The camera orbits slowly. Particles drift on seeded sin paths.
- **Beats:** the portal opens · an object rises · a power reveal · the title.
- **Example:** "सुदर्शन चक्र की शक्ति", "अक्षय पात्र का रहस्य".

## 09 3D Teardown
- **Look:** an object on black, its layers separating vertically (exploded view), each layer labelled on the right ("कुंजी", "स्विच", "प्लेट").
- **Engine:** Three.js. Each layer is a mesh whose `y = base + spread(t) * index`, with a slow rotation. Labels are HTML aligned to each layer.
- **Beats:** whole object · explode layer by layer · labels · collapse back with the title.
- **Example:** "मंदिर के शिखर की परतें", "तलवार कैसे बनती थी".

## 10 Iceberg Dive
- **Look:** the iceberg tip above a calm sea, the camera sinks underwater, each level gets darker, a label at each depth plus a depth meter.
- **Engine:** Canvas 2D or Three.js. One tall world; camera `y` eases from level to level. Bubbles and god rays use a seeded random.
- **Beats:** the tip (the famous fact) · 4–6 levels, each 2.5 s · the deepest = the most mysterious, in yellow · a CTA question.
- **Example:** "भारत के रहस्यों का आइसबर्ग" (a reference implementation in Python exists at `reel_styles/iceberg.py`).
