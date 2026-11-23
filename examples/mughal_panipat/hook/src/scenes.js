// rider on a paper horse, facing right, at ground point (x, y)
function rider(x, y, s, k, lead) {
  const bob = Math.sin(TT * 9 + k) * 6 * s, R = 'rd' + k;
  const legA = Math.sin(TT * 9 + k) * 0.5;
  for (let i = 0; i < 4; i++) { const lx = x + (i < 2 ? -55 : 45) * s + (i % 2) * 14 * s, sw = (i % 2 ? legA : -legA);
    cut(capsulePts(lx, y - 70 * s + bob, lx + sw * 30 * s, y, 13 * s, 4), PAL.woodD, { key: R + 'l' + i, sb: 3 }); }
  cut(ellipsePts(x, y - 95 * s + bob, 85 * s, 38 * s, 0, 24), k % 2 ? PAL.wood : '#8a5a34', { key: R + 'b' });
  cut(capsulePts(x + 60 * s, y - 110 * s + bob, x + 100 * s, y - 165 * s + bob, 22 * s, 4), k % 2 ? PAL.wood : '#8a5a34', { key: R + 'n' });
  cut(ellipsePts(x + 112 * s, y - 165 * s + bob, 30 * s, 17 * s, 0.4, 16), k % 2 ? PAL.wood : '#8a5a34', { key: R + 'h' });
  cut(capsulePts(x - 80 * s, y - 105 * s + bob, x - 115 * s, y - 60 * s + bob, 10 * s, 4), PAL.ink, { key: R + 't', shadow: false });
  // rider
  cut(capsulePts(x - 5 * s, y - 120 * s + bob, x, y - 195 * s + bob, 30 * s, 4), lead ? PAL.teal : PAL.blue, { key: R + 'bd' });
  cut(ellipsePts(x, y - 220 * s + bob, 24 * s, 26 * s, 0, 18), PAL.skin2, { key: R + 'hd' });
  cut(ellipsePts(x, y - 240 * s + bob, 30 * s, 16 * s, 0, 18), '#fbf6ea', { key: R + 'tb', sb: 3 });
  if (lead) { ink([[x + 20 * s, y - 180 * s + bob], [x + 20 * s, y - 320 * s + bob]], { w: 4, color: PAL.ink, key: R + 'pole' });
    cut([[x + 20 * s, y - 320 * s + bob], [x + 95 * s + Math.sin(TT * 6) * 8 * s, y - 300 * s + bob], [x + 20 * s, y - 275 * s + bob]], '#2e7d5b', { key: R + 'fl', sb: 3 }); }
  for (let j = 0; j < 3; j++) { const u = (TT * 2 + j / 3 + k * 0.2) % 1; cut(ellipsePts(x - 120 * s - u * 120 * s, y - 10 * s - u * 30 * s, (14 + u * 26) * s, (10 + u * 14) * s, 0, 12), 'rgba(240,214,160,' + (0.8 - u * 0.7).toFixed(2) + ')', { key: R + 'du' + j, shadow: false, tear: 0.3, shade: false }); }
}
function sceneDesert() {
  const u = UNIT, [sx, sy, sr] = SUNP();
  cut(rect(-30, -30, W + 60, H + 60, 0), '#f3c98b', { key: 'skyD', shadow: false, tear: 0, shade: false, pat: pat.stripes('rgba(255,255,255,0.14)', 26, 90) });
  cut(ellipsePts(sx, sy, sr, sr, 0, 40), PAL.yellow, { key: 'sun', crayon: '#e6b23a' });
  for (let i = 0; i < 5; i++) { const bx = (LX(0.1 + i * 0.12) + TT * 30 * u) % (W + 100), by = LY(0.18 + (i % 2) * 0.06); ink([[bx - 18 * u, by], [bx - 6 * u, by - 8 * u + Math.sin(TT * 8 + i) * 4 * u], [bx, by], [bx + 6 * u, by - 8 * u + Math.sin(TT * 8 + i) * 4 * u], [bx + 18 * u, by]], { w: 3, color: PAL.ink, key: 'bird' + i }); }
  [[0.62, '#e2a25a', 'd1'], [0.72, '#d08a45', 'd2']].forEach(([fy, c, k], j) => cut([[-40, LY(fy)], [W * 0.2, LY(fy) - 70 * u], [W * 0.45, LY(fy) - 10 * u], [W * 0.7, LY(fy) - 90 * u], [W + 40, LY(fy) - 30 * u], [W + 40, H + 60], [-40, H + 60]], c, { key: k, sy: -5, pat: pat.stripes('rgba(255,255,255,0.10)', 3, 26, 0.25) }));
  // a palm and a tent: background life
  const px = LX(0.12), py = LY(0.66);
  cut(capsulePts(px, py, px + 20 * u, py - 230 * u, 16 * u, 6), PAL.woodD, { key: 'palm' });
  for (let i = 0; i < 5; i++) { const a = -2.6 + i * 0.5 + Math.sin(TT * 2 + i) * 0.05; cut(capsulePts(px + 20 * u, py - 230 * u, px + 20 * u + Math.cos(a) * 110 * u, py - 230 * u + Math.sin(a) * 60 * u + 40 * u, 14 * u, 6), PAL.green, { key: 'leaf' + i, sb: 3 }); }
  cut([[LX(0.88) - 90 * u, LY(0.69)], [LX(0.88), LY(0.69) - 110 * u], [LX(0.88) + 90 * u, LY(0.69)]], PAL.pink, { key: 'tentD', pat: pat.stripes('rgba(255,255,255,0.3)', 10, 26) });
  // the caravan crosses left to right
  const gx = LX(0.12) + TT * 120 * u;
  for (let k = 0; k < 4; k++) rider(gx - k * 260 * u, LY(0.86) - (k % 2) * 18 * u, 0.95 * u, k, k === 0);
  yearTag('1494');
  if (TT >= TIMELINE.cues.epic) tag('एक महाकाव्य', LX(0.3), LY(0.33), 92 * u, { rot: -0.04, s: popS(TIMELINE.cues.epic), fill: '#fbf6ea' });
}
function sceneFate() {
  const u = UNIT, [sx, sy, sr] = STARP();
  cut(rect(-30, -30, W + 60, H + 60, 0), PAL.navy, { key: 'night', shadow: false, tear: 0, shade: false, pat: pat.dots('rgba(255,230,180,0.12)', 4, 70) });
  const R = RNG('st'); for (let i = 0; i < 40; i++) sparkle(R.r(0, W), R.r(0, LY(0.6)), R.r(3, 8) * u * (0.6 + 0.4 * ((B + i) % 2)));
  cut(star5Pts(sx, sy, sr * (1 + 0.04 * Math.sin(TT * 6))), '#fff3c4', { key: 'fstar', crayon: '#e6c25a' });
  cut(ellipsePts(LX(0.14), LY(0.18), 46 * u, 46 * u, 0, 24), '#f6ecc8', { key: 'moon' });
  cut(ellipsePts(LX(0.14) + 20 * u, LY(0.18) - 10 * u, 40 * u, 40 * u, 0, 24), PAL.navy, { key: 'moonc', shadow: false });
  cut([[-40, LY(0.72)], [W * 0.4, LY(0.66)], [W + 40, LY(0.74)], [W + 40, H + 40], [-40, H + 40]], '#3a4a7a', { key: 'hill', sy: -4, pat: pat.stripes('rgba(255,255,255,0.06)', 3, 24, 0.3) });
  cut([[LX(0.8) - 110 * u, LY(0.75)], [LX(0.8), LY(0.75) - 140 * u], [LX(0.8) + 110 * u, LY(0.75)]], PAL.purple, { key: 'tentN', pat: pat.stripes('rgba(255,255,255,0.2)', 10, 28) });
  // campfire flicker
  const fx = LX(0.62), fy = LY(0.82);
  for (let i = 0; i < 3; i++) cut(ellipsePts(fx + (i - 1) * 14 * u, fy - 30 * u - (B % 3) * 4 * u, (16 - i * 3) * u, (40 + ((B + i) % 3) * 8) * u, 0, 14), i === 1 ? PAL.yellow : '#e8743a', { key: 'fire' + i, shadow: false, tear: 0.4 });
  cut(capsulePts(fx - 50 * u, fy, fx + 50 * u, fy - 10 * u, 12 * u, 4), PAL.woodD, { key: 'log' });
  // the boy (young Babur) looks up at the star
  const bx = LX(0.33), by = LY(0.74) + 40 * u;
  person(bx, by, 1.05 * u, { key: 'boy', shirt: PAL.teal, mood: TT < TIMELINE.cues.amb ? 'wow' : 'happy', hair: '#2b211d' });
  cut(ellipsePts(bx, by - 225 * u, 92 * u, 42 * u, 0, 22), '#fbf6ea', { key: 'turban', pat: pat.stripes('rgba(200,150,60,0.25)', 6, 18) });
  cut(ellipsePts(bx + 50 * u, by - 250 * u, 12 * u, 22 * u, 0.3, 12), '#e9b53a', { key: 'plume' });
  if (TT >= TIMELINE.cues.fate) tag('मुक़द्दर', LX(0.62), LY(0.48), 96 * u, { rot: 0.03, s: popS(TIMELINE.cues.fate + 0.1) });
  if (TT >= TIMELINE.cues.amb) tag('महत्वाकांक्षा', LX(0.6), LY(0.62), 70 * u, { rot: -0.04, s: popS(TIMELINE.cues.amb), fill: PAL.yellow });
}
const MAP = [[0.30,0.00],[0.42,0.05],[0.45,0.15],[0.60,0.20],[0.75,0.25],[0.95,0.25],[1.0,0.33],[0.85,0.38],[0.75,0.42],[0.70,0.50],[0.62,0.62],[0.55,0.78],[0.48,1.0],[0.40,0.82],[0.33,0.62],[0.28,0.50],[0.15,0.45],[0.05,0.40],[0.12,0.30],[0.22,0.25],[0.25,0.12]];
function sceneEmpire() {
  const u = UNIT, [cx, cy, cs] = CROWNP();
  cut(rect(-30, -30, W + 60, H + 60, 0), PAL.cream, { key: 'parch', shadow: false, tear: 0, shade: false, pat: pat.gingham('rgba(190,140,80,0.10)', 46) });
  const mx = LX(0.5) - 330 * u, my = LY(0.36), mw = 600 * u, mh = 620 * u;
  const P = MAP.map(([a, b]) => [mx + a * mw, my + b * mh]);
  cut(ellipsePts(mx - 60 * u, my + 140 * u, 90 * u, 70 * u, 0.3, 20), '#d8c8a0', { key: 'afg' });
  cut(P, '#e8d8b0', { key: 'india', crayon: '#c9b27a' });
  // the empire spreads: Kabul -> Panipat -> Delhi/Agra -> north India
  const spots = [[-60, 140, 70, 52], [120, 150, 70, 50], [180, 210, 90, 70], [260, 260, 120, 80], [200, 330, 140, 90], [330, 230, 110, 70]];
  spots.forEach(([dx, dy, rx, ry], i) => { const k = popS(TIMELINE.cues.map + i * 0.18); if (k <= 0) return; cut(ellipsePts(mx + dx * u, my + dy * u, rx * u * k, ry * u * k, 0.2, 20), i ? '#3f9f6a' : '#2e7d5b', { key: 'emp' + i, sb: 4 }); });
  // compass, quill and ink, wax seal: background life
  const qx = LX(0.84), qy = LY(0.78);
  for (let i = 0; i < 8; i++) { const a = i / 8 * TAU + TT * 0.2; ink([[qx, qy], [qx + Math.cos(a) * (i % 2 ? 40 : 80) * u, qy + Math.sin(a) * (i % 2 ? 40 : 80) * u]], { w: i % 2 ? 2 : 4, color: PAL.ink, key: 'cmp' + i }); }
  cut(rect(LX(0.12) - 40 * u, LY(0.76), 80 * u, 70 * u, 10 * u), PAL.ink, { key: 'inkpot' });
  cut(capsulePts(LX(0.12), LY(0.77), LX(0.12) + 70 * u, LY(0.55), 9 * u, 4), '#fbf6ea', { key: 'quill' });
  cut(ellipsePts(LX(0.2), LY(0.88), 40 * u, 38 * u, 0, 20), '#b23a3a', { key: 'seal' });
  // the crown (bridge object) settles, then shines
  cut(crownPts(cx, cy + Math.sin(TT * 3) * 4 * u, cs), '#e9b53a', { key: 'crown', crayon: '#c48a1f' });
  [-0.55, 0, 0.55].forEach((f, i) => cut(ellipsePts(cx + f * 150 * cs, cy + 18 * cs, 14 * cs, 14 * cs, 0, 12), [PAL.pink, PAL.blue, PAL.pink][i], { key: 'gem' + i, shadow: false }));
  if (TT >= TIMELINE.cues.crown) for (let i = 0; i < 6; i++) sparkle(cx + Math.cos(i + TT) * 210 * u, cy + Math.sin(i * 2 + TT) * 90 * u, (8 + (B + i) % 3 * 4) * u);
  if (TT >= TIMELINE.cues.crown) tag('मुग़ल साम्राज्य', LX(0.5), LY(0.9), 84 * u, { rot: 0.015, s: popS(TIMELINE.cues.crown), fill: '#fbf6ea' });
  yearTag('1526');
}
