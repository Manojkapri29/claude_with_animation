import sys, os, math, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import OUT, QAUDIO, SFX
import numpy as np, skia
from mengine import *
import audiofx as GR
from quiz_data import QUIZZES
FPS, SR = 24, 24000
W, H = 1080, 1920
OPT = ['A', 'B', 'C', 'D']

def aud(j):
    return GR.load_wav(os.path.join(QAUDIO, f'{j}.wav'))

def build(qz):
    segs, tt = [], 0.4
    a = aud(f"{qz['id']}_intro"); segs.append(dict(kind='intro', start=tt, a=a)); tt += len(a) / SR + 0.6
    for i, q in enumerate(qz['qs']):
        qa, aa = aud(f"{qz['id']}_q{i}"), aud(f"{qz['id']}_a{i}")
        sg = dict(kind='q', i=i, start=tt, qa=qa, aa=aa)
        sg['timer'] = tt + len(qa) / SR + 0.5
        sg['reveal'] = sg['timer'] + 5.0
        sg['end'] = sg['reveal'] + 0.3 + len(aa) / SR + 0.9
        segs.append(sg); tt = sg['end']
    o = aud(f"{qz['id']}_outro"); segs.append(dict(kind='outro', start=tt + 0.2, a=o))
    return segs, tt + 0.2 + len(o) / SR + 1.2

def EL(k):
    p = os.path.join(SFX, f'{k}.wav')
    if not os.path.exists(p):
        return GR.sfx({'tick': 'tick', 'correct': 'ding'}.get(k, 'whoosh'))
    a = GR.load_wav(p); return a / (np.abs(a).max() + 1e-6) * 0.9

def mixaudio(segs, total):
    n = int(total * SR) + SR
    v = np.zeros(n, np.float32); fx = np.zeros(n, np.float32)
    def put(b, t, a, g=1.0):
        p = int(t * SR); L = min(len(a), n - p); b[p:p + L] += a[:L] * g
    for sg in segs:
        if sg['kind'] != 'q':
            put(v, sg['start'], sg['a']); put(fx, sg['start'] - 0.2, EL('drums'), 0.35)
        else:
            put(fx, sg['start'] - 0.3, EL('whoosh'), 0.35); put(v, sg['start'], sg['qa'])
            for k in range(5):
                put(fx, sg['timer'] + k, EL('tick'), 0.7)
            put(fx, sg['reveal'], EL('correct'), 0.6); put(v, sg['reveal'] + 0.3, sg['aa'])
    m = GR.music(total + 1, 'tense')[:n]
    v /= np.max(np.abs(v)) + 1e-6
    env = np.convolve(np.abs(v), np.ones(SR // 5) / (SR // 5), mode='same')
    return v * 0.9 + fx * 0.6 + m * 0.10 * (1 - 0.55 * np.clip(env * 12, 0, 1))

LAYERS = bg_court()

def frame(cv, qz, segs, total, fi, ov):
    T = fi / FPS
    cv.save(); s = H / 1080 * 1.0
    cv.translate(W / 2, H / 2); cv.scale(s, s); cv.translate(-960 - 60 * math.sin(T * 0.12), -560)
    for p, fn in LAYERS:
        fn(cv, dict(t=T, bt=T, bp=0, bd=1))
    cv.restore()
    Particles('sparkle', 40, 3, (0, 0, W, H)).draw(cv, T)
    cv.drawRect(skia.Rect.MakeWH(W, H), P(C('#140608', 0.58)))
    ov.finish(cv, fi, '#ffd54f')
    cur = segs[0]
    for sg in segs:
        if T >= sg['start'] - 0.3:
            cur = sg
    hero = qz['hero']
    if cur['kind'] == 'intro':
        k = ease_out((T - cur['start']) / 0.5)
        draw_text(cv, 'कथा और रहस्य', W / 2, 230, 46, 'deco', '#e8c766', alpha=k)
        draw_text(cv, qz['title'], W / 2, 380, 118, 'title', '#ffd54f', stroke=6, alpha=k, scale=0.8 + 0.2 * k, maxw=1000)
        draw_text(cv, 'क्विज़', W / 2, 520, 96, 'title', '#ffffff', stroke=5, alpha=k)
        draw_text(cv, qz['sub'], W / 2, 640, 50, 'body', '#ffe9a8', alpha=k)
        draw_throne(cv, W / 2, 1720, 1.1, peacock=True, t=T)
        draw_person(cv, hero, W / 2, 1720, T, scale=1.3, gesture=0.5 + 0.3 * math.sin(T * 2), mouth=0.5 * abs(math.sin(T * 9)))
    elif cur['kind'] == 'q':
        q = qz['qs'][cur['i']]
        k = ease_out((T - cur['start'] + 0.3) / 0.5)
        draw_text(cv, f"सवाल {cur['i'] + 1} / 5", W / 2, 170, 54, 'deco', '#ffe9a8', alpha=k)
        # progress dots
        for j in range(5):
            cv.drawCircle(W / 2 - 120 + 60 * j, 240, 12, P('#f2c232' if j <= cur['i'] else '#5d4a3a'))
        bw, by, bh = 960, 300, 300
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(W / 2 - bw / 2, by, bw, bh), 34, 34)
        cv.drawRRect(rr, P(C('#1a0f08', 0.85 * k))); cv.drawRRect(rr, P(C('#f2c232', k), stroke=5))
        draw_text(cv, q['q'], W / 2, by + bh / 2, 66, 'title', '#ffffff', alpha=k, maxw=880)
        rev = T >= cur['reveal']
        for j, o in enumerate(q['opts']):
            ox, oy, ow, oh = W / 2, 760 + j * 170, 900, 136
            kj = ease_out((T - cur['start'] - 0.2 - j * 0.12) / 0.4)
            ok = rev and j == q['a']
            col = '#2e7d32' if ok else ('#3a2a30' if rev else '#2b1420')
            r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(ox - ow / 2, oy - oh / 2, ow, oh), oh / 2, oh / 2)
            cv.drawRRect(r, P(C(col, 0.93 * kj))); cv.drawRRect(r, P(C('#b9f6ca' if ok else '#f2c232', kj), stroke=4))
            cv.drawCircle(ox - ow / 2 + oh / 2, oy, oh * 0.36, P(C('#f2c232', kj)))
            draw_text(cv, OPT[j], ox - ow / 2 + oh / 2, oy, int(oh * 0.42), 'body', '#1a0f08', alpha=kj)
            draw_text(cv, o, ox + oh * 0.3, oy, 60, 'title', '#ffffff', alpha=kj * (0.45 if rev and not ok else 1))
            if ok:
                glow(cv, ox, oy, ow * 0.6, '#69f0ae', 0.35 * ease_out((T - cur['reveal']) / 0.4))
        tx, ty, R = W / 2, 1560, 120
        if cur['timer'] <= T < cur['reveal']:
            rem = cur['reveal'] - T
            cv.drawCircle(tx, ty, R, P(C('#000000', 0.65)))
            arc = skia.Path(); arc.addArc(skia.Rect.MakeXYWH(tx - R, ty - R, 2 * R, 2 * R), -90, 360 * rem / 5)
            cv.drawPath(arc, P(mix('#e53935', '#ffd54f', rem / 5), stroke=18))
            draw_text(cv, str(int(math.ceil(rem))), tx, ty, 110, 'body', '#ffffff', scale=1 + 0.15 * (1 - rem % 1))
        elif rev:
            k2 = ease_out((T - cur['reveal']) / 0.4)
            draw_text(cv, 'सही जवाब!', tx, ty, 92, 'title', '#69f0ae', stroke=5, alpha=k2, scale=0.8 + 0.2 * k2)
        else:
            draw_person(cv, hero, W - 170, 1830, T, scale=0.75, facing=-1, gesture=0.6, mouth=0.5 * abs(math.sin(T * 9)))
    else:
        k = ease_out((T - cur['start']) / 0.5)
        draw_text(cv, 'आपका स्कोर', W / 2, 420, 110, 'title', '#ffd54f', stroke=6, alpha=k)
        draw_text(cv, 'कितना रहा?', W / 2, 560, 110, 'title', '#ffd54f', stroke=6, alpha=k)
        draw_text(cv, 'कमेंट में लिखिए', W / 2, 720, 68, 'title', '#ffffff', alpha=k)
        r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(190, 860, 700, 120), 60, 60)
        cv.drawRRect(r, P(C('#b71c1c', k))); cv.drawRRect(r, P(C('#f2c232', k), stroke=4))
        draw_text(cv, 'सब्सक्राइब करें', W / 2, 920, 60, 'title', '#ffffff', alpha=k)
        draw_person(cv, hero, W / 2, 1780, T, scale=1.3, gesture=0.9, mouth=0.5 * abs(math.sin(T * 9)))
    if T < 0.4:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(C('#000000', 1 - T / 0.4)))
    if T > total - 0.6:
        cv.drawRect(skia.Rect.MakeWH(W, H), P(C('#000000', min(1, (T - total + 0.6) / 0.6))))

def render(qz, test=None):
    segs, total = build(qz)
    ov = GR.Overlay(W, H)
    surf = skia.Surface(W, H); cv = surf.getCanvas()
    if test:
        from PIL import Image
        ims = []
        for s_ in test:
            cv.clear(skia.ColorBLACK); frame(cv, qz, segs, total, int(s_ * FPS), ov)
            ims.append(Image.fromarray(surf.makeImageSnapshot().toarray()[..., [2, 1, 0]]).resize((270, 480)))
        sh = Image.new('RGB', (270 * len(ims), 480))
        for i, im in enumerate(ims):
            sh.paste(im, (270 * i, 0))
        sh.save(f'{OUT}/qsheet.jpg'); print(total, [round(s['start'], 1) for s in segs]); return
    wav = f"{OUT}/{qz['id']}.wav"; GR.write_wav(wav, mixaudio(segs, total))
    name = {'q1': 'quiz1-babur-panipat', 'q2': 'quiz2-mughal-samrajya'}[qz['id']]
    pr = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS),
                           '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '21', '-pix_fmt', 'yuv420p',
                           '-af', 'loudnorm=I=-14:TP=-1.5', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                           '-movflags', '+faststart', f'{OUT}/{name}.mp4'], stdin=subprocess.PIPE)
    for fi in range(int(total * FPS)):
        cv.clear(skia.ColorBLACK); frame(cv, qz, segs, total, fi, ov)
        pr.stdin.write(surf.makeImageSnapshot().toarray().tobytes())
    pr.stdin.close(); pr.wait(); print('DONE', name, round(total, 1))

if __name__ == '__main__':
    qz = QUIZZES[int(sys.argv[1])]
    render(qz, [float(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else None)
