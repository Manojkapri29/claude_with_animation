"""Audio helpers (load/write wav, synth SFX + music fallback) and the film overlay (grain, vignette, grade)."""
import math, random, wave
import numpy as np
import skia
from engine import *
FPS = 24
SR = 24000

def load_wav(path):
    with wave.open(path) as w:
        sr = w.getframerate()
        n = w.getnframes()
        ch = w.getnchannels()
        sw = w.getsampwidth()
        raw = w.readframes(n)
    if sw == 2:
        a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    else:
        a = np.frombuffer(raw, np.int32).astype(np.float32) / 2 ** 31
    if ch > 1:
        a = a.reshape(-1, ch).mean(1)
    if sr != SR:
        x = np.arange(len(a)) / sr
        a = np.interp(np.arange(int(len(a) * SR / sr)) / SR, x, a).astype(np.float32)
    # trim leading/trailing silence
    thr = 0.01
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx):
        a = a[max(0, idx[0] - int(0.03 * SR)): idx[-1] + int(0.08 * SR)]
    return a


def envelope(a):
    hop = SR // FPS
    n = int(math.ceil(len(a) / hop))
    e = np.array([np.sqrt(np.mean(a[i * hop:(i + 1) * hop] ** 2) + 1e-9) for i in range(n)])
    ref = np.percentile(e, 90) + 1e-6
    e = np.clip(e / ref, 0, 1)
    e = np.convolve(e, [0.25, 0.5, 0.25], mode='same')
    return e

def write_wav(path, a):
    a = np.clip(a, -1, 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())

# ---- synth sfx / music
def _t(d):
    return np.arange(int(d * SR)) / SR

def sfx(kind):
    rnd = np.random.default_rng(abs(hash(kind)) % 1000)
    if kind == 'whoosh':
        t = _t(0.9)
        n = rnd.standard_normal(len(t))
        env = np.sin(np.pi * t / t[-1]) ** 2
        k = np.cumsum(n) * 0.02
        k -= np.convolve(k, np.ones(200) / 200, mode='same')
        return (k * env * 0.6).astype(np.float32)
    if kind == 'boom':
        t = _t(2.2)
        s = np.sin(2 * np.pi * (55 - 20 * t) * t) * np.exp(-t * 2.2)
        n = rnd.standard_normal(len(t)) * np.exp(-t * 5) * 0.4
        n = np.convolve(n, np.ones(30) / 30, mode='same')
        return ((s + n) * 0.9).astype(np.float32)
    if kind == 'thunder':
        t = _t(3.0)
        n = rnd.standard_normal(len(t))
        n = np.convolve(n, np.ones(60) / 60, mode='same') * 6
        env = np.exp(-t * 1.3) * (1 + 0.5 * np.sin(t * 17))
        return (n * env * 0.8 + np.sin(2 * np.pi * 40 * t) * np.exp(-t * 2) * 0.5).astype(np.float32)
    if kind == 'crack':
        out = np.zeros(int(0.8 * SR), np.float32)
        for i in range(6):
            p = int(rnd.uniform(0, 0.7) * SR)
            L = int(0.02 * SR)
            out[p:p + L] += rnd.standard_normal(L).astype(np.float32) * np.exp(-np.arange(L) / 120) * 0.7
        return out
    if kind == 'shimmer':
        t = _t(2.0)
        s = np.zeros_like(t)
        for i, f in enumerate([1318, 1568, 1976, 2349, 2637]):
            st = i * 0.12
            m = t > st
            s[m] += np.sin(2 * np.pi * f * (t[m] - st)) * np.exp(-(t[m] - st) * 2.5) * 0.18
        return s.astype(np.float32)
    if kind == 'flap':
        out = np.zeros(int(1.2 * SR), np.float32)
        for i in range(3):
            p = int(i * 0.35 * SR)
            L = int(0.18 * SR)
            n = rnd.standard_normal(L)
            n = np.convolve(n, np.ones(40) / 40, mode='same') * 4
            out[p:p + L] += (n * np.sin(np.linspace(0, np.pi, L)) * 0.5).astype(np.float32)
        return out
    if kind == 'fire':
        t = _t(4.0)
        n = rnd.standard_normal(len(t))
        n = np.convolve(n, np.ones(25) / 25, mode='same') * 3 * 0.25
        clicks = (rnd.random(len(t)) > 0.9993) * rnd.standard_normal(len(t)) * 0.8
        env = np.minimum(1, t * 2) * np.minimum(1, (t[-1] - t) * 2)
        return ((n + clicks) * env).astype(np.float32)
    if kind == 'splash':
        t = _t(1.5)
        n = rnd.standard_normal(len(t))
        n = n - np.convolve(n, np.ones(8) / 8, mode='same')
        return (n * np.exp(-t * 2.5) * 0.5).astype(np.float32)
    if kind == 'hiss':
        t = _t(1.6)
        n = rnd.standard_normal(len(t))
        n = n - np.convolve(n, np.ones(4) / 4, mode='same')
        return (n * np.sin(np.pi * t / t[-1]) * 0.35).astype(np.float32)
    if kind == 'spin':
        t = _t(3.0)
        s = np.sin(2 * np.pi * 300 * t + 3 * np.sin(2 * np.pi * 12 * t)) * 0.15
        n = rnd.standard_normal(len(t)) * 0.08 * (0.5 + 0.5 * np.sin(2 * np.pi * 12 * t))
        return ((s + n) * np.minimum(1, t * 3) * np.minimum(1, (3 - t) * 3)).astype(np.float32)
    if kind == 'tick':
        t = _t(0.06)
        return (np.sin(2 * np.pi * 2000 * t) * np.exp(-t * 90) * 0.5).astype(np.float32)
    if kind == 'ding':
        t = _t(1.4)
        s = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(880, 0.4), (1760, 0.15), (2640, 0.08)])
        return (s * np.exp(-t * 3)).astype(np.float32)
    if kind == 'hooves':
        out = np.zeros(int(2.0 * SR), np.float32)
        for i in range(10):
            p = int(i * 0.19 * SR)
            L = int(0.04 * SR)
            out[p:p + L] += (np.sin(2 * np.pi * 120 * np.arange(L) / SR) * np.exp(-np.arange(L) / 200) * 0.5)
        return out
    return np.zeros(10, np.float32)

def music(dur, mood='calm'):
    """Tanpura-like drone + soft pad, optional low drum pulse."""
    t = _t(dur)
    base = 130.81  # C3 (Sa)
    s = np.zeros_like(t)
    for f, a in [(base, 0.35), (base * 1.5, 0.25), (base * 2, 0.2), (base / 2, 0.25), (base * 3, 0.06)]:
        s += a * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.11 * t)) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.07 * t + f))
    # tanpura pluck cycle
    cyc = 2.4
    ph = (t % cyc) / cyc
    pl = np.exp(-ph * 4) * np.sin(2 * np.pi * base * 2 * t) * 0.25
    s += pl
    if mood == 'tense':
        beat = (t % 0.75) / 0.75
        s += np.sin(2 * np.pi * 60 * t) * np.exp(-beat * 9) * 0.9
    s /= np.max(np.abs(s)) + 1e-6
    fade = np.minimum(1, t / 2.0) * np.minimum(1, (dur - t) / 2.5)
    return (s * fade).astype(np.float32)

# ------------------------------------------------------------------ timeline (long)

class Overlay:
    def __init__(self, W, H):
        self.W, self.H = W, H
        rng = np.random.default_rng(1)
        self.grain = []
        for i in range(6):
            g = rng.integers(0, 255, (H // 2, W // 2), dtype=np.uint8)
            rgba = np.stack([g, g, g, np.full_like(g, 10)], -1)
            self.grain.append(skia.Image.fromarray(np.ascontiguousarray(rgba),
                                                   colorType=skia.ColorType.kRGBA_8888_ColorType))
        self.vig = P(shader=rad(W / 2, H / 2, max(W, H) * 0.75, [C('#000000', 0), C('#000000', 0.0),
                                                                     C('#000000', 0.55)], [0, 0.55, 1]))

    def finish(self, cv, fi, grade):
        W, H = self.W, self.H
        cv.drawRect(skia.Rect.MakeWH(W, H), P(shader=lin(0, 0, W, H, [C(grade, 0.22), C('#1a237e', 0.18)]),
                                               blend=skia.BlendMode.kSoftLight))
        cv.drawRect(skia.Rect.MakeWH(W, H), self.vig)
        g = self.grain[(fi // 4) % 6]
        p = skia.Paint()
        p.setBlendMode(skia.BlendMode.kOverlay)
        cv.drawImageRect(g, skia.Rect.MakeWH(W, H), SAMP, p)

