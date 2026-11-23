import sys, os, math, subprocess, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import OUT, SRC, SFX, PROJECT
import numpy as np, skia
from mengine import *
import scenes as S   # your project's scenes.py
import audiofx as GR
FPS, SR = 24, 24000
os.makedirs(OUT, exist_ok=True)
W, H = 1920, 1080

# ------------------------------------------------------------------ audio
def load16(path):
    w = wave.open(path)
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    sr = w.getframerate()
    return np.interp(np.arange(int(len(a) * SR / sr)) / SR, np.arange(len(a)) / sr, a).astype(np.float32)

def build_audio():
    srcs = {}
    seg = lambda a, s, e: a[int(s * SR):int(e * SR)]
    parts = []
    for fname, s0, s1, at in S.SEGMENTS:   # (wav in src/, start, end, position in final video)
        if fname not in srcs:
            srcs[fname] = load16(os.path.join(SRC, fname))
        parts.append((at, seg(srcs[fname], s0, s1)))
    n = int((S.END + 1) * SR)
    voice = np.zeros(n, np.float32)
    for st, a in parts:
        i = int(st * SR)
        fade = np.ones(len(a), np.float32)
        k = int(0.04 * SR)
        fade[:k] = np.linspace(0, 1, k); fade[-k:] = np.linspace(1, 0, k)
        voice[i:i + len(a)] += a * fade
    voice /= np.max(np.abs(voice)) + 1e-6
    X = {}
    def snd(k):
        if k not in X:
            p_ = os.path.join(SFX, f'{k}.wav')
            if not os.path.exists(p_):   # no SFX file yet: stay silent for this effect
                X[k] = np.zeros(1, np.float32); return X[k]
            a = load16(p_); X[k] = a / (np.max(np.abs(a)) + 1e-6) * 0.9
        return X[k]
    fx = np.zeros(n, np.float32); amb = np.zeros(n, np.float32)
    def put(t, k, g=0.4, buf=None):
        buf = fx if buf is None else buf
        s = snd(k) * g; i = int(t * SR)
        if i < 0 or i >= n: return
        L = min(len(s), n - i); buf[i:i + L] += s[:L]
    def bed(t0, t1, k, g=0.15):
        s = snd(k); i0, i1 = int(t0 * SR), min(n, int(t1 * SR))
        L = i1 - i0
        if L <= 0: return
        xf = int(0.5 * SR); out = np.zeros(L, np.float32); pos = 0
        while pos < L:
            c = s[:min(len(s), L - pos)].copy()
            if pos > 0:
                q = min(xf, len(c)); c[:q] *= np.linspace(0, 1, q); out[pos:pos + q] *= 1  # crossfade-in
            out[pos:pos + len(c)] += c
            pos += max(1, len(s) - xf)
        e = int(0.6 * SR); e = min(e, L // 2)
        out[:e] *= np.linspace(0, 1, e); out[-e:] *= np.linspace(1, 0, e)
        amb[i0:i1] += out * g
    starts = [b[0] for b in S.BEATS] + [S.END]
    AMB = {'a_coup': 'court', 'a_throne_guard': 'court', 'a_coronation': 'court', 'a_exile': 'rain', 'a_hindukush': 'wind',
           'a_vs': 'march', 'a_indus': 'river', 'a_tent': 'candle', 'a_swords': 'battle', 'a_battle': 'battle',
           'a_elephants': 'battle', 'a_lodi_falls': 'battle', 'a_admin': 'court', 'a_akbar': 'court', 'a_puppet': 'court',
           'a_nadir': 'fire', 'a_shrink': 'wind', 'a_1857': 'march', 'a_whatif': 'wind', 'a_fergana_boy': 'wind',
           'a_kabul': 'wind', 'a_treasury': 'wind', 'a_wagons': 'wind', 'a_cannons': 'battle', 'a_gunners': 'wind'}
    AMBG = {'wind': 0.07, 'court': 0.12, 'battle': 0.14, 'fire': 0.16, 'rain': 0.14, 'march': 0.12, 'river': 0.12, 'candle': 0.15}
    for i, b in enumerate(S.BEATS):
        nm = b[1].__name__; s0, s1 = starts[i], starts[i + 1]; bd = s1 - s0
        at = lambda f: s0 + f * bd
        if nm in AMB:
            bed(s0, s1, AMB[nm], AMBG[AMB[nm]])
        if i > 0:
            put(s0 - 0.35, 'whoosh', 0.22)
        if nm == 'a_title': put(0.6, 'drums', 0.45)
        elif nm == 'a_book':
            for f in (0.03, 0.4, 0.75): put(at(f), 'page', 0.3)
        elif nm == 'a_coup':
            put(at(0.05), 'unsheathe', 0.35); put(at(0.25), 'clash', 0.35); put(at(0.38), 'clash', 0.3); put(at(0.48), 'thunder', 0.4)
        elif nm == 'a_throne_guard': put(at(0.1), 'unsheathe', 0.3)
        elif nm == 'a_coronation': put(at(0.05), 'drums', 0.35)
        elif nm == 'a_lineage': put(at(0.1), 'drums', 0.25); put(at(0.35), 'thunder', 0.25)
        elif nm == 'a_exile': put(at(0.05), 'gallop', 0.3); put(at(0.6), 'thunder', 0.3)
        elif nm == 'a_hindukush': bed(s0, s1, 'march', 0.08)
        elif nm == 'a_kabul': put(at(0.0), 'gallop', 0.3); put(at(0.25), 'drums', 0.3); put(at(0.5), 'warcry', 0.25)
        elif nm == 'a_treasury': put(at(0.03), 'chest', 0.4)
        elif nm in ('a_map_south', 'a_build', 'a_aurangzeb', 'a_tulughma'): put(at(0.02), 'paper', 0.3)
        elif nm == 'a_pawn': put(at(0.15), 'chess', 0.45); put(at(0.37), 'chess', 0.35)
        elif nm == 'a_not_merc': put(at(0.2), 'unsheathe', 0.4)
        elif nm == 'a_vs': put(at(0.1), 'heartbeat', 0.3); put(at(0.5), 'heartbeat', 0.3)
        elif nm == 'a_indus': bed(s0, s1, 'march', 0.08)
        elif nm == 'a_gunners': put(at(0.75), 'cannon', 0.45)
        elif nm == 'a_cannons':
            for ci in range(5):
                tt = s0 + ci * 0.45
                while tt < s1 - 0.3:
                    if tt - s0 > 1: put(tt, 'cannon', 0.22)
                    tt += 2.6
            put(at(0.3), 'musket', 0.3)
        elif nm == 'a_swords':
            for ci in range(3):
                tt = s0 + ci * 0.5
                while tt < s1 - 0.3:
                    put(tt, 'cannon', 0.2); tt += 2.4
        elif nm == 'a_wagons':
            put(at(0.05), 'wagons', 0.4); put(at(0.25), 'wagons', 0.3); put(at(0.66), 'musket', 0.4); put(at(0.82), 'musket', 0.35)
        elif nm == 'a_tulughma': put(at(0.45), 'gallop', 0.25)
        elif nm == 'a_battle':
            put(at(0.0), 'warcry', 0.35); put(at(0.1), 'musket', 0.35); put(at(0.35), 'arrows', 0.4); put(at(0.37), 'gallop', 0.4)
            tt = at(0.75)
            while tt < s1 - 0.5: put(tt, 'cannon', 0.3); tt += 1.8
        elif nm == 'a_elephants':
            put(at(0.03), 'elephant', 0.5); put(at(0.3), 'elephant', 0.4); put(at(0.6), 'elephant', 0.45); put(at(0.5), 'warcry', 0.2)
        elif nm == 'a_lodi_falls': put(at(0.45), 'thud', 0.5); put(at(0.6), 'heartbeat', 0.3)
        elif nm == 'a_victory': put(at(0.02), 'cheer', 0.4); put(at(0.05), 'drums', 0.35)
        elif nm == 'a_timeline':
            for f in (0.05, 0.27, 0.49): put(at(f), 'drums', 0.18)
        elif nm == 'a_admin':
            for f in (0.0, 0.25, 0.5, 0.75): put(at(f), 'swish', 0.2)
        elif nm == 'a_humayun': put(at(0.05), 'heartbeat', 0.3); put(at(0.3), 'unsheathe', 0.3); put(at(0.66), 'gallop', 0.35)
        elif nm == 'a_akbar': put(at(0.02), 'drums', 0.35)
        elif nm == 'a_crack': put(at(0.05), 'thunder', 0.35); put(at(0.52), 'warcry', 0.3)
        elif nm == 'a_puppet': put(at(0.1), 'heartbeat', 0.25)
        elif nm == 'a_nadir': put(at(0.02), 'gallop', 0.4); put(at(0.15), 'warcry', 0.3); put(at(0.62), 'chest', 0.25)
        elif nm == 'a_1857': put(at(0.3), 'musket', 0.35); put(at(0.65), 'heartbeat', 0.3)
        elif nm == 'a_outro': put(at(0.05), 'drums', 0.4)
    # light swish on every in-beat shot cut
    for i, edges in enumerate(SHOTS):
        for t in edges[1:-1]:
            put(t - 0.12, 'swish', 0.07)
    CUE = {}
    for k in ('a_title', 'a_coronation', 'a_kabul', 'a_victory', 'a_timeline', 'a_build', 'a_admin', 'a_akbar', 'a_outro'):
        CUE[k] = 'm_royal'
    for k in ('a_vs', 'a_gunners', 'a_cannons', 'a_swords', 'a_wagons', 'a_battle', 'a_elephants', 'a_coup', 'a_nadir',
              'a_crack', 'a_1857', 'a_not_merc', 'a_throne_guard'):
        CUE[k] = 'm_battle'
    for k in ('a_lodi_falls', 'a_humayun', 'a_aurangzeb', 'a_puppet', 'a_shrink'):
        CUE[k] = 'm_tragic'
    regions = []
    for i, b in enumerate(S.BEATS):
        c = CUE.get(b[1].__name__, 'm_journey')
        if regions and regions[-1][0] == c:
            regions[-1][2] = starts[i + 1]
        else:
            regions.append([c, starts[i], starts[i + 1]])
    mus = np.zeros(n, np.float32)
    for c, t0, t1 in regions:
        s = snd(c); i0, i1 = int(max(0, t0 - 0.8) * SR), min(n, int((t1 + 0.8) * SR))
        L = i1 - i0; out = np.zeros(L, np.float32); pos = 0; xf = int(1.0 * SR)
        while pos < L:
            seg_ = s[:min(len(s), L - pos)].copy()
            if pos > 0:
                q = min(xf, len(seg_)); seg_[:q] *= np.linspace(0, 1, q); out[pos:pos + q] *= np.linspace(1, 0, q)[:len(out[pos:pos + q])]
            out[pos:pos + len(seg_)] += seg_
            pos += len(s) - xf
        e = min(int(1.6 * SR), L // 2)
        out[:e] *= np.linspace(0, 1, e); out[-e:] *= np.linspace(1, 0, e)
        mus[i0:i1] += out
    venv = np.convolve(np.abs(voice), np.ones(SR // 5) / (SR // 5), mode='same')
    vd = np.clip(venv * 12, 0, 1)
    out = voice * 0.92 + fx * 0.55 * (1 - 0.35 * vd) + amb * (1 - 0.4 * vd) + mus * 0.20 * (1 - 0.6 * vd)
    return out

# ------------------------------------------------------------------ overlays
def chapter_card(cv, top, main, lt):
    dur = 3.2
    if lt < 0 or lt > dur:
        return
    a = min(ease_out(lt / 0.4), 1 - ease((lt - dur + 0.5) / 0.5))
    cv.drawRect(skia.Rect.MakeWH(W, H), P(C('#120608', 0.55 * a)))
    cx, cy = W / 2, H / 2
    arch = smooth_path([(cx - 420, cy + 200), (cx - 420, cy - 120), (cx - 330, cy - 220), (cx - 160, cy - 270), (cx, cy - 330),
                        (cx + 160, cy - 270), (cx + 330, cy - 220), (cx + 420, cy - 120), (cx + 420, cy + 200)], closed=True)
    cv.drawPath(arch, P(C('#4a1020', 0.92 * a)))
    cv.drawPath(arch, P(C('#f2c232', a), stroke=7))
    s = 1.08 - 0.08 * ease_out(lt / 0.6)
    draw_text(cv, top, cx, cy - 120, 52, 'deco', '#ffe9a8', alpha=a, scale=s)
    draw_text(cv, main, cx, cy + 20, 96, 'title', '#ffd54f', stroke=4, alpha=a, scale=s, maxw=760)

def date_badge(cv, text, lt, dur):
    if lt < 0 or lt > dur:
        return
    a = min(ease_out(lt / 0.4), 1 - ease((lt - dur + 0.4) / 0.4))
    x0 = 70 - 60 * (1 - a)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, 95, 640, 84), 14, 14)
    cv.drawRRect(r, P(C('#120a06', 0.78 * a)))
    cv.drawRect(skia.Rect.MakeXYWH(x0, 95, 10, 84), P(C('#f2c232', a)))
    draw_text(cv, text, x0 + 34, 137, 44, 'title', '#ffe9a8', anchor='l', alpha=a)

def name_card(cv, name, sub, lt):
    dur = 4.0
    if lt < 0 or lt > dur:
        return
    a = min(ease_out(lt / 0.45), 1 - ease((lt - dur + 0.5) / 0.5))
    x0 = 70 - 120 * (1 - a)
    y0 = H - 290
    cv.drawRect(skia.Rect.MakeXYWH(x0, y0, 760, 140), P(shader=lin(x0, 0, x0 + 760, 0, [C('#2a0d14', 0.9 * a), C('#2a0d14', 0)])))
    cv.drawRect(skia.Rect.MakeXYWH(x0, y0, 8, 140), P(C('#f2c232', a)))
    draw_text(cv, name, x0 + 36, y0 + 50, 58, 'title', '#ffd54f', stroke=3, anchor='l', alpha=a)
    draw_text(cv, sub, x0 + 38, y0 + 108, 34, 'body', '#fff3e0', anchor='l', alpha=a)

def pop(cv, text, lt, dur, y, x=0.5, size=96, col='#ffd54f'):
    if lt < 0 or lt > dur:
        return
    k = ease_out(lt / 0.35)
    a = min(k, 1 - ease((lt - dur + 0.4) / 0.4))
    glow(cv, W * x, H * y, 280, '#ff8f00', 0.3 * a)
    draw_text(cv, text, W * x, H * y, size, 'title', col, stroke=5, alpha=a, scale=0.7 + 0.3 * k, maxw=int(W * 0.85))


# ------------------------------------------------------------------ v2: realism + motion graphics
import json as _json
FLAT = {'a_map_south', 'a_tulughma', 'a_timeline', 'a_build', 'a_aurangzeb', 'a_crack', 'a_shrink', 'a_book',
        'a_pawn', 'a_outro', 'a_lineage', 'a_tent'}
SMOKY = {'a_battle', 'a_elephants', 'a_cannons', 'a_swords', 'a_wagons', 'a_lodi_falls', 'a_nadir', 'a_gunners', 'a_vs'}
CHAPTERS = [(0, 'अध्याय 1 • बाबर का उदय'), (S.TB(97.6), 'अध्याय 2 • पानीपत का युद्ध'),
            (S.TB(201.4), 'अध्याय 3 • तुलुग़मा रणनीति'), (S.TC(274.0), 'अध्याय 4 • साम्राज्य का निर्माण'),
            (S.TC(341.9), 'अध्याय 5 • दुखद पतन')]
KEYS = [('मुकद्दर', 'मुक़द्दर'), ('बेगर', 'बेघर राजकुमार'), ('तक्टोताज', 'तख़्त-ओ-ताज छिना'), ('फरगना', 'फ़रग़ना'),
        ('साजचे', 'साज़िशें'), ('तैमूर', 'तैमूर का वंशज'), ('चंगीस', 'चंगेज़ ख़ान का ख़ून'), ('खदेड', 'घर से बेदख़ल'),
        ('कुष', 'हिंदूकुश पार'), ('वापसी.', 'शानदार वापसी'), ('दक्षिन', 'नज़र दक्षिण की ओर'), ('मोहरे', 'मोहरा?'),
        ('किराया', 'किराए का सैनिक नहीं'), ('पानिपात', 'पानीपत'), ('आदूनेग', 'आधुनिक हथियार'),
        ('तोपची', 'उस्मानी तोपची'), ('आत्माहत्या', 'खुला मैदान = आत्महत्या'), ('अबहिदियत', 'अभेद्य दीवार'),
        ('संकरी', 'तंग जगह में फँसाओ'), ('गुर्सवार', 'घुड़सवार'), ('तीरन्दास', 'तीरंदाज़'),
        ('विग्यानिक', 'मनोवैज्ञानिक असर'), ('ताश', 'ताश के पत्तों की तरह'), ('तुक्का', 'तुक्का नहीं'),
        ('तींसो', '300 साल'), ('कुट', 'कूटनीति'), ('कगार', 'ख़त्म होने की कगार'), ('पलट्वार', 'पलटवार'),
        ('जवाल', 'हर उरूज का ज़वाल'), ('बगावते', 'बग़ावतें'), ('प्रतिकात्मक', 'सिर्फ़ नाम का बादशाह'),
        ('कतलियाम', 'क़त्ल-ए-आम'), ('जनाजा', 'शान-ओ-शौकत का जनाज़ा'), ('पुरानी', 'सिर्फ़ पुरानी दिल्ली'),
        ('ब्रितिश', 'ब्रिटिश राज'), ('सवाल', 'एक बड़ा सवाल')]

def build_captions():
    words = _json.load(open(os.path.join(PROJECT, 'words_final.json')))
    used, caps, last = set(), [], -99
    for t, w in words:
        for k, disp in KEYS:
            if k in used or k not in w:
                continue
            if t - last < 2.6:
                break
            used.add(k); caps.append((t - 0.1, disp)); last = t
            break
    return caps
CAPS = build_captions()

def kinetic_caption(cv, T):
    for t0, txt in CAPS:
        lt = T - t0
        if lt < 0 or lt > 2.4:
            continue
        k = ease_out(min(1, lt / 0.35))
        a = min(k, 1 - ease((lt - 1.95) / 0.45))
        y = H - 112 + 22 * (1 - k)
        timg = text_img(txt, 52, 'title', '#ffe9a8', stroke=4)
        w = timg.width()
        x0 = W / 2 - w / 2
        cv.drawRect(skia.Rect.MakeLTRB(x0 - 40, y - 46, x0 + w + 40, y + 40),
                    P(shader=lin(x0 - 40, 0, x0 + w + 40, 0, [C('#120608', 0), C('#120608', 0.75 * a), C('#120608', 0.75 * a), C('#120608', 0)], [0, 0.15, 0.85, 1])))
        uw = w * ease_out(min(1, max(0, (lt - 0.15) / 0.4)))
        cv.drawRect(skia.Rect.MakeXYWH(W / 2 - uw / 2, y + 30, uw, 5), P(C('#f2c232', a)))
        p = skia.Paint(); p.setAlphaf(a)
        cv.drawImage(timg, x0, y - timg.height() / 2 - 4, SAMP, p)

def chapter_tracker(cv, T):
    i = max(k for k, (t0, _) in enumerate(CHAPTERS) if T >= t0)
    draw_text(cv, CHAPTERS[i][1], 60, 33, 28, 'title', '#e8c766', anchor='l', alpha=0.9)
    x0, x1 = 1240, 1860
    cv.drawRect(skia.Rect.MakeLTRB(x0, 30, x1, 35), P(C('#ffffff', 0.18)))
    cv.drawRect(skia.Rect.MakeLTRB(x0, 30, x0 + (x1 - x0) * T / S.END, 35), P('#f2c232'))
    for t0, _ in CHAPTERS[1:]:
        cx = x0 + (x1 - x0) * t0 / S.END
        cv.drawCircle(cx, 32.5, 6, P('#f2c232' if T >= t0 else '#5d4a3a'))

def wipe(cv, T, cut):
    d = (T - cut) / 0.55          # -1..1 around the cut
    if abs(d) >= 1:
        return
    cx = W / 2 + d * W * 1.35
    bw = W * 0.75
    sk = 260
    pts = [(cx - bw - sk, 0), (cx + bw - sk, 0), (cx + bw + sk, H), (cx - bw + sk, H)]
    cv.drawPath(poly(pts), P(shader=lin(cx - bw, 0, cx + bw, 0, ['#1c0a10', '#3a1420', '#1c0a10'])))
    for off in (-bw, bw):
        cv.drawPath(poly([(cx + off - sk - 8, 0), (cx + off - sk + 8, 0), (cx + off + sk + 8, H), (cx + off + sk - 8, H)]), P('#f2c232'))
    glow(cv, cx, H / 2, 300, '#ffcc66', 0.25)

_blur = {}
def blur_paint(s):
    s = round(s, 1)
    if s not in _blur:
        p = skia.Paint(); p.setImageFilter(skia.ImageFilters.Blur(s, s)); _blur[s] = p
    return _blur[s]

def realism_mid(cv, T, grade, name):
    if name in FLAT:
        return
    # atmospheric haze at horizon
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 330, 0, 920, [C(grade, 0), C(mix(grade, '#ffffff', 0.4), 0.14), C(grade, 0)], [0, 0.55, 1])))
    for i in range(3):
        fx = (T * (18 + 9 * i) + i * 700) % (W + 1200) - 600
        cv.drawOval(skia.Rect.MakeXYWH(fx, 560 + 40 * i, 900, 120), P(C('#ffffff', 0.05), ))

def realism_top(cv, T, grade, name):
    if name in FLAT:
        return
    # key light from upper side + soft god rays
    cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=rad(1500, 80, 1300, [C(mix(grade, '#ffffff', 0.5), 0.20), C(grade, 0)]), blend=skia.BlendMode.kScreen))
    rays(cv, 1500, -60, T, col=mix(grade, '#ffffff', 0.6), a=0.06, n=6, spread=60, length=1700)
    # ground darkening (contact depth)
    cv.drawRect(skia.Rect.MakeLTRB(0, 880, W, H), P(shader=lin(0, 880, 0, H, [C('#000000', 0), C('#000000', 0.35)])))
    if name in SMOKY:
        mf = skia.MaskFilter.MakeBlur(skia.BlurStyle.kNormal_BlurStyle, 60)
        for i in range(6):
            x = (T * (35 + 12 * i) + i * 420) % (W + 900) - 450
            y = 760 + 90 * math.sin(T * 0.3 + i)
            p = P(C('#d7ccc8', 0.11)); p.setMaskFilter(mf)
            cv.drawCircle(x, y, 220 + 40 * (i % 3), p)


# ------------------------------------------------------------------ v3: fast shot cutting synced to narration
def _dyn(fx, fy):
    return lambda bp: (fx(bp), fy)
FOCUS = {
 'a_title': [(960, 700), (960, 480)], 'a_book': [(960, 530), (760, 500)],
 'a_coup': [(960, 600), (700, 600), (1220, 600)], 'a_throne_guard': [(960, 590), (520, 640), (1400, 640)],
 'a_fergana_boy': [(900, 520), (900, 700), (600, 600)], 'a_coronation': [(960, 560), (500, 640), (1410, 640)],
 'a_lineage': [(960, 600), (440, 470), (1480, 470)], 'a_exile': [_dyn(lambda b: 1300 - 600 * b, 620), (1700, 750)],
 'a_hindukush': [_dyn(lambda b: 820 + 900 * b, 680), _dyn(lambda b: 250 + 900 * b, 880)],
 'a_kabul': [(700, 650), (1430, 450), (310, 860)], 'a_treasury': [(680, 570), (1250, 860)],
 'a_map_south': [(1000, 560), (1075, 650), (700, 470)], 'a_pawn': [(1100, 850), (360, 620), (1000, 800)],
 'a_not_merc': [(960, 500), (1120, 380)], 'a_vs': [(580, 600), (1450, 650)],
 'a_indus': [_dyn(lambda b: 700 + 1200 * b, 700), _dyn(lambda b: 150 + 1200 * b, 900)],
 'a_tent': [(960, 640), (1380, 680), (900, 760)], 'a_gunners': [(600, 590), (860, 600), (1350, 900)],
 'a_cannons': [(600, 930), (1250, 930), (960, 800)], 'a_swords': [(480, 700), (1450, 700)],
 'a_wagons': [(960, 760), (400, 960), (1500, 960), (960, 940)], 'a_tulughma': [(960, 500), (960, 700)],
 'a_battle': [(600, 900), (1400, 900), (960, 700)], 'a_elephants': [(600, 750), (1100, 750), (1550, 750)],
 'a_lodi_falls': [(960, 800), (1300, 700), (450, 950)], 'a_victory': [(900, 520), (1380, 600)],
 'a_timeline': [(400, 560), (960, 560), (1520, 560), (960, 800)], 'a_build': [(1075, 560), (1000, 600)],
 'a_admin': [(300, 720), (600, 720), (1320, 720), (1620, 720), (960, 600)],
 'a_humayun': [(700, 620), (1300, 600), (1400, 800)], 'a_akbar': [(960, 560), (460, 700), (1460, 700)],
 'a_aurangzeb': [(1075, 650), (1600, 640)], 'a_crack': [(1000, 560), (400, 640)],
 'a_puppet': [(960, 700), (960, 560)], 'a_nadir': [(900, 650), (1300, 800), (700, 560)],
 'a_shrink': [(1075, 650), (960, 560)], 'a_1857': [(700, 600), (1450, 800), (1700, 700)],
 'a_whatif': [(700, 520), (1350, 520)], 'a_outro': [(960, 540)],
}
TEXTY = {'a_vs', 'a_swords', 'a_tulughma', 'a_timeline', 'a_admin', 'a_outro', 'a_book', 'a_map_south',
         'a_build', 'a_aurangzeb', 'a_crack', 'a_shrink'}

def _cut_candidates():
    c = list(_json.load(open(os.path.join(PROJECT, 'seg_starts.json'))))
    words = _json.load(open(os.path.join(PROJECT, 'words_final.json')))
    for k in range(1, len(words)):
        if words[k - 1][1][-1:] in ',.?।' :
            c.append(words[k][0])
    c += [t for t, _ in CAPS]
    return sorted(set(round(x, 2) for x in c))
CUTC = _cut_candidates()

def plan_shots():
    starts = [b[0] for b in S.BEATS] + [S.END]
    plans = []
    for i in range(len(S.BEATS)):
        s0, s1 = starts[i], starts[i + 1]
        cuts, last = [], s0
        for t in CUTC:
            if t - last >= 3.0 and s1 - t >= 2.5:
                cuts.append(t); last = t
        # fill long gaps
        pts = [s0] + cuts + [s1]
        out = [s0]
        for a, b in zip(pts, pts[1:]):
            n = int((b - a) // 5.5)
            for k in range(1, n + 1):
                out.append(a + (b - a) * k / (n + 1))
            out.append(b)
        plans.append(out)
    return plans
SHOTS = plan_shots()
CYCLE = ['wide', 'mid', 'close', 'alt']
GROUNDY = {'a_vs', 'a_indus', 'a_hindukush', 'a_cannons', 'a_swords', 'a_wagons', 'a_battle', 'a_elephants',
           'a_lodi_falls', 'a_1857', 'a_nadir', 'a_exile', 'a_kabul'}

def shot_cam(i, T, base):
    nm = S.BEATS[i][1].__name__
    edges = SHOTS[i]
    j = max(k for k in range(len(edges) - 1) if T >= edges[k]) if T >= edges[0] else 0
    j = min(j, len(edges) - 2)
    a, b = edges[j], edges[j + 1]
    u = (T - a) / max(1e-3, b - a)
    if len(edges) == 2:
        return base, None
    kind = CYCLE[(i + j) % 4]
    if nm in TEXTY and kind == 'close':
        kind = 'mid'
    if nm == 'a_outro':
        kind = 'wide'
    pts = FOCUS.get(nm, [(960, 600)])
    f = pts[0] if kind == 'close' else pts[(j + i) % len(pts)]
    bp = (T - S.BEATS[i][0]) / max(1e-3, edges[-1] - edges[0])
    fx, fy = f(bp) if callable(f) else f
    if kind == 'wide':
        cx, cy, z = base[0], base[1], base[2] * (1.0 + 0.05 * u)
    elif kind == 'mid':
        z = (1.18 if nm in TEXTY else 1.38) + 0.06 * u
        cx, cy = fx + 40 * (u - 0.5), fy - 70
    elif kind == 'close':
        z = 1.78 + 0.08 * u
        cx, cy = fx, fy - 90
    else:  # lateral tracking shot
        z = 1.25
        cx, cy = fx - 120 + 240 * u, fy - 90
    if nm in GROUNDY:
        cy, z = max(cy, 830), max(z, 1.15)
    # punch-in on cut
    z *= 1 + 0.035 * (1 - ease_out(min(1, (T - a) / 0.3)))
    z = max(z, 1.0)
    if nm in FLAT:
        cx = min(max(cx, 960 / z), 1920 - 960 / z)
        cy = min(max(cy, 540 / z), 1080 - 540 / z)
    elif kind != 'wide':
        cx = min(max(cx, 380), 1540)
        cy = min(max(cy, 320), 960)
    return (cx, cy, z), a

def cut_flash(cv, T, a):
    if a is None:
        return
    d = T - a
    if 0 <= d < 0.14 and a > 0.5:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(C('#fff4dc', 0.28 * (1 - d / 0.14))))

# ------------------------------------------------------------------ frame
class RT:
    cache = {}

def beat_at(T):
    i = 0
    while i + 1 < len(S.BEATS) and T >= S.BEATS[i + 1][0]:
        i += 1
    s0 = S.BEATS[i][0]
    s1 = S.BEATS[i + 1][0] if i + 1 < len(S.BEATS) else S.END
    return i, s0, s1

def get_layers(i):
    if i not in RT.cache:
        b = S.BEATS[i]
        RT.cache[i] = (b[2]() if b[2] else [], Particles(b[5], 70, 5 + i) if b[5] else None)
    return RT.cache[i]

def render_frame(cv, fi, ov):
    T = fi / FPS
    i, s0, s1 = beat_at(T)
    start, act, bgf, camse, grade, fxk, cards = S.BEATS[i]
    bd = s1 - s0
    bt = T - s0
    bp = max(0, min(1, bt / bd))
    (x0, y0, z0), (x1, y1, z1) = camse
    e = ease(bp)
    (cx, cy, z), shot_a = shot_cam(i, T, (lerp(x0, x1, e), lerp(y0, y1, e), lerp(z0, z1, e)))
    if act.__name__ in ('a_battle', 'a_elephants', 'a_cannons') and int(T * 8) % 5 == 0:
        cx += 6 * math.sin(T * 50); cy += 6 * math.cos(T * 43)
    # handheld camera drift
    cx += 3.5 * math.sin(T * 0.71) + 1.8 * math.sin(T * 1.93)
    cy += 2.5 * math.sin(T * 0.87 + 1.1)
    rot = 0.22 * math.sin(T * 0.43)
    layers, fx = get_layers(i)
    ctx = dict(t=T, bt=bt, bp=bp, bd=bd)
    nm = act.__name__
    for p, fn in layers + [(1.0, act)]:
        if fn is act:
            realism_mid(cv, T, grade, nm)
        blurred = p < 0.75 and nm not in FLAT
        if blurred:
            cv.saveLayer(None, blur_paint(1.0 + 5.0 * (0.75 - p) / 0.75))
        cv.save()
        cv.translate(W / 2, H / 2)
        cv.rotate(rot * p)
        sc = 1 + (z - 1) * p
        cv.scale(sc, sc)
        cv.translate(-(960 + (cx - 960) * p), -(540 + (cy - 540) * p))
        fn(cv, ctx)
        if fn is act and fx:
            fx.draw(cv, T, 0.8)
        cv.restore()
        if blurred:
            cv.restore()
    realism_top(cv, T, grade, nm)
    ov.finish(cv, fi, grade)
    cut_flash(cv, T, shot_a)
    # parchment warmth + letterbox (cinematic look)
    cv.drawRect(skia.Rect.MakeWH(W, H), P(C('#704214', 0.10), blend=skia.BlendMode.kMultiply))
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, 64), P('#000000'))
    cv.drawRect(skia.Rect.MakeLTRB(0, H - 64, W, H), P('#000000'))
    for cd in cards:
        kind = cd[0]
        if kind == 'chapter':
            chapter_card(cv, cd[1], cd[2], bt)
        elif kind == 'date':
            date_badge(cv, cd[1], bt - cd[2], cd[3])
        elif kind == 'name':
            name_card(cv, cd[1], cd[2], bt - cd[3])
        elif kind == 'pop':
            x = cd[5] if len(cd) > 5 else 0.5
            pop(cv, cd[1], bt - cd[2], cd[3], cd[4], x=x)
        elif kind == 'sub':
            pop(cv, cd[1], bt - cd[2], cd[3], cd[4], size=56, col='#ffffff')
    kinetic_caption(cv, T)
    chapter_tracker(cv, T)
    # motion-graphic wipe across each cut
    for cut in (s0, s1):
        if 1.0 < cut < S.END - 1:
            wipe(cv, T, cut)
    if T < 0.8:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(C('#000000', 1 - T / 0.8)))
    if T > S.END - 1.2:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(C('#000000', min(1, (T - S.END + 1.2) / 1.2))))

G = {}

def encode_part(part):
    a, b = part
    seg = f'{OUT}/part{a:06d}.mp4'
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS),
           '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-maxrate', '8M', '-bufsize', '16M',
           '-pix_fmt', 'yuv420p', seg]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    ov = GR.Overlay(W, H)
    for fi in range(a, b):
        cv.clear(skia.ColorBLACK)
        render_frame(cv, fi, ov)
        pr.stdin.write(surf.makeImageSnapshot().toarray().tobytes())
        if (fi - a) % 300 == 0:
            open(f'{OUT}/progress_{a}.txt', 'w').write(f'{fi - a}/{b - a}')
    pr.stdin.close(); pr.wait()
    return seg

if __name__ == '__main__':
    mode = sys.argv[1]
    nfr = int(S.END * FPS)
    if mode == 'frames':
        from PIL import Image
        secs = [float(x) for x in sys.argv[2].split(',')]
        surf = skia.Surface(W, H); cv = surf.getCanvas(); ov = GR.Overlay(W, H)
        ims = []
        for s_ in secs:
            cv.clear(skia.ColorBLACK); render_frame(cv, int(s_ * FPS), ov)
            ims.append(Image.fromarray(surf.makeImageSnapshot().toarray()[..., [2, 1, 0]]).resize((480, 270)))
        cols = 4; rows = math.ceil(len(ims) / cols)
        sh = Image.new('RGB', (cols * 480, rows * 270))
        for k, im in enumerate(ims):
            sh.paste(im, ((k % cols) * 480, (k // cols) * 270))
        sh.save(f'{OUT}/sheet.jpg', quality=82); print('sheet', S.END); sys.exit()
    wav = f'{OUT}/mix.wav'
    GR.write_wav(wav, build_audio())
    import multiprocessing as mp
    nw = 2
    bounds = [(nfr * k // nw, nfr * (k + 1) // nw) for k in range(nw)]
    with mp.get_context('fork').Pool(nw) as pool:
        segs = pool.map(encode_part, bounds)
    lst = f'{OUT}/list.txt'
    open(lst, 'w').write(''.join(f"file '{s}'\n" for s in segs))
    final = f'{OUT}/final_raw.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-i', wav, '-c:v', 'copy',
                    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                    '-movflags', '+faststart', final], check=True)
    for s_ in segs:
        os.remove(s_)
    print('DONE', final)
