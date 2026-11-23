const ERA_BG = ['#f3c98b', '#26315f', '#f3ead6'];
function pieceCam(era, t) { return null; }
const SUNP = () => [LX(0.72), LY(0.3), 105 * UNIT];
const STARP = () => [LX(0.66), LY(0.24), 70 * UNIT];
const CROWNP = () => [LX(0.5), LY(0.2), 1.0 * UNIT];
function star5Pts(x, y, r) { const P = []; for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, rr = i % 2 ? r * 0.45 : r; P.push([x + Math.cos(a) * rr, y + Math.sin(a) * rr]); } return resample(P, true, 6); }
function crownPts(x, y, s) { const w = 150 * s, h = 110 * s; return resample([[x - w, y + h * 0.5], [x - w, y - h * 0.2], [x - w * 0.55, y + h * 0.1], [x - w * 0.3, y - h * 0.7], [x, y - h * 0.05], [x + w * 0.3, y - h * 0.7], [x + w * 0.55, y + h * 0.1], [x + w, y - h * 0.2], [x + w, y + h * 0.5]], true, 6); }
const BRIDGES = [
  { tc: TIMELINE.morphs[0], A: () => { const [x, y, r] = SUNP(); return { P: ellipsePts(x, y, r, r, 0, 64), c: PAL.yellow }; }, B: () => { const [x, y, r] = STARP(); return { P: star5Pts(x, y, r), c: '#fff3c4' }; } },
  { tc: TIMELINE.morphs[1], A: () => { const [x, y, r] = STARP(); return { P: star5Pts(x, y, r), c: '#fff3c4' }; }, B: () => { const [x, y, s] = CROWNP(); return { P: crownPts(x, y, s), c: '#e9b53a' }; } },
];
