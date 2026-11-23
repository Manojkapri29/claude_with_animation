"""2D drawing engine: skia primitives, characters, props, backgrounds, fx, text."""
import math, random, functools
import numpy as np
import skia
from PIL import Image, ImageDraw, ImageFont

from config import FONTS as FD
FONTS = {'title': FD + 'RozhaOne-Regular.ttf', 'body': FD + 'NotoSansDevanagari.ttf',
         'deco': FD + 'YatraOne-Regular.ttf', 'serif': FD + 'TiroDevanagariHindi-Regular.ttf'}

# ---------------------------------------------------------------- basics
def C(h, a=1.0):
    h = h.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return skia.Color(r, g, b, int(max(0, min(1, a)) * 255))

def mix(h1, h2, t):
    a = [int(h1.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
    b = [int(h2.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
    return '#%02x%02x%02x' % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def P(color=None, stroke=0, shader=None, blend=None, alpha=None, cap_round=True):
    p = skia.Paint(AntiAlias=True)
    if color is not None:
        p.setColor(color if isinstance(color, int) else C(color))
    if alpha is not None:
        p.setAlphaf(alpha)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        if cap_round:
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
    if shader is not None:
        p.setShader(shader)
    if blend is not None:
        p.setBlendMode(blend)
    return p

def lin(x0, y0, x1, y1, cols, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)],
                                          [c if isinstance(c, int) else C(c) for c in cols], pos)

def rad(x, y, r, cols, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(x, y), max(r, 0.1),
                                          [c if isinstance(c, int) else C(c) for c in cols], pos)

def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

def lerp(a, b, t):
    return a + (b - a) * t

def smooth_path(pts, closed=False):
    """Catmull-Rom through points -> cubic path."""
    p = skia.Path()
    n = len(pts)
    if n < 2:
        return p
    p.moveTo(*pts[0])
    rng = range(n if closed else n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        p.cubicTo(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    if closed:
        p.close()
    return p

def poly(pts):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    return p

INK = '#2a1a14'

def fill_outline(cv, path, fillpaint, ow=4.0, oc=INK):
    cv.drawPath(path, fillpaint)
    if ow:
        cv.drawPath(path, P(oc, stroke=ow))

def glow(cv, x, y, r, col, a=0.8):
    cv.drawCircle(x, y, r, P(shader=rad(x, y, r, [C(col, a), C(col, a * 0.35), C(col, 0)], [0, 0.4, 1]),
                             blend=skia.BlendMode.kScreen))

def shadow(cv, x, y, w, a=0.35):
    cv.drawOval(skia.Rect.MakeXYWH(x - w / 2, y - w * 0.09, w, w * 0.18),
                P(shader=rad(x, y, w / 2, [C('#000000', a), C('#000000', 0)])))

# ---------------------------------------------------------------- text
@functools.lru_cache(maxsize=512)
def text_img(text, size, font='title', fill='#ffe9a8', stroke=0, stroke_fill='#2a1a14', shadow_px=0, maxw=0):
    f = ImageFont.truetype(FONTS[font], size, layout_engine=ImageFont.Layout.RAQM)
    lines = [text]
    if maxw:
        words, lines, cur = text.split(' '), [], ''
        for w in words:
            tst = (cur + ' ' + w).strip()
            if f.getlength(tst) > maxw and cur:
                lines.append(cur)
                cur = w
            else:
                cur = tst
        lines.append(cur)
    asc, desc = f.getmetrics()
    lh = int((asc + desc) * 1.12)
    widths = [int(f.getlength(l)) for l in lines]
    pad = stroke + shadow_px + 12
    W = max(widths) + pad * 2
    H = lh * len(lines) + pad * 2
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        x = pad + (max(widths) - widths[i]) // 2
        y = pad + i * lh
        if shadow_px:
            d.text((x + shadow_px, y + shadow_px), l, font=f, fill=(0, 0, 0, 150), stroke_width=stroke,
                   stroke_fill=(0, 0, 0, 150))
        d.text((x, y), l, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    arr = np.ascontiguousarray(np.array(im))
    return skia.Image.fromarray(arr, colorType=skia.ColorType.kRGBA_8888_ColorType)

SAMP = skia.SamplingOptions(skia.FilterMode.kLinear)

def draw_text(cv, text, x, y, size, font='title', fill='#ffe9a8', stroke=0, stroke_fill='#2a1a14',
              alpha=1.0, scale=1.0, anchor='c', shadow_px=0, maxw=0):
    im = text_img(text, size, font, fill, stroke, stroke_fill, shadow_px, maxw)
    w, h = im.width() * scale, im.height() * scale
    if anchor == 'c':
        x0, y0 = x - w / 2, y - h / 2
    elif anchor == 'l':
        x0, y0 = x, y - h / 2
    else:
        x0, y0 = x - w, y - h / 2
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(max(0, min(1, alpha)))
    cv.drawImageRect(im, skia.Rect.MakeXYWH(x0, y0, w, h), SAMP, p)
    return w, h

# ---------------------------------------------------------------- characters
class Look:
    def __init__(self, **kw):
        self.skin = '#e9b98e'
        self.cloth = '#d9a23a'
        self.cloth2 = '#8a2b2b'
        self.hair = '#2b1d16'
        self.kind = 'man'        # man, woman, sage, garuda, youth
        self.beard = None
        self.crown = None        # None, 'gold', 'tall'
        self.jewel = '#f2c232'
        self.arms4 = False
        self.halo = None
        self.brow = 'calm'       # calm, angry, sad, sly
        self.dupatta = None
        self.s = 1.0
        self.__dict__.update(kw)

LOOKS = {
    'kashyap': Look(kind='sage', skin='#e6b48a', cloth='#e8762b', cloth2='#c65a1c', hair='#e9e4da',
                    beard='#efebe2', s=1.05, halo='#ffd27a'),
    'vinata': Look(kind='woman', skin='#eab993', cloth='#2f7fc1', cloth2='#f2c232', hair='#1d1410',
                   dupatta='#f2c232', brow='sad'),
    'kadru': Look(kind='woman', skin='#d9a77f', cloth='#2e7d4f', cloth2='#7a1e5a', hair='#140d0b',
                  dupatta='#7a1e5a', brow='sly'),
    'aruna': Look(kind='youth', skin='#f08a4b', cloth='#c62828', cloth2='#ffb300', hair='#5a1d0e',
                  crown='gold', halo='#ff8a3d'),
    'garuda': Look(kind='garuda', skin='#f0b43c', cloth='#c62828', cloth2='#2e5aa8', hair='#c62828',
                   crown='gold', s=1.15, brow='angry'),
    'vishnu': Look(kind='man', skin='#4f7fd0', cloth='#f2c232', cloth2='#e65100', hair='#13101c',
                   crown='tall', arms4=True, halo='#fff2b0', s=1.12),
    'indra': Look(kind='man', skin='#efc49a', cloth='#e0e0e0', cloth2='#b71c1c', hair='#1d1410',
                  crown='gold', s=1.08, brow='angry'),
    'deva': Look(kind='man', skin='#e7b88f', cloth='#9e9e9e', cloth2='#5d4037', hair='#1d1410', crown='gold',
                 s=0.95),
}

def _eye(cv, x, y, r, blink, look_dx=0.0, angry=False, white='#ffffff', iris='#2a1a14'):
    h = r * max(0.08, 1 - blink)
    cv.drawOval(skia.Rect.MakeXYWH(x - r, y - h, 2 * r, 2 * h), P(white))
    if blink < 0.7:
        ir = r * 0.62
        cv.save()
        clip = skia.Path()
        clip.addOval(skia.Rect.MakeXYWH(x - r, y - h, 2 * r, 2 * h))
        cv.clipPath(clip, doAntiAlias=True)
        cv.drawCircle(x + look_dx * r * 0.35, y + r * 0.05, ir, P(iris))
        cv.drawCircle(x + look_dx * r * 0.35 - ir * 0.35, y - ir * 0.35, ir * 0.33, P('#ffffff'))
        cv.restore()
    cv.drawOval(skia.Rect.MakeXYWH(x - r, y - h, 2 * r, 2 * h), P(INK, stroke=2.4))

def blink_at(t, seed=0):
    ph = (t + seed * 1.7) % 3.7
    return max(0.0, 1 - abs(ph - 0.12) / 0.09) if ph < 0.25 else 0.0

def draw_wings(cv, look, flap, spread=1.0):
    """Big layered wings behind the torso. flap in [-1,1]."""
    for side in (-1, 1):
        cv.save()
        cv.translate(side * 40, -320)
        cv.scale(side, 1)
        cv.rotate(-25 * flap * spread)
        # rows: (count, length, width, colors, angle range)
        rows = [(9, 330, 34, ('#7f1414', '#c62828'), (-80, 28)),
                (8, 240, 32, ('#c62828', '#ef8f1c'), (-72, 22)),
                (7, 150, 30, ('#ef8f1c', '#ffd54f'), (-62, 16))]
        for cnt, ln, wd, (c1, c2), (a0, a1) in rows:
            for i in range(cnt):
                a = a0 + (a1 - a0) * i / (cnt - 1)
                l = ln * spread * (0.8 + 0.2 * math.sin(i * 0.9 + 1))
                cv.save()
                cv.rotate(a)
                f = smooth_path([(0, -wd * 0.35), (l * 0.5, -wd * 0.5), (l, 0), (l * 0.5, wd * 0.5), (0, wd * 0.35)],
                                closed=True)
                fill_outline(cv, f, P(shader=lin(0, 0, l, 0, [c1, c2])), 2.2)
                cv.drawLine(6, 0, l * 0.9, 0, P(C('#3a0a0a', 0.35), stroke=2))
                cv.restore()
        cv.restore()

def draw_person(cv, name, x, y, t, scale=1.0, facing=1, mouth=0.0, gesture=0.0, look_dx=0.0,
                flap=None, emotion=None, lower_fade=False, seed=0, pose='stand', no_lower=False):
    """Feet at (x,y). Height ~ 430*scale*look.s px."""
    L = LOOKS[name]
    s = scale * L.s
    cv.save()
    cv.translate(x, y)
    if pose == 'fly':
        cv.rotate(-8 * facing)
    cv.scale(s * facing, s)
    breath = 1 + 0.012 * math.sin(t * 2.2 + seed)
    sway = 2.0 * math.sin(t * 1.1 + seed)
    if pose != 'fly' and not no_lower:
        shadow(cv, 0, 0, 210)
    if L.halo:
        hy = -360 + sway * 0.3
        glow(cv, 0, hy, 170, L.halo, 0.55)
        cv.drawCircle(0, hy, 92, P(C(L.halo, 0.8), stroke=4))
    if L.kind == 'garuda':
        draw_wings(cv, L, flap if flap is not None else 0.25 * math.sin(t * 2.0), 0.78)
    bob = (1 - breath) * 200
    # ---- lower body (dhoti / saree / skirt)
    cv.save()
    if no_lower:
        cv.clipRect(skia.Rect.MakeLTRB(-300, -2000, 300, -170))
    if lower_fade:
        cv.saveLayer(None, None)
    skirt = smooth_path([(-70, -175), (70, -175), (88, -60), (78, 0), (-78, 0), (-88, -60)], closed=True)
    if pose == 'fly':
        skirt = smooth_path([(-60, -175), (60, -175), (40, -40), (-20, 30), (-70, -40)], closed=True)
    fill_outline(cv, skirt, P(shader=lin(-80, 0, 80, 0, [mix(L.cloth, '#ffffff', 0.18), L.cloth,
                                                         mix(L.cloth, '#000000', 0.35)])), 3.5)
    cv.drawLine(-60, -60, 60, -55, P(C(L.cloth2, 0.9), stroke=9))
    if pose != 'fly':
        for fx in (-38, 38):
            cv.drawOval(skia.Rect.MakeXYWH(fx - 26, -14, 52, 18), P(L.skin))
            cv.drawOval(skia.Rect.MakeXYWH(fx - 26, -14, 52, 18), P(INK, stroke=2.5))
    if lower_fade:
        fp = skia.Paint()
        fp.setShader(lin(0, -190, 0, -20, [C('#000000', 1), C('#000000', 0)]))
        fp.setBlendMode(skia.BlendMode.kDstIn)
        cv.drawRect(skia.Rect.MakeLTRB(-120, -200, 120, 40), fp)
        cv.restore()
    cv.restore()
    # ---- torso
    cv.save()
    cv.translate(0, -175)
    cv.scale(1, breath)
    cv.translate(sway * 0.4, 0)
    torso = smooth_path([(-62, 0), (-74, -120), (-58, -190), (58, -190), (74, -120), (62, 0)], closed=True)
    upper = L.skin if (L.kind in ('sage', 'garuda', 'man', 'youth') and not getattr(L, 'robe', False)) else L.cloth
    fill_outline(cv, torso, P(shader=lin(-70, -190, 70, 0, [mix(upper, '#fff3d6', 0.25), upper,
                                                            mix(upper, '#2a1020', 0.35)])), 3.5)
    if L.kind == 'woman':
        cv.drawPath(smooth_path([(-70, -150), (-20, -190), (70, -40), (40, 0)], closed=False),
                    P(C(L.dupatta or L.cloth2, 0.95), stroke=26))
    elif L.kind in ('sage', 'youth', 'man', 'garuda'):
        cv.drawPath(smooth_path([(-60, -185), (10, -110), (60, -10)]), P(C(L.cloth2, 0.95), stroke=12))
    if getattr(L, 'robe', False):
        cv.drawLine(0, -185, 0, -10, P(C(mix(L.cloth, '#000000', 0.4), 0.7), stroke=3))
        for by in (-160, -130, -100):
            cv.drawCircle(6, by, 4, P('#f2c232'))
        cv.drawRect(skia.Rect.MakeLTRB(-64, -40, 64, -18), P(L.cloth2))
        cv.drawRect(skia.Rect.MakeLTRB(-64, -40, 64, -18), P(INK, stroke=2))
    # necklace
    cv.drawPath(smooth_path([(-34, -186), (0, -150), (34, -186)]), P(C(L.jewel, 1), stroke=5))
    cv.drawCircle(0, -150, 7, P('#e53935'))
    # ---- arms
    def arm(side, raise_):
        sx = side * 66
        ex = side * (95 + 30 * raise_)
        ey = -110 - 90 * raise_
        hx = side * (90 + 70 * raise_)
        hy = -20 - 230 * raise_ + 6 * math.sin(t * 3 + side)
        path = smooth_path([(sx, -175), (ex, ey), (hx, hy)])
        cv.drawPath(path, P(INK, stroke=30))
        cv.drawPath(path, P(mix(L.cloth, '#000000', 0.12) if getattr(L, 'robe', False) else L.skin, stroke=24))
        cv.drawCircle(hx, hy, 17, P(L.skin))
        cv.drawCircle(hx, hy, 17, P(INK, stroke=2.5))
        cv.drawCircle(ex * 0.6 + hx * 0.4, ey * 0.6 + hy * 0.4, 9, P(C(L.jewel), stroke=4))
        return hx, hy
    hands = {}
    if L.arms4:
        for side in (-1, 1):
            hx, hy = arm(side, 0.85)
            hands['up%d' % side] = (hx, hy)
    hands['b'] = arm(-1, 0.05 + 0.04 * math.sin(t))
    hands['f'] = arm(1, gesture)
    cv.restore()
    # ---- head
    hy = -175 - 190 * breath - 70
    cv.save()
    cv.translate(sway * 0.6, hy + bob * 0.2)
    cv.rotate(1.5 * math.sin(t * 0.9 + seed))
    cv.drawRect(skia.Rect.MakeLTRB(-20, 30, 20, 75), P(L.skin))
    bl = blink_at(t, seed)
    if L.kind == 'garuda':
        # eagle head
        head = smooth_path([(-58, 20), (-62, -40), (-20, -78), (40, -70), (66, -30), (58, 30), (10, 52)],
                           closed=True)
        fill_outline(cv, head, P(shader=lin(-60, -70, 60, 50, ['#fff1c1', '#f0b43c', '#c77d16'])), 3.5)
        beak = smooth_path([(40, -18), (118, -8), (128, 22), (100, 16), (52, 22)], closed=True)
        fill_outline(cv, beak, P(shader=lin(40, -20, 128, 22, ['#ffcc80', '#ef6c00'])), 3)
        cv.drawPath(smooth_path([(52, 8 + 10 * mouth), (110, 18 + 8 * mouth)]), P(INK, stroke=3))
        _eye(cv, 18, -22, 15, bl, look_dx, iris='#b71c1c')
        cv.drawPath(smooth_path([(-4, -46), (36, -36)]), P(INK, stroke=6))
        for i in range(5):
            a = math.radians(140 + 18 * i)
            cv.drawPath(smooth_path([(-40, -30), (-40 + 70 * math.cos(a), -30 + 60 * math.sin(a))]),
                        P('#c62828', stroke=12))
    else:
        if L.kind == 'woman':
            cv.drawCircle(-44, -46, 34, P(L.hair))  # bun
            cv.drawCircle(-44, -46, 34, P(INK, stroke=2.5))
        face = skia.Rect.MakeXYWH(-52, -70, 104, 120)
        cv.drawOval(face, P(shader=lin(-52, -70, 52, 50, [mix(L.skin, '#fff3d6', 0.3), L.skin,
                                                          mix(L.skin, '#3a1a10', 0.25)])))
        cv.drawOval(face, P(INK, stroke=3.5))
        cv.drawCircle(-52, -2, 11, P(L.skin))
        cv.drawCircle(52, -2, 11, P(L.skin))
        cv.drawCircle(52, 12, 5, P(L.jewel))
        cv.drawCircle(-52, 12, 5, P(L.jewel))
        # hair
        if L.kind == 'sage':
            cv.drawPath(smooth_path([(-54, -10), (-50, -62), (0, -84), (50, -62), (54, -10), (38, -48), (0, -60),
                                     (-38, -48)], closed=True), P(L.hair))
            cv.drawCircle(0, -86, 26, P(L.hair))
            cv.drawCircle(0, -86, 26, P(C('#8d7e6a'), stroke=2.5))
        else:
            cv.drawPath(smooth_path([(-55, -5), (-52, -60), (0, -80), (52, -60), (55, -5), (40, -46), (0, -58),
                                     (-40, -46)], closed=True), P(L.hair))
        if L.kind == 'woman':
            cv.drawCircle(0, -40, 5.5, P('#d81b60'))  # bindi
            cv.drawPath(smooth_path([(0, -76), (0, -58)]), P('#e53935', stroke=4))
        else:
            if getattr(L, 'tilak', True):
                cv.drawPath(smooth_path([(0, -58), (0, -40)]), P(C('#e53935', 0.9), stroke=5))  # tilak
        # brows
        bdy = {'angry': (8, -8), 'sad': (-6, 6), 'sly': (-4, 6), 'calm': (0, 0)}[emotion or L.brow]
        cv.drawPath(smooth_path([(-36, -30 + bdy[0]), (-10, -32 + bdy[1])]), P(INK, stroke=5))
        cv.drawPath(smooth_path([(10, -32 + bdy[1]), (36, -30 + bdy[0])]), P(INK, stroke=5))
        _eye(cv, -22, -12, 11, bl, look_dx)
        _eye(cv, 22, -12, 11, bl, look_dx)
        cv.drawPath(smooth_path([(2, -2), (8, 16), (0, 20)]), P(C('#7a4a2a', 0.8), stroke=3))
        cv.drawCircle(-30, 14, 10, P(C('#ff6f61', 0.25)))
        cv.drawCircle(30, 14, 10, P(C('#ff6f61', 0.25)))
        mo = max(0.0, min(1.0, mouth))
        if L.beard:
            cv.drawPath(smooth_path([(-50, 0), (-40, 60), (0, 112), (40, 60), (50, 0), (30, 30), (0, 38), (-30, 30)],
                                    closed=True), P(L.beard))
            cv.drawPath(smooth_path([(-30, 22), (0, 16), (30, 22)]), P(L.beard, stroke=9))
        mw = 13 + 3 * mo
        cv.drawOval(skia.Rect.MakeXYWH(-mw, 26 - 2, 2 * mw, 4 + 15 * mo), P('#7b1f1f'))
        if mo < 0.1:
            cv.drawPath(smooth_path([(-14, 27), (0, 31 if (emotion or L.brow) != 'sad' else 25), (14, 27)]),
                        P(INK, stroke=3.5))
        else:
            cv.drawOval(skia.Rect.MakeXYWH(-mw, 26 - 2, 2 * mw, 4 + 15 * mo), P(INK, stroke=2.5))
    # crown
    if L.crown:
        tall = L.crown == 'tall'
        top = -150 if tall else -112
        crown = poly([(-46, -62), (-50, -92), (-28, -84), (-14, top + 10), (0, top), (14, top + 10), (28, -84),
                      (50, -92), (46, -62)])
        fill_outline(cv, crown, P(shader=lin(0, top, 0, -60, ['#fff59d', '#f2c232', '#b8860b'])), 3)
        cv.drawCircle(0, -78, 8, P('#e53935'))
        cv.drawCircle(-26, -72, 5, P('#43a047'))
        cv.drawCircle(26, -72, 5, P('#1e88e5'))
    if getattr(L, 'mous', None) and L.kind != 'garuda':
        mc = L.mous
        cv.drawPath(smooth_path([(-26, 26), (-12, 18), (0, 21), (12, 18), (26, 26)]), P(mc, stroke=8))
    hat = getattr(L, 'hat', None)
    if hat and L.kind != 'garuda':
        hc = getattr(L, 'hat_col', '#f5f0e1')
        if hat == 'turban':
            tb = smooth_path([(-60, -40), (-64, -84), (-30, -112), (20, -116), (58, -92), (62, -46), (30, -56), (-20, -58)], closed=True)
            fill_outline(cv, tb, P(shader=lin(-60, -116, 60, -40, [mix(hc, '#ffffff', 0.35), hc, mix(hc, '#000000', 0.25)])), 3.5)
            for k in range(3):
                cv.drawPath(smooth_path([(-56, -52 - k * 18), (0, -70 - k * 18), (56, -56 - k * 18)]), P(C(mix(hc, '#000000', 0.35), 0.6), stroke=3))
            cv.drawCircle(4, -78, 10, P('#e53935'))
            cv.drawCircle(4, -78, 10, P('#f2c232', stroke=3))
            if getattr(L, 'plume', False):
                cv.drawPath(smooth_path([(4, -88), (16, -128), (40, -150), (34, -122), (14, -92)], closed=True), P('#fafafa'))
                cv.drawPath(smooth_path([(4, -88), (16, -128), (40, -150)]), P(INK, stroke=2))
        elif hat == 'helmet':
            hm = smooth_path([(-56, -30), (-54, -70), (-20, -96), (20, -96), (54, -70), (56, -30)], closed=True)
            fill_outline(cv, hm, P(shader=lin(-56, -96, 56, -30, ['#e0e0e0', '#9e9e9e', '#616161'])), 3)
            cv.drawPath(poly([(-6, -96), (0, -136), (6, -96)]), P('#bdbdbd'))
            cv.drawLine(0, -40, 0, 10, P('#757575', stroke=6))
        elif hat == 'fez':
            fz = poly([(-40, -58), (-32, -110), (32, -110), (40, -58)])
            fill_outline(cv, fz, P(shader=lin(-40, 0, 40, 0, ['#e53935', '#b71c1c'])), 3)
            cv.drawLine(0, -110, 24, -70, P('#212121', stroke=4))
        elif hat == 'persian':
            pz = poly([(-44, -56), (-30, -150), (30, -150), (44, -56)])
            fill_outline(cv, pz, P(shader=lin(-44, 0, 44, 0, ['#424242', '#111111'])), 3)
            cv.drawRect(skia.Rect.MakeLTRB(-48, -66, 48, -52), P('#c62828'))
        elif hat == 'redcoat':
            bc = smooth_path([(-70, -58), (-40, -96), (40, -96), (70, -58), (0, -70)], closed=True)
            fill_outline(cv, bc, P('#212121'), 3)
        elif hat == 'saffron':
            tb = smooth_path([(-58, -42), (-60, -82), (-20, -110), (30, -108), (58, -80), (60, -44), (20, -56), (-24, -58)], closed=True)
            fill_outline(cv, tb, P(shader=lin(-60, -110, 60, -40, ['#ffb74d', '#ef6c00', '#bf360c'])), 3.5)
            cv.drawPath(smooth_path([(50, -70), (78, -40), (70, -10)]), P('#ef6c00', stroke=10))
    cv.restore()
    cv.restore()
    # world-space hand positions (approx) for props
    out = {}
    for k, (hx, hy) in hands.items():
        out[k] = (x + facing * s * (hx + sway * 0.4), y + s * (-175 + hy * breath))
    out['head'] = (x, y + s * (hy))
    return out

# ---------------------------------------------------------------- props
def draw_snake(cv, x, y, t, length=260, scale=1.0, color='#2e7d32', belly='#c5e1a5', hood=True, facing=1,
               phase=0.0, rise=1.0, eye='#ffeb3b', tongue=True, split_tongue=False):
    cv.save()
    cv.translate(x, y)
    cv.scale(scale * facing, scale)
    pts = []
    n = 14
    for i in range(n + 1):
        u = i / n
        px = -length * (1 - u)
        py = 18 * math.sin(u * 7 + t * 3 + phase) * (1 - u * 0.6)
        if u > 0.65:
            py -= (u - 0.65) / 0.35 * 150 * rise
            px -= (u - 0.65) * 120
        pts.append((px, py))
    path = smooth_path(pts)
    cv.drawPath(path, P(INK, stroke=32))
    cv.drawPath(path, P(color, stroke=26))
    cv.drawPath(path, P(C(belly, 0.55), stroke=9))
    for i in range(2, n - 2, 2):
        cv.drawCircle(pts[i][0], pts[i][1] - 6, 3.5, P(C('#0b3d0b', 0.6)))
    hx, hy = pts[-1]
    if hood:
        hood_p = smooth_path([(hx - 30, hy + 30), (hx - 36, hy - 10), (hx, hy - 34), (hx + 36, hy - 10),
                              (hx + 30, hy + 30)], closed=True)
        fill_outline(cv, hood_p, P(shader=lin(hx, hy - 34, hx, hy + 30, [mix(color, '#ffffff', 0.2), color])), 3)
        cv.drawPath(smooth_path([(hx - 14, hy + 6), (hx, hy - 6), (hx + 14, hy + 6)]), P(C(belly, 0.8), stroke=4))
    head = skia.Rect.MakeXYWH(hx - 4, hy - 18, 42, 30)
    cv.drawOval(head, P(color))
    cv.drawOval(head, P(INK, stroke=3))
    cv.drawCircle(hx + 22, hy - 8, 5, P(eye))
    cv.drawCircle(hx + 23, hy - 8, 2, P('#000000'))
    if tongue and (math.sin(t * 6 + phase) > 0.2 or split_tongue):
        tx = hx + 38
        cv.drawLine(tx, hy, tx + 18, hy + 2, P('#e53935', stroke=3))
        cv.drawLine(tx + 18, hy + 2, tx + 27, hy - 5, P('#e53935', stroke=2.5))
        cv.drawLine(tx + 18, hy + 2, tx + 27, hy + 9, P('#e53935', stroke=2.5))
    cv.restore()

def draw_horse(cv, x, y, t, scale=1.0, tail_dark=0.0, gallop=1.0, facing=1):
    cv.save()
    cv.translate(x, y)
    cv.scale(scale * facing, scale)
    bob = 8 * math.sin(t * 8) * gallop
    cv.translate(0, bob)
    white = '#fbfbf7'
    # legs
    for i, lx in enumerate((-110, -80, 70, 100)):
        a = math.sin(t * 8 + i * 1.6) * 25 * gallop
        cv.save()
        cv.translate(lx, -10)
        cv.rotate(a)
        cv.drawLine(0, 0, 0, 120, P(INK, stroke=24))
        cv.drawLine(0, 0, 0, 120, P('#ececec' if i % 2 else white, stroke=18))
        cv.drawRect(skia.Rect.MakeXYWH(-11, 112, 22, 14), P('#5d4037'))
        cv.restore()
    body = smooth_path([(-150, -30), (-120, -80), (60, -86), (130, -60), (140, 10), (40, 30), (-120, 26)],
                       closed=True)
    fill_outline(cv, body, P(shader=lin(0, -90, 0, 30, ['#ffffff', white, '#cfd8dc'])), 3.5)
    neck = smooth_path([(90, -70), (150, -170), (190, -190), (200, -150), (150, -40)], closed=True)
    fill_outline(cv, neck, P(shader=lin(90, -190, 200, -40, ['#ffffff', '#e0e0e0'])), 3.5)
    head = smooth_path([(180, -200), (250, -170), (262, -140), (240, -128), (190, -140)], closed=True)
    fill_outline(cv, head, P(white), 3.5)
    cv.drawCircle(214, -170, 5, P(INK))
    cv.drawPath(smooth_path([(185, -205), (196, -228), (200, -200)]), P(INK, stroke=3))
    for i in range(6):
        cv.drawPath(smooth_path([(150 + i * 9, -190 + i * 22), (120 + i * 6, -170 + i * 22 + 8 * math.sin(t * 5 + i))]),
                    P('#e3f2fd', stroke=10))
    # tail: white, gets darker with snakes
    tail_col = mix('#f5f5f5', '#1b1b1b', tail_dark)
    for k in range(3):
        tp = smooth_path([(-145, -60), (-200, -50 + k * 8), (-240 + 10 * math.sin(t * 6 + k), 20 + k * 14),
                          (-230 + 14 * math.sin(t * 5 + k), 90 + k * 10)])
        cv.drawPath(tp, P(INK, stroke=16))
        cv.drawPath(tp, P(tail_col, stroke=11))
    glow(cv, 0, -40, 260, '#bbdefb', 0.25)
    cv.restore()

def draw_egg(cv, x, y, t, scale=1.0, crack=0.0, glowk=0.0, col='#f3e5ab'):
    cv.save()
    cv.translate(x, y)
    cv.scale(scale, scale)
    shake = math.sin(t * 40) * 3 * crack
    cv.rotate(shake)
    if glowk > 0:
        glow(cv, 0, -80, 220 + 120 * glowk, '#ffd54f', 0.5 + 0.4 * glowk)
    shadow(cv, 0, 0, 140)
    egg = smooth_path([(0, -190), (62, -120), (72, -50), (40, -2), (-40, -2), (-72, -50), (-62, -120)], closed=True)
    fill_outline(cv, egg, P(shader=lin(-60, -190, 60, 0, ['#fffde7', col, mix(col, '#795548', 0.35)])), 4)
    rnd = random.Random(7)
    for _ in range(14):
        cv.drawCircle(rnd.uniform(-45, 45), rnd.uniform(-150, -20), rnd.uniform(3, 7), P(C('#a1887f', 0.45)))
    if crack > 0:
        pts = [(-50, -100)]
        for i in range(1, 7):
            pts.append((-50 + 100 * i / 6 * min(1, crack * 1.4), -100 + (14 if i % 2 else -14)))
        pp = skia.Path()
        pp.moveTo(*pts[0])
        for q in pts[1:]:
            pp.lineTo(*q)
        cv.drawPath(pp, P(INK, stroke=4))
        if crack > 0.6:
            cv.drawPath(pp, P(C('#fff59d', (crack - 0.6) * 2.5), stroke=10, blend=skia.BlendMode.kScreen))
    cv.restore()

def draw_kalash(cv, x, y, t, scale=1.0, glowk=1.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(scale, scale)
    if glowk:
        glow(cv, 0, -60, 180, '#fff59d', 0.55 * glowk)
    pot = smooth_path([(-28, -118), (28, -118), (34, -100), (66, -60), (60, -10), (30, 6), (-30, 6), (-60, -10),
                       (-66, -60), (-34, -100)], closed=True)
    fill_outline(cv, pot, P(shader=lin(-66, -120, 66, 6, ['#fff59d', '#f2c232', '#a66c00'])), 3.5)
    cv.drawRect(skia.Rect.MakeLTRB(-40, -128, 40, -114), P('#c99a1a'))
    cv.drawRect(skia.Rect.MakeLTRB(-40, -128, 40, -114), P(INK, stroke=2.5))
    cv.drawPath(smooth_path([(-56, -62), (0, -48), (56, -62)]), P('#e53935', stroke=5))
    # amrit shimmer
    for i in range(6):
        a = t * 2 + i * 1.05
        cv.drawCircle(math.cos(a) * 34, -140 - (t * 40 + i * 20) % 80, 3.5, P(C('#ffffff', 0.8)))
    cv.restore()

def draw_vajra(cv, x, y, t, scale=1.0, rot=0.0, glowk=1.0):
    cv.save()
    cv.translate(x, y)
    cv.rotate(rot)
    cv.scale(scale, scale)
    if glowk:
        glow(cv, 0, 0, 160, '#b3e5fc', 0.6 * glowk)
    cv.drawRect(skia.Rect.MakeLTRB(-14, -40, 14, 40), P('#f2c232'))
    cv.drawRect(skia.Rect.MakeLTRB(-14, -40, 14, 40), P(INK, stroke=3))
    for sgn in (-1, 1):
        for dx in (-30, 0, 30):
            pth = smooth_path([(0, sgn * 40), (dx, sgn * 80), (dx * 0.6, sgn * 120)])
            cv.drawPath(pth, P(INK, stroke=12))
            cv.drawPath(pth, P('#ffe082', stroke=7))
    cv.restore()

def draw_chakra(cv, x, y, t, r=160, speed=6.0, blades=12, col='#cfd8dc'):
    cv.save()
    cv.translate(x, y)
    cv.rotate(math.degrees(t * speed))
    glow(cv, 0, 0, r * 1.5, '#ffecb3', 0.4)
    for i in range(blades):
        cv.save()
        cv.rotate(360 / blades * i)
        blade = poly([(r * 0.55, -12), (r * 1.08, -4), (r * 1.08, 4), (r * 0.55, 12)])
        fill_outline(cv, blade, P(shader=lin(r * 0.5, 0, r * 1.1, 0, ['#ffffff', col])), 2.5)
        cv.restore()
    cv.drawCircle(0, 0, r * 0.6, P(C('#f2c232'), stroke=14))
    cv.drawCircle(0, 0, r * 0.6, P(INK, stroke=3))
    for i in range(8):
        a = math.radians(45 * i)
        cv.drawLine(0, 0, r * 0.6 * math.cos(a), r * 0.6 * math.sin(a), P('#b8860b', stroke=6))
    cv.drawCircle(0, 0, 22, P('#f2c232'))
    cv.restore()

def draw_flames(cv, x0, x1, base, t, height=320, n=14, alpha=1.0):
    rnd = random.Random(3)
    for layer, (col1, col2, hk) in enumerate([('#b71c1c', '#ff5722', 1.0), ('#ff6f00', '#ffca28', 0.75),
                                               ('#ffe082', '#ffffff', 0.45)]):
        for i in range(n):
            fx = lerp(x0, x1, (i + 0.5) / n) + rnd.uniform(-20, 20)
            h = height * hk * (0.7 + 0.3 * math.sin(t * 7 + i * 1.7 + layer)) * rnd.uniform(0.8, 1.1)
            w = (x1 - x0) / n * 0.9
            sway = 18 * math.sin(t * 5 + i)
            fl = smooth_path([(fx - w / 2, base), (fx - w * 0.35, base - h * 0.4), (fx + sway, base - h),
                              (fx + w * 0.35, base - h * 0.45), (fx + w / 2, base)], closed=True)
            cv.drawPath(fl, P(shader=lin(fx, base, fx, base - h, [C(col1, alpha), C(col2, alpha * 0.9)])))
    glow(cv, (x0 + x1) / 2, base - height * 0.4, (x1 - x0) * 0.6, '#ff6f00', 0.45 * alpha)

def draw_kusha(cv, x, y, t, w=300, n=26, scale=1.0, col='#7cb342'):
    rnd = random.Random(11)
    for i in range(n):
        bx = x - w / 2 + w * i / (n - 1) + rnd.uniform(-6, 6)
        h = rnd.uniform(70, 150) * scale
        lean = rnd.uniform(-25, 25) + 6 * math.sin(t * 1.5 + i)
        pth = smooth_path([(bx, y), (bx + lean * 0.4, y - h * 0.6), (bx + lean, y - h)])
        cv.drawPath(pth, P(INK, stroke=6))
        cv.drawPath(pth, P(mix(col, '#dce775', rnd.random() * 0.5), stroke=3.5))

def draw_sun(cv, x, y, r, t, a=1.0):
    glow(cv, x, y, r * 3.2, '#ffcc80', 0.6 * a)
    cv.drawCircle(x, y, r, P(shader=rad(x, y, r, [C('#fffde7', a), C('#ffd54f', a), C('#ff8f00', a)])))
    for i in range(16):
        ang = math.radians(i * 22.5 + t * 6)
        cv.drawLine(x + r * 1.15 * math.cos(ang), y + r * 1.15 * math.sin(ang),
                    x + r * 1.55 * math.cos(ang), y + r * 1.55 * math.sin(ang), P(C('#ffe082', 0.8 * a), stroke=6))

def draw_chariot(cv, x, y, t, scale=1.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(scale, scale)
    body = poly([(-120, -110), (110, -110), (140, -20), (-140, -20)])
    fill_outline(cv, body, P(shader=lin(0, -110, 0, -20, ['#fff59d', '#f2c232', '#b8860b'])), 3.5)
    for wx in (-80, 80):
        cv.save()
        cv.translate(wx, -10)
        cv.rotate(math.degrees(t * 3))
        cv.drawCircle(0, 0, 46, P('#8d5a1e', stroke=10))
        for k in range(8):
            a = math.radians(45 * k)
            cv.drawLine(0, 0, 46 * math.cos(a), 46 * math.sin(a), P('#8d5a1e', stroke=5))
        cv.restore()
    cv.restore()

def draw_hut(cv, x, y, s=1.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    walls = poly([(-120, 0), (-120, -130), (120, -130), (120, 0)])
    fill_outline(cv, walls, P(shader=lin(0, -130, 0, 0, ['#d7b98a', '#a8865a'])), 3.5)
    roof = smooth_path([(-170, -120), (0, -250), (170, -120), (140, -110), (0, -215), (-140, -110)], closed=True)
    fill_outline(cv, roof, P(shader=lin(0, -250, 0, -110, ['#c9a227', '#8a6d1d'])), 3.5)
    cv.drawRect(skia.Rect.MakeLTRB(-30, -90, 30, 0), P('#4e342e'))
    cv.restore()

def draw_tree(cv, x, y, s=1.0, col='#2e7d32', t=0.0, dark=0.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    trunk = poly([(-18, 0), (-12, -170), (12, -170), (18, 0)])
    cv.drawPath(trunk, P(mix('#5d4037', '#0d0a14', dark)))
    sway = 4 * math.sin(t * 0.8 + x)
    for (cx, cy, r) in [(-60, -200, 80), (60, -205, 85), (0, -270, 100), (-20, -170, 70), (40, -160, 65)]:
        c1 = mix(mix(col, '#ffffff', 0.12), '#0d0a14', dark)
        c2 = mix(mix(col, '#000000', 0.3), '#0d0a14', dark)
        cv.drawCircle(cx + sway, cy, r, P(shader=rad(cx - r * 0.3 + sway, cy - r * 0.3, r * 1.3, [c1, c2])))
    cv.restore()

def draw_pillar(cv, x, y, h, w=70, col='#f5e6c8'):
    body = skia.Rect.MakeLTRB(x - w / 2, y - h, x + w / 2, y)
    cv.drawRect(body, P(shader=lin(x - w / 2, 0, x + w / 2, 0, [mix(col, '#ffffff', 0.4), col,
                                                                 mix(col, '#7a5a30', 0.4)])))
    cv.drawRect(skia.Rect.MakeLTRB(x - w * 0.7, y - h - 26, x + w * 0.7, y - h), P('#e0c27a'))
    cv.drawRect(skia.Rect.MakeLTRB(x - w * 0.7, y - 22, x + w * 0.7, y), P('#e0c27a'))
    for i in range(3):
        cv.drawLine(x - w / 2 + w * (i + 1) / 4, y - h + 10, x - w / 2 + w * (i + 1) / 4, y - 30,
                    P(C('#8d6e43', 0.35), stroke=3))

def cloud(cv, x, y, s, col='#ffffff', a=0.9):
    for (dx, dy, r) in [(-60, 0, 50), (0, -20, 65), (60, 0, 50), (-20, 15, 45), (35, 15, 45)]:
        cv.drawCircle(x + dx * s, y + dy * s, r * s, P(shader=rad(x + dx * s, y + (dy - 20) * s, r * s * 1.3,
                                                                  [C(mix(col, '#ffffff', 0.4), a), C(col, a)])))

# ---------------------------------------------------------------- backgrounds (layers drawn in world coords)
def bg_sky(cv, top, mid, bot):
    cv.drawRect(skia.Rect.MakeLTRB(-1400, -1400, 3400, 2600), P(shader=lin(0, -500, 0, 1300, [top, mid, bot])))

def mountains(cv, base, col, seed, amp=220, n=9, dark=0.0):
    rnd = random.Random(seed)
    pts = [(-1400, 2600), (-1400, base)]
    for i in range(n * 3 + 1):
        x = -1400 + 4800 * i / (n * 3)
        pts.append((x, base - rnd.uniform(0.3, 1.0) * amp))
    pts += [(3400, base), (3400, 2600)]
    cv.drawPath(smooth_path(pts, closed=True), P(shader=lin(0, base - amp, 0, base + 400,
                                                            [mix(col, '#ffffff', 0.1), mix(col, '#000000', dark)])))

def ground(cv, y, c1, c2):
    cv.drawRect(skia.Rect.MakeLTRB(-1400, y, 3400, 2600), P(shader=lin(0, y, 0, y + 500, [c1, c2])))

def stars(cv, t, n=160, seed=5, a=1.0):
    rnd = random.Random(seed)
    for i in range(n):
        x, y = rnd.uniform(-1200, 3200), rnd.uniform(-1200, 600)
        tw = 0.5 + 0.5 * math.sin(t * rnd.uniform(1, 3) + i)
        cv.drawCircle(x, y, rnd.uniform(1, 3), P(C('#ffffff', a * (0.3 + 0.7 * tw))))

# ---------------------------------------------------------------- fx
class Particles:
    def __init__(self, kind, n=60, seed=1, area=(-400, -500, 2320, 1500)):
        self.kind, self.n = kind, n
        rnd = random.Random(seed)
        self.p = [(rnd.uniform(area[0], area[2]), rnd.uniform(area[1], area[3]), rnd.uniform(0.5, 1.5),
                   rnd.uniform(0, 6.28)) for _ in range(n)]
        self.area = area

    def draw(self, cv, t, alpha=1.0):
        x0, y0, x1, y1 = self.area
        H = y1 - y0
        W = x1 - x0
        for (x, y, s, ph) in self.p:
            if self.kind == 'embers':
                yy = y0 + (y - y0 - t * 90 * s) % H
                xx = x + 30 * math.sin(t * 1.5 + ph)
                cv.drawCircle(xx, yy, 2.5 * s, P(C('#ffb74d', alpha * (0.5 + 0.5 * math.sin(t * 6 + ph))),
                                                  blend=skia.BlendMode.kScreen))
            elif self.kind == 'dust':
                yy = y0 + (y - y0 - t * 12 * s) % H
                xx = x0 + (x - x0 + t * 15 * s) % W
                cv.drawCircle(xx, yy, 2.2 * s, P(C('#fff8e1', alpha * 0.35 * (0.6 + 0.4 * math.sin(t + ph))),
                                                  blend=skia.BlendMode.kScreen))
            elif self.kind == 'sparkle':
                yy = y0 + (y - y0 - t * 30 * s) % H
                a = max(0, math.sin(t * 3 + ph))
                r = 7 * s * a
                if r > 0.5:
                    pp = P(C('#fffde7', alpha * a), blend=skia.BlendMode.kScreen)
                    cv.drawPath(poly([(x, yy - r * 2), (x + r * 0.4, yy), (x, yy + r * 2), (x - r * 0.4, yy)]), pp)
                    cv.drawPath(poly([(x - r * 2, yy), (x, yy - r * 0.4), (x + r * 2, yy), (x, yy + r * 0.4)]), pp)
            elif self.kind == 'leaves':
                yy = y0 + (y - y0 + t * 60 * s) % H
                xx = x0 + (x - x0 + t * 50 * s + 40 * math.sin(t * 2 + ph)) % W
                cv.save()
                cv.translate(xx, yy)
                cv.rotate(math.degrees(t * 2 + ph))
                cv.drawOval(skia.Rect.MakeXYWH(-8 * s, -4 * s, 16 * s, 8 * s), P(C('#c0ca33', alpha * 0.8)))
                cv.restore()
            elif self.kind == 'rain':
                yy = y0 + (y - y0 + t * 900 * s) % H
                cv.drawLine(x, yy, x - 8, yy + 30, P(C('#b3e5fc', alpha * 0.35), stroke=2))

def fog(cv, t, y, col='#ffffff', a=0.25, speed=20):
    for i in range(5):
        x = ((i * 700 + t * speed * (1 + i * 0.2)) % 3600) - 900
        cv.drawOval(skia.Rect.MakeXYWH(x - 500, y - 90 + 30 * math.sin(i), 1000, 180),
                    P(shader=rad(x, y, 500, [C(col, a), C(col, 0)])))

def rays(cv, x, y, t, col='#fff3c4', a=0.18, n=7, spread=70, length=1800):
    for i in range(n):
        ang = math.radians(90 - spread / 2 + spread * i / (n - 1) + 2 * math.sin(t * 0.5 + i))
        w = 50 + 30 * math.sin(t + i * 2)
        dx, dy = math.cos(ang), math.sin(ang)
        px, py = -dy, dx
        pth = poly([(x - px * 10, y - py * 10), (x + px * 10, y + py * 10),
                    (x + dx * length + px * w * 3, y + dy * length + py * w * 3),
                    (x + dx * length - px * w * 3, y + dy * length - py * w * 3)])
        cv.drawPath(pth, P(shader=lin(x, y, x + dx * length, y + dy * length, [C(col, a), C(col, 0)]),
                           blend=skia.BlendMode.kScreen))

def draw_elephant(cv, x, y, t, scale=1.0, facing=1, push=0.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(scale * facing, scale)
    g1, g2 = '#a3a7b3', '#5f6472'
    for i, lx in enumerate((-120, -60, 60, 110)):
        cv.drawRect(skia.Rect.MakeXYWH(lx - 26, -110, 52, 115), P(shader=lin(lx - 26, 0, lx + 26, 0, [g1, g2])))
        cv.drawRect(skia.Rect.MakeXYWH(lx - 26, -110, 52, 115), P(INK, stroke=3))
    body = skia.Rect.MakeXYWH(-190, -300, 360, 230)
    cv.drawOval(body, P(shader=lin(0, -300, 0, -70, ['#c5c9d4', g1, g2])))
    cv.drawOval(body, P(INK, stroke=3.5))
    hx, hy = 170, -250
    cv.drawCircle(hx, hy, 95, P(shader=rad(hx - 30, hy - 30, 130, ['#c5c9d4', g1])))
    cv.drawCircle(hx, hy, 95, P(INK, stroke=3.5))
    ear = smooth_path([(hx - 40, hy - 70), (hx - 140, hy - 40), (hx - 130, hy + 70), (hx - 40, hy + 50)], closed=True)
    fill_outline(cv, ear, P(shader=lin(hx - 140, 0, hx - 40, 0, [g2, g1])), 3)
    sw = 30 * math.sin(t * 3) + 40 * push
    trunk = smooth_path([(hx + 70, hy + 20), (hx + 120, hy + 110), (hx + 110 + sw * 0.5, hy + 210), (hx + 150 + sw, hy + 240)])
    cv.drawPath(trunk, P(INK, stroke=44))
    cv.drawPath(trunk, P(g1, stroke=38))
    cv.drawPath(smooth_path([(hx + 50, hy + 50), (hx + 120, hy + 80), (hx + 160, hy + 60)]), P('#fffde7', stroke=14))
    cv.drawCircle(hx + 30, hy - 20, 9, P(INK))
    cv.restore()

def draw_tortoise(cv, x, y, t, scale=1.0, facing=1):
    cv.save()
    cv.translate(x, y)
    cv.scale(scale * facing, scale)
    for lx in (-120, -50, 50, 120):
        cv.drawOval(skia.Rect.MakeXYWH(lx - 30, -40, 60, 50), P('#8d9a4a'))
        cv.drawOval(skia.Rect.MakeXYWH(lx - 30, -40, 60, 50), P(INK, stroke=3))
    nx = 170 + 20 * math.sin(t * 2.5)
    cv.drawPath(smooth_path([(120, -60), (nx, -110), (nx + 30, -100)]), P(INK, stroke=50))
    cv.drawPath(smooth_path([(120, -60), (nx, -110), (nx + 30, -100)]), P('#9aa857', stroke=44))
    cv.drawCircle(nx + 34, -108, 34, P('#9aa857'))
    cv.drawCircle(nx + 34, -108, 34, P(INK, stroke=3))
    cv.drawCircle(nx + 46, -118, 6, P(INK))
    shell = smooth_path([(-200, -20), (-170, -150), (0, -230), (170, -150), (200, -20)], closed=True)
    fill_outline(cv, shell, P(shader=lin(0, -230, 0, -20, ['#8d6e43', '#5d4632', '#3e2e22'])), 4)
    for (cx, cy) in [(0, -150), (-100, -110), (100, -110), (-60, -60), (60, -60)]:
        hexp = poly([(cx + 40 * math.cos(math.radians(60 * k)), cy + 32 * math.sin(math.radians(60 * k))) for k in range(6)])
        cv.drawPath(hexp, P(C('#c9a46a', 0.6), stroke=4))
    cv.drawRect(skia.Rect.MakeLTRB(-205, -30, 205, -10), P('#a1887f'))
    cv.restore()

def draw_sage_tiny(cv, x, y, t, scale=0.18, hang=True, seed=0):
    """Tiny Valakhilya sage; if hang, upside down from (x,y)."""
    cv.save()
    cv.translate(x, y)
    if hang:
        cv.drawLine(0, 0, 0, 30, P('#5d4037', stroke=2))
        cv.translate(0, 30)
        cv.rotate(180 + 4 * math.sin(t * 2 + seed))
        cv.translate(0, 0)
    draw_person(cv, 'kashyap', 0, 0, t, scale=scale, seed=seed)
    cv.restore()

def draw_big_tree(cv, x, y, t, bend=0.0, branch=True):
    cv.save()
    cv.translate(x, y)
    trunk = poly([(-70, 0), (-50, -520), (50, -520), (70, 0)])
    cv.drawPath(trunk, P(shader=lin(-70, 0, 70, 0, ['#8d6e43', '#5d4037', '#3e2723'])))
    cv.drawPath(trunk, P(INK, stroke=4))
    for (cx, cy, r) in [(-150, -620, 170), (120, -640, 180), (0, -760, 200), (-260, -540, 120), (240, -540, 130)]:
        cv.drawCircle(cx, cy, r, P(shader=rad(cx - r * 0.3, cy - r * 0.3, r * 1.3, ['#5aa04a', '#1f5a2a'])))
    if branch:
        cv.save()
        cv.translate(-40, -420)
        cv.rotate(bend * 12)
        br = smooth_path([(0, -18), (-400, -40), (-720, -10), (-720, 12), (-400, -8), (0, 22)], closed=True)
        fill_outline(cv, br, P(shader=lin(0, -30, 0, 30, ['#8d6e43', '#4e342e'])), 3)
        for k in range(6):
            draw_sage_tiny(cv, -150 - k * 95, 8, t, seed=k)
        cv.restore()
    cv.restore()
