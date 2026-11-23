"""40 animated beats synced to the merged narration (times in final-video seconds)."""
import math, random
from mengine import *

def TA(s): return s                       # mughal part 1 (0..200.55)
def TB(s): return 201.75 + (s - 97.6)     # panipat part
def TC(s): return 403.25 + (s - 274.0)    # mughal part 2
END = TC(462.3) + 2.0

# Narration pieces glued into the final timeline: (wav file in src/, start s, end s, position in final video s)
SEGMENTS = [('mughal.wav', 0.0, 200.55, TA(0.0)),
            ('panipat.wav', 97.6, 297.6, TB(97.6)),
            ('mughal.wav', 274.0, 462.3, TC(274.0))]

_draw_map0 = draw_map
def draw_map(cv, t, highlight=None, **kw):
    _draw_map0(cv, t, highlight=highlight, **kw)
    for nm in (highlight or []):
        if nm not in PLACES:
            continue
        x, y = PLACES[nm]
        for k in range(3):
            u = (t * 0.6 + k / 3) % 1
            cv.drawCircle(x, y, 10 + 70 * u, P(C('#b71c1c', 0.7 * (1 - u)), stroke=4))
        cv.drawCircle(x, y, 9, P('#b71c1c'))
        cv.drawCircle(x, y, 9, P('#ffffff', stroke=3))

def W_(a, b, x):
    return ease((x - a) / max(1e-6, b - a))

def cam(x, y, z): return (x, y, z)
WIDE = ((960, 540, 1.0), (960, 540, 1.08))

# ------------------------------------------------------------------ acts (c: t global, bt beat time, bp progress)
def a_title(cv, c):
    t, p = c['t'], c['bp']
    draw_throne(cv, 960, 980, 1.0, peacock=True, t=t)
    draw_crown2(cv, 960, 420 - 10 * math.sin(t * 2), 1.0, a=1)
    Particles('sparkle', 50, 2, (400, 200, 1520, 900)).draw(cv, t)

def a_book(cv, c):
    t, p = c['t'], c['bp']
    cv.drawRect(skia.Rect.MakeLTRB(-1400, -1400, 3400, 2600), P(shader=rad(960, 540, 1100, ['#5d4037', '#1b100b'])))
    glow(cv, 960, 500, 600, '#ffcc80', 0.35)
    # open book
    for side in (-1, 1):
        pg = smooth_path([(960, 780), (960 + side * 520, 800), (960 + side * 540, 300), (960, 280)], closed=True)
        fill_outline(cv, pg, P(shader=lin(960, 0, 960 + side * 540, 0, ['#e8d3a8', '#f7ead0'])), 4)
        for k in range(8):
            yy = 360 + k * 50
            cv.drawLine(960 + side * 60, yy, 960 + side * 470, yy + 6, P(C('#8d6e63', 0.35), stroke=3))
    # turning page
    k = (c['bt'] * 0.7) % 1.0
    ang = math.pi * ease(k)
    x2 = 960 + 520 * math.cos(ang)
    pg = smooth_path([(960, 780), (x2, 790 - 40 * math.sin(ang)), (x2 + 20 * math.cos(ang), 300 - 40 * math.sin(ang)), (960, 280)], closed=True)
    fill_outline(cv, pg, P(C('#fff3dc', 0.95)), 3)
    Particles('dust', 50, 3, (300, 200, 1620, 900)).draw(cv, t, 1.0)

def a_coup(cv, c):
    t, p, bt = c['t'], c['bp'], c['bt']
    # throne room silhouettes: sword clash, throne changes hands
    draw_throne(cv, 960, 900, 0.7, t=t)
    k = W_(0.0, 0.45, p)
    if p < 0.5:
        draw_person(cv, 'noble', 960, 900, t, scale=0.8, seed=1, emotion='sad')
    for i, side in enumerate((-1, 1)):
        x = 960 + side * lerp(700, 260, k)
        draw_person(cv, 'uzbek' if side < 0 else 'shersha', x, 960, t, scale=0.9, facing=-side, gesture=0.8, seed=i,
                    emotion='angry')
        sx = x - side * 90
        cv.drawLine(sx, 520, sx - side * 120 * math.sin(t * 6), 420, P('#cfd8dc', stroke=8))
    if p >= 0.5:
        draw_person(cv, 'lodi', 960, 900, t, scale=0.8, seed=2, emotion='sly')
        draw_crown2(cv, 960, 470, 0.5, a=0.8)
    if 0.45 < p < 0.55:
        cv.drawRect(skia.Rect.MakeLTRB(-1400, -1400, 3400, 2600), P(C('#ffffff', 1 - abs(p - 0.5) / 0.05)))

def a_throne_guard(cv, c):
    t = c['t']
    draw_throne(cv, 960, 930, 0.8, t=t)
    draw_person(cv, 'noble', 960, 930, t, scale=0.85, emotion='sad', look_dx=math.sin(t * 2))
    for x in (520, 1400):
        draw_person(cv, 'uzbek', x, 980, t, scale=0.85, facing=1 if x < 960 else -1, gesture=0.1, emotion='angry')

def a_fergana_boy(cv, c):
    t, p = c['t'], c['bp']
    draw_person(cv, 'babur_boy', 900, 960, t, scale=1.2, look_dx=1, emotion='sad' if p > 0.6 else 'calm', gesture=0.15)
    Particles('leaves', 30, 2).draw(cv, t)

def a_coronation(cv, c):
    t, p = c['t'], c['bp']
    draw_throne(cv, 960, 930, 0.9, t=t)
    draw_person(cv, 'babur_boy', 960, 930, t, scale=1.0, gesture=0.3)
    draw_crown2(cv, 960, lerp(200, 450, W_(0.05, 0.3, p)), 0.45, a=0.8)
    if p > 0.45:
        a = W_(0.45, 0.6, p)
        cv.saveLayerAlpha(None, int(255 * a))
        for i, (x, f) in enumerate(((420, 1), (600, 1), (1320, -1), (1500, -1))):
            draw_person(cv, 'noble' if i % 2 else 'uzbek', x, 990, t, scale=0.8, facing=f, emotion='sly', seed=i,
                        gesture=0.2 + 0.3 * (i % 2))
        cv.restore()

def a_lineage(cv, c):
    t, p = c['t'], c['bp']
    cv.drawRect(skia.Rect.MakeLTRB(-1400, -1400, 3400, 2600), P(shader=rad(960, 540, 1200, ['#3b1d4a', '#0b0614'])))
    draw_person(cv, 'babur_boy', 960, 1000, t, scale=1.1, gesture=0.3)
    for side, nm in ((-1, 'timur'), (1, 'genghis')):
        a = W_(0.1 if side < 0 else 0.35, 0.3 if side < 0 else 0.55, p)
        if a > 0:
            x = 960 + side * 520
            glow(cv, x, 450, 360, '#ffcc80' if side < 0 else '#ef9a9a', 0.35 * a)
            cv.saveLayerAlpha(None, int(230 * a))
            draw_person(cv, nm, x, 850, t, scale=1.0, facing=-side, gesture=0.6, seed=side)
            cv.restore()
            cv.drawPath(smooth_path([(x - side * 100, 520), (960 + side * 120, 640)]), P(C('#ffd54f', 0.8 * a), stroke=5))

def a_exile(cv, c):
    t, p = c['t'], c['bp']
    draw_person(cv, 'babur_boy', lerp(1300, 700, p), 980, t, scale=1.0, facing=-1, emotion='sad', seed=3)
    cavalry(cv, 1700 + 300 * (1 - p), 2500, 1000, 1, t, 'uzbek', facing=-1, s=0.9, speed=0)
    Particles('rain', 120, 4).draw(cv, t)

def a_hindukush(cv, c):
    t, p = c['t'], c['bp']
    army(cv, -200 + 900 * p, 700 + 900 * p, 1010, 3, t, 'mughal', facing=1, s=0.8, march=1.0)
    rider(cv, 'babur', 820 + 900 * p, 1000, t, scale=0.9, gallop=0.6)
    Particles('rain', 0).draw(cv, t)
    for i in range(80):
        rnd = random.Random(i)
        x = (rnd.uniform(-400, 2400) + t * 40) % 2800 - 400
        y = (rnd.uniform(-200, 1200) + t * 120 * rnd.uniform(0.5, 1.2)) % 1400 - 200
        cv.drawCircle(x, y, rnd.uniform(2, 5), P(C('#ffffff', 0.8)))

def a_kabul(cv, c):
    t, p = c['t'], c['bp']
    draw_flag(cv, 1430, 520, 200, t, col='#1f5f8b', col2='#f2c232', s=W_(0.2, 0.6, p) + 0.01)
    rider(cv, 'babur', 700, 1000, t, scale=1.0, gallop=0.2, gesture=0.8)
    army(cv, 100, 520, 1010, 2, t, 'mughal', s=0.8, march=0.3)

def a_treasury(cv, c):
    t, p = c['t'], c['bp']
    draw_person(cv, 'babur', 680, 990, t, scale=1.05, emotion='sad', gesture=0.3)
    # empty chest
    cv.drawRect(skia.Rect.MakeLTRB(1050, 820, 1450, 990), P('#6d4c41'))
    cv.drawRect(skia.Rect.MakeLTRB(1050, 820, 1450, 990), P(INK, stroke=4))
    cv.save(); cv.translate(1050, 820); cv.rotate(-40 * W_(0.05, 0.3, p))
    cv.drawRect(skia.Rect.MakeLTRB(0, -60, 400, 0), P('#8d6e63')); cv.drawRect(skia.Rect.MakeLTRB(0, -60, 400, 0), P(INK, stroke=4))
    cv.restore()
    for i in range(3):
        cv.drawCircle(1250 + 40 * math.sin(t * 2 + i), 760 - ((t * 60 + i * 40) % 120), 8, P(C('#9e9e9e', 0.6)))
    if p > 0.5:
        a = W_(0.5, 0.7, p)
        cv.saveLayerAlpha(None, int(200 * a))
        army(cv, 100, 560, 1010, 2, t, 'mughal', s=0.7, march=0.0)
        cv.restore()

def a_map_south(cv, c):
    t, p = c['t'], c['bp']
    draw_map(cv, t, route=lerp(0.55, 1.0, W_(0.0, 0.7, p)), highlight=['काबुल', 'दिल्ली'])
    if p > 0.45:
        for i in range(10):
            a = t * 1.5 + i * 0.63
            gx, gy = 1075 + 90 * math.cos(a), 650 + 60 * math.sin(a)
            cv.drawCircle(gx, gy, 12, P('#f2c232'))
            cv.drawCircle(gx, gy, 12, P('#a66c00', stroke=2))

def a_pawn(cv, c):
    t, p = c['t'], c['bp']
    cv.drawRect(skia.Rect.MakeLTRB(-1400, -1400, 3400, 2600), P(shader=rad(960, 400, 1300, ['#4a3426', '#140b07'])))
    draw_chess(cv, 1100, 980, 1.0, t)
    px = lerp(820, 1010, W_(0.15, 0.4, p))
    draw_pawn(cv, px, 860, 1.0, col='#f5f0e1', glowk=W_(0.6, 0.85, p))
    draw_pawn(cv, 1300, 800, 0.8, col='#3e2723')
    draw_pawn(cv, 1500, 760, 0.7, col='#3e2723')
    draw_person(cv, 'daulat', 360, 1060, t, scale=1.1, emotion='sly', gesture=0.6, look_dx=1)
    if p > 0.7:
        draw_text(cv, 'बाबर', px, 680, 54, 'title', '#ffd54f', stroke=4, alpha=W_(0.7, 0.8, p))

def a_not_merc(cv, c):
    t, p = c['t'], c['bp']
    draw_person(cv, 'babur', 960, 1000, t, scale=1.25, gesture=0.9 * W_(0.2, 0.4, p), emotion='angry')
    cv.drawLine(1080, 420, 1180, 240, P('#cfd8dc', stroke=10))
    glow(cv, 1180, 240, 80, '#ffffff', 0.6 * W_(0.2, 0.4, p))

def inr(n):
    s = str(n)
    if len(s) <= 3:
        return s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:]); head = head[:-2]
    if head:
        parts.insert(0, head)
    return ','.join(parts) + ',' + tail

def a_vs(cv, c):
    t, p = c['t'], c['bp']
    cv.drawLine(960, 0, 960, 1080, P(C('#ffd54f', 0.8), stroke=6))
    army(cv, 1000, 1900, 1010, 6, t, 'lodi', facing=-1, s=0.62, march=0.4, seed=2)
    for ex in (1200, 1500, 1800):
        draw_elephant(cv, ex, 790, t, scale=0.38, facing=-1)
    army(cv, 300, 860, 1010, 3, t, 'mughal', facing=1, s=0.62, march=0.4, seed=3)
    n1 = int(100000 * W_(0.05, 0.4, p))
    n2 = int(12000 * W_(0.45, 0.75, p))
    if p > 0.05:
        draw_text(cv, inr(n1), 1450, 300, 120, 'title', '#ef5350', stroke=6)
        draw_text(cv, 'लोदी की सेना', 1450, 420, 56, 'title', '#ffffff', stroke=4)
    if p > 0.45:
        draw_text(cv, inr(n2), 580, 300, 120, 'title', '#4fc3f7', stroke=6)
        draw_text(cv, 'बाबर की सेना', 580, 420, 56, 'title', '#ffffff', stroke=4)

def a_indus(cv, c):
    t, p = c['t'], c['bp']
    army(cv, -300 + 1200 * p, 600 + 1200 * p, 1000, 3, t, 'mughal', s=0.8)
    rider(cv, 'babur', 700 + 1200 * p, 990, t, scale=0.9, gallop=0.8)
    for i in range(2):
        draw_cannon(cv, 200 + 1200 * p - i * 260, 1010, t, s=0.6)

def a_tent(cv, c):
    t, p = c['t'], c['bp']
    cv.drawRect(skia.Rect.MakeLTRB(-1400, -1400, 3400, 2600), P(shader=rad(960, 600, 1200, ['#6d4c2f', '#1a0f08'])))
    cv.drawPath(poly([(-200, 0), (960, -300), (2120, 0)]), P('#3e2a1a'))
    cv.drawRect(skia.Rect.MakeLTRB(560, 760, 1360, 820), P('#5d4037'))
    cv.drawRect(skia.Rect.MakeLTRB(620, 700, 1300, 770), P('#e8d3a8'))
    for k in range(6):
        cv.drawLine(680 + k * 100, 715, 720 + k * 100, 755, P(C('#b71c1c', 0.7), stroke=4))
    fl = 1 + 0.15 * math.sin(t * 13) + 0.1 * math.sin(t * 7)
    glow(cv, 1380, 640, 260 * fl, '#ffb74d', 0.7)
    cv.drawRect(skia.Rect.MakeLTRB(1370, 650, 1390, 740), P('#fff3e0'))
    cv.drawOval(skia.Rect.MakeXYWH(1372, 620 - 8 * fl, 16, 30 * fl), P('#ffca28'))
    draw_person(cv, 'babur', 960, 1060, t, scale=1.05, gesture=0.55 + 0.1 * math.sin(t), look_dx=-0.5, emotion='calm')

def a_gunners(cv, c):
    t, p = c['t'], c['bp']
    draw_person(cv, 'gunner', 600, 990, t, scale=1.0, gesture=0.5, seed=1)
    draw_person(cv, 'gunner', 860, 990, t, scale=0.95, gesture=0.2, seed=2, facing=-1)
    draw_cannon(cv, 1350, 1000, t, s=1.6, fire=(c['bt'] - c['bd'] * 0.75) if p > 0.75 else -1)

def a_cannons(cv, c):
    t, p, bt = c['t'], c['bp'], c['bt']
    for i in range(5):
        draw_cannon(cv, 260 + i * 330, 1000, t, s=1.0, fire=((bt - i * 0.45) % 2.6) if bt > 1 else -1)
    army(cv, 200, 1700, 860, 1, t, 'mughal', s=0.7, march=0, weapon='gun')

def a_swords(cv, c):
    t, p = c['t'], c['bp']
    army(cv, 1000, 1900, 1010, 4, t, 'lodi', facing=-1, s=0.8, march=0.6, weapon='sword')
    for i in range(3):
        draw_cannon(cv, 250 + i * 250, 1010, t, s=0.85, fire=((c['bt'] - i * 0.5) % 2.4))
    cv.drawLine(960, 300, 960, 1080, P(C('#ffd54f', 0.6), stroke=4))
    draw_text(cv, 'तलवार-भाले', 1450, 300, 64, 'title', '#ffffff', stroke=4)
    draw_text(cv, 'बारूद', 480, 300, 72, 'title', '#ffca28', stroke=4)

def a_wagons(cv, c):
    t, p, bt = c['t'], c['bp'], c['bt']
    link = W_(0.08, 0.45, p)
    wagon_wall(cv, -200, 2100, 1000, t, s=0.75, link=link, gunners=p > 0.5, fire_t=(bt - c['bd'] * 0.65) if p > 0.65 else -1)
    draw_person(cv, 'babur', 960, 1080, t, scale=0.85, gesture=0.7 if p < 0.5 else 0.3, look_dx=math.sin(t * 0.5))

def a_tulughma(cv, c):
    t, p = c['t'], c['bp']
    # top-down tactical diagram on parchment
    cv.drawLine(150, 500, 1770, 500, P(C('#6d4c41', 0.15), stroke=600))
    # wagon line
    for i in range(14):
        x = 520 + i * 62
        cv.drawRect(skia.Rect.MakeXYWH(x, 640, 44, 22), P('#6d4c41'))
    draw_text(cv, 'गाड़ियों की दीवार', 960, 700, 34, 'title', '#3e2723')
    for i in range(4):
        cv.drawCircle(640 + i * 220, 680, 14, P('#212121'))
    # babur center block
    cv.drawRect(skia.Rect.MakeXYWH(800, 730, 320, 90), P(C('#1f5f8b', 0.9)))
    draw_text(cv, 'बाबर', 960, 775, 40, 'title', '#ffffff')
    # lodi mass advancing from top, squeezing into narrow
    adv = W_(0.05, 0.5, p)
    lw = lerp(1200, 620, adv)
    ly = lerp(160, 360, adv)
    cv.drawRect(skia.Rect.MakeXYWH(960 - lw / 2, ly, lw, 200), P(C('#8e1b1b', 0.85)))
    draw_text(cv, 'लोदी की सेना', 960, ly + 100, 46, 'title', '#ffffff')
    # tulughma flanks sweeping around
    fk = W_(0.45, 0.95, p)
    for side in (-1, 1):
        start = (960 + side * 420, 760)
        mid = (960 + side * 760, 420)
        end = (960 + side * 300, ly - 60)
        pth = smooth_path([start, mid, end])
        meas = skia.PathMeasure(pth, False)
        L_ = meas.getLength()
        seg = skia.Path()
        meas.getSegment(0, L_ * fk, seg, True)
        cv.drawPath(seg, P('#1f5f8b', stroke=18))
        pos = meas.getPosTan(L_ * fk)
        if pos and fk > 0.02:
            (px, py), (tx, ty) = pos
            ang = math.atan2(ty, tx)
            cv.drawPath(poly([(px + 40 * math.cos(ang), py + 40 * math.sin(ang)),
                              (px + 26 * math.cos(ang + 2.4), py + 26 * math.sin(ang + 2.4)),
                              (px + 26 * math.cos(ang - 2.4), py + 26 * math.sin(ang - 2.4))]), P('#1f5f8b'))
    if fk > 0.5:
        draw_text(cv, 'तुलुग़मा', 960, 110, 80, 'title', '#b71c1c', stroke=3, alpha=W_(0.5, 0.65, fk))

def a_battle(cv, c):
    t, p, bt = c['t'], c['bp'], c['bt']
    adv = W_(0.0, 0.6, p)
    army(cv, 1100 - 300 * adv, 2300 - 300 * adv, 1010, 5, t, 'lodi', facing=-1, s=0.72, march=1.0, weapon='sword', seed=5)
    wagon_wall(cv, -100, 760, 1010, t, s=0.7, link=1.0, gunners=True, fire_t=bt)
    if p > 0.35:
        k = W_(0.35, 0.8, p)
        cavalry(cv, 2300 - 900 * k, 2700 - 900 * k, 900, 1, t, 'mughal', facing=-1, s=0.75)
        cavalry(cv, -600 + 1000 * k, -200 + 1000 * k, 860, 1, t, 'mughal', facing=1, s=0.7)
        for i in range(16):
            u = (t * 1.3 + i / 16) % 1
            x0 = 300 + i * 30
            cv.drawLine(x0 + 900 * u, 500 - 300 * math.sin(math.pi * u), x0 + 900 * u + 30, 500 - 300 * math.sin(math.pi * u) + 6,
                        P('#3e2723', stroke=3))
    if p > 0.75:
        for i in range(3):
            draw_cannon(cv, 200 + i * 200, 1010, t, s=0.8, fire=((bt - i * 0.4) % 1.8))
    Particles('dust', 90, 6).draw(cv, t * 4, 1.0)

def a_elephants(cv, c):
    t, p = c['t'], c['bp']
    for i, ex in enumerate((600, 1100, 1550)):
        cv.save()
        cv.translate(ex, 900)
        cv.rotate(-14 * math.sin(t * 5 + i) * W_(0.1, 0.3, p))
        draw_elephant(cv, 0, 0, t, scale=0.7, facing=-1 if i % 2 else 1, push=math.sin(t * 6))
        cv.restore()
    army(cv, 100, 1900, 1020, 2, t, 'lodi', facing=-1, s=0.7, march=1.5, fall=W_(0.5, 0.9, p), seed=7)
    for i in range(6):
        sx = 200 + i * 300
        cv.drawCircle(sx + 30 * math.sin(t + i), 500 - (t * 30 + i * 50) % 200, 120, P(C('#bdbdbd', 0.25)))

def a_lodi_falls(cv, c):
    t, p = c['t'], c['bp']
    k = W_(0.25, 0.55, p)
    cv.save(); cv.translate(960, 1000); cv.rotate(-70 * k)
    draw_person(cv, 'lodi', 0, 0, t, scale=1.1, emotion='sad', seed=4)
    cv.restore()
    cv.save(); cv.translate(1300, 1000); cv.rotate(60 * W_(0.4, 0.8, p))
    draw_flag(cv, 0, 0, 360, t, col='#2e7d32', col2='#f2c232', emblem='moon')
    cv.restore()
    army(cv, 200, 700, 1020, 1, t, 'lodi', s=0.7, march=0, fall=1.0, seed=8)
    army(cv, 1500, 1900, 1020, 1, t, 'lodi', s=0.7, march=0, fall=1.0, seed=9)
    Particles('embers', 50, 2).draw(cv, t, 0.6)

def a_victory(cv, c):
    t, p = c['t'], c['bp']
    draw_flag(cv, 1380, 980, 520, t, col='#1f5f8b', col2='#f2c232', s=1.0)
    draw_person(cv, 'babur', 900, 1000, t, scale=1.2, gesture=0.95, emotion='calm')
    cv.drawLine(1010, 330, 1080, 120, P('#cfd8dc', stroke=10))
    rays(cv, 960, -100, t, a=0.18)
    army(cv, -100, 600, 1030, 2, t, 'mughal', s=0.7, march=0.0)

def a_timeline(cv, c):
    t, p = c['t'], c['bp']
    cv.drawLine(200, 560, 1720, 560, P('#5d4037', stroke=8))
    items = [(400, '1526', 'पानीपत'), (960, '1527', 'खानवा'), (1520, '1529', 'घाघरा')]
    for i, (x, y_, nm) in enumerate(items):
        a = W_(0.05 + i * 0.22, 0.2 + i * 0.22, p)
        if a <= 0:
            continue
        cv.drawCircle(x, 560, 30 * a, P('#b71c1c'))
        cv.drawCircle(x, 560, 30 * a, P(INK, stroke=3))
        draw_text(cv, y_, x, 450, 80, 'title', '#3e2723', alpha=a)
        draw_text(cv, nm, x, 660, 60, 'title', '#b71c1c', alpha=a)
    if p > 0.75:
        draw_text(cv, '300 साल का शासन', 960, 860, 90, 'title', '#1f5f8b', stroke=3, alpha=W_(0.75, 0.9, p))

def a_build(cv, c):
    t, p = c['t'], c['bp']
    draw_map(cv, t, empire=W_(0.0, 0.6, p) * 0.75, highlight=['दिल्ली', 'आगरा'])
    draw_crown2(cv, 1075, lerp(380, 540, W_(0.2, 0.6, p)), 0.5, a=0.9)

def a_admin(cv, c):
    t, p = c['t'], c['bp']
    draw_throne(cv, 960, 900, 0.7, t=t)
    draw_person(cv, 'babur', 960, 900, t, scale=0.8, gesture=0.4)
    steps = [(0.0, 'queen', 'शाही रिश्ते'), (0.25, 'farmer', 'उचित कर'), (0.5, 'gunner', 'कला-साहित्य'), (0.75, 'noble', 'सूबेदार')]
    for i, (st, nm, lbl) in enumerate(steps):
        a = W_(st, st + 0.08, p)
        if a <= 0:
            continue
        x = [300, 600, 1320, 1620][i]
        cv.saveLayerAlpha(None, int(255 * a))
        draw_person(cv, nm, x, 1000, t, scale=0.75, facing=1 if x < 960 else -1, gesture=0.4, seed=i)
        cv.restore()
        draw_text(cv, lbl, x, 560, 46, 'title', '#ffd54f', stroke=4, alpha=a)

def a_humayun(cv, c):
    t, p = c['t'], c['bp']
    if p < 0.25:
        draw_person(cv, 'babur', 960, 1000, t, scale=1.0, emotion='sad')
        cv.drawRect(skia.Rect.MakeLTRB(-1400, -1400, 3400, 2600), P(C('#000000', 0.5 * W_(0.1, 0.25, p))))
    elif p < 0.65:
        k = W_(0.3, 0.6, p)
        draw_person(cv, 'humayun', lerp(900, 300, k), 1000, t, scale=1.0, facing=-1, emotion='sad')
        draw_person(cv, 'shersha', 1300, 1000, t, scale=1.1, facing=-1, gesture=0.8, emotion='angry')
        draw_throne(cv, 1600, 980, 0.6, t=t)
    else:
        rider(cv, 'humayun', lerp(-200, 900, W_(0.65, 0.85, p)), 1000, t, scale=1.0, gallop=0.8, gesture=0.8)
        draw_throne(cv, 1400, 980, 0.7, t=t)

def a_akbar(cv, c):
    t, p = c['t'], c['bp']
    draw_throne(cv, 960, 930, 0.95, peacock=False, t=t)
    draw_person(cv, 'akbar', 960, 930, t, scale=1.0, gesture=0.5)
    for i, x in enumerate((360, 560, 1360, 1560)):
        draw_person(cv, 'noble', x, 1000, t, scale=0.75, facing=1 if x < 960 else -1, gesture=0.2, seed=i)
    Particles('sparkle', 40, 5).draw(cv, t)

def a_aurangzeb(cv, c):
    t, p = c['t'], c['bp']
    draw_map(cv, t, empire=1.0, empire_col='#2e7d32', highlight=['दिल्ली'])
    if p > 0.3:
        a = W_(0.3, 0.5, p)
        cv.saveLayerAlpha(None, int(255 * a))
        draw_person(cv, 'aurangzeb', 1600, 1000, t, scale=0.9, facing=-1, emotion='angry')
        cv.restore()

def a_crack(cv, c):
    t, p = c['t'], c['bp']
    draw_map(cv, t, empire=1.0, empire_col='#2e7d32', crack=W_(0.0, 0.6, p))
    if p > 0.5:
        a = W_(0.5, 0.65, p)
        cv.saveLayerAlpha(None, int(255 * a))
        draw_person(cv, 'maratha', 400, 1010, t, scale=0.95, gesture=0.9, emotion='angry')
        draw_flag(cv, 560, 1010, 380, t, col='#ef6c00', col2='#ffffff', emblem='sun', s=0.9)
        cv.restore()

def a_puppet(cv, c):
    t, p = c['t'], c['bp']
    draw_throne(cv, 960, 980, 1.5, t=t)
    draw_person(cv, 'zafar', 960, 840, t, scale=0.55, emotion='sad')

def a_nadir(cv, c):
    t, p = c['t'], c['bp']
    if p < 0.62:
        draw_flames(cv, -200, 2100, 700, t, height=160, n=18, alpha=W_(0.2, 0.5, p))
        cavalry(cv, 2200 - 1400 * W_(0.0, 0.5, p), 3000 - 1400 * W_(0.0, 0.5, p), 1010, 2, t, 'persian', facing=-1, s=0.85)
        rider(cv, 'nadir', 1500 - 700 * W_(0.0, 0.5, p), 1000, t, scale=1.1, facing=-1, gallop=0.8, gesture=0.8)
        Particles('embers', 80, 3).draw(cv, t)
    else:
        k = W_(0.62, 0.95, p)
        draw_person(cv, 'nadir', 700, 1000, t, scale=1.1, gesture=0.9, emotion='sly')
        draw_diamond(cv, 860, 420, 1.0, t)
        draw_throne(cv, 1400 + 600 * k, 990, 0.7, peacock=True, t=t)
        army(cv, 1100 + 600 * k, 1900 + 600 * k, 1020, 1, t, 'persian', facing=1, s=0.7)

def a_shrink(cv, c):
    t, p = c['t'], c['bp']
    draw_map(cv, t, empire=1.0, empire_col='#2e7d32', shrink=W_(0.05, 0.9, p), highlight=['दिल्ली'])

def a_1857(cv, c):
    t, p = c['t'], c['bp']
    draw_person(cv, 'zafar', 700, 1000, t, scale=1.0, emotion='sad')
    army(cv, 1000, 1900, 1020, 2, t, 'british', facing=-1, s=0.85, march=0.6, weapon='gun')
    draw_flag(cv, 1700, 1020, 420, t, col='#1a237e', col2='#ef5350', emblem='cross', s=0.9, facing=-1)
    if p > 0.6:
        cv.drawRect(skia.Rect.MakeLTRB(-1400, -1400, 3400, 2600), P(C('#000000', 0.6 * W_(0.6, 1.0, p))))

def a_whatif(cv, c):
    t, p = c['t'], c['bp']
    draw_person(cv, 'babur_boy', 700, 1000, t, scale=1.2, look_dx=1, emotion='calm')
    a = W_(0.3, 0.5, p)
    draw_text(cv, '?', 1350, 520, 360, 'title', '#ffd54f', stroke=8, alpha=a, scale=0.9 + 0.05 * math.sin(t * 2))

def a_outro(cv, c):
    t, p = c['t'], c['bp']
    cv.drawRect(skia.Rect.MakeLTRB(-1400, -1400, 3400, 2600), P(shader=rad(960, 540, 1100, ['#4a1a2a', '#0b0610'])))
    draw_crown2(cv, 960, 420, 0.9, a=1)
    draw_text(cv, 'कथा और रहस्य', 960, 620, 110, 'title', '#ffd54f', stroke=5)
    draw_text(cv, 'ऐसी ही कहानियों के लिए सब्सक्राइब करें', 960, 760, 54, 'body', '#ffffff')

# ------------------------------------------------------------------ beat table
BEATS = [
 # (start, act, bg, cam(start,end), grade, fx, cards)
 (TA(0.0), a_title, lambda: bg_palace_night(), ((960, 560, 1.15), (960, 540, 1.0)), '#ffb74d', 'sparkle',
  [('pop', 'मुग़ल साम्राज्य', 0.8, 8.5, 0.16), ('sub', 'उदय • पानीपत • पतन', 1.4, 8.0, 0.29)]),
 (TA(11.2), a_book, None, ((960, 540, 1.0), (960, 520, 1.12)), '#ffb74d', 'dust', []),
 (TA(21.6), a_coup, lambda: bg_palace_night(), ((960, 600, 1.05), (960, 560, 1.18)), '#7986cb', 'dust',
  [('date', '16वीं सदी • हिंदुस्तान', 1.0, 6.0)]),
 (TA(43.1), a_throne_guard, lambda: bg_court(), ((960, 560, 1.2), (960, 540, 1.3)), '#ff8a65', 'dust', []),
 (TA(47.1), a_fergana_boy, lambda: bg_land('fergana'), ((900, 600, 1.15), (900, 560, 1.35)), '#ffcc80', 'leaves',
  [('name', 'ज़हीरुद्दीन मुहम्मद बाबर', 'फ़रग़ना का राजकुमार', 1.0), ('date', 'फ़रग़ना • मध्य एशिया', 0.5, 5.0)]),
 (TA(67.6), a_coronation, lambda: bg_court(), ((960, 560, 1.15), (960, 600, 1.0)), '#ffb74d', 'sparkle',
  [('date', '1494 • उम्र सिर्फ़ 12 साल', 0.8, 7.0)]),
 (TA(86.5), a_lineage, None, ((960, 560, 1.0), (960, 540, 1.08)), '#ce93d8', 'sparkle',
  [('pop', 'तैमूर', 2.5, 15.0, 0.12, 0.27), ('pop', 'चंगेज़ ख़ान', 7.0, 11.0, 0.12, 0.73)]),
 (TA(105.5), a_exile, lambda: bg_land('dusk'), ((1000, 600, 1.1), (900, 580, 1.2)), '#90a4ae', 'rain', []),
 (TA(121.9), a_hindukush, lambda: bg_land('snow'), ((900, 600, 1.0), (1300, 560, 1.08)), '#b3e5fc', 'dust',
  [('date', '1504 • हिंदूकुश पार', 1.0, 6.0)]),
 (TA(130.6), a_kabul, lambda: bg_land('kabul'), ((1000, 560, 1.0), (1100, 540, 1.1)), '#ffcc80', 'dust',
  [('date', 'काबुल पर क़ब्ज़ा', 0.5, 5.0)]),
 (TA(136.5), a_treasury, lambda: bg_land('kabul'), ((960, 620, 1.2), (960, 600, 1.05)), '#bcaaa4', 'dust',
  [('pop', 'ख़ज़ाना ख़ाली!', 4.0, 5.0, 0.15)]),
 (TA(147.3), a_map_south, lambda: parchment_bg(), ((900, 520, 1.0), (1000, 560, 1.25)), '#ffe0b2', None, []),
 (TA(160.1), a_pawn, None, ((960, 600, 1.0), (980, 620, 1.12)), '#ffb74d', 'dust',
  [('name', 'दौलत ख़ान लोदी', 'पंजाब का गवर्नर', 1.5)]),
 (TA(174.8), a_not_merc, lambda: bg_land('battle'), ((960, 560, 1.25), (960, 520, 1.4)), '#ff8a65', 'dust',
  [('pop', 'डेविड बनाम गोलियथ', 6.5, 4.0, 0.14)]),
 (TA(184.98), a_vs, lambda: bg_land('battle'), ((960, 560, 1.0), (960, 560, 1.05)), '#ffab91', 'dust', []),
 # ---------------- Panipat
 (TB(97.6), a_indus, lambda: bg_land('river'), ((800, 600, 1.0), (1300, 560, 1.08)), '#ffe0b2', 'dust',
  [('chapter', 'दूसरा अध्याय', 'पानीपत का युद्ध'), ('date', 'अप्रैल 1526 • पानीपत', 2.5, 5.0)]),
 (TB(104.8), a_tent, None, ((960, 680, 1.15), (960, 640, 1.35)), '#ffb74d', None, []),
 (TB(112.9), a_gunners, lambda: bg_land('battle'), ((900, 600, 1.0), (1000, 600, 1.15)), '#ffcc80', 'dust',
  [('name', 'उस्ताद अली और मुस्तफ़ा', 'उस्मानी (ऑटोमन) तोपची', 7.5)]),
 (TB(133.5), a_cannons, lambda: bg_land('battle'), ((960, 620, 1.05), (900, 620, 1.12)), '#ff8a65', 'dust',
  [('pop', '15–20 तोपें + मैचलॉक बंदूकें', 0.5, 7.0, 0.14)]),
 (TB(145.5), a_swords, lambda: bg_land('battle'), ((960, 600, 1.0), (960, 600, 1.06)), '#ffab91', 'dust', []),
 (TB(161.6), a_wagons, lambda: bg_land('battle'), ((960, 860, 1.3), (960, 800, 1.12)), '#ffcc80', 'dust',
  [('pop', '700 गाड़ियाँ', 3.0, 7.0, 0.15), ('sub', 'चमड़े की रस्सियों से बँधी दीवार', 4.0, 6.5, 0.27)]),
 (TB(201.4), a_tulughma, lambda: parchment_bg(), ((960, 520, 1.0), (960, 520, 1.03)), '#ffe0b2', None,
  [('chapter', 'तीसरा अध्याय', 'तुलुग़मा रणनीति')]),
 (TB(218.6), a_battle, lambda: bg_land('battle'), ((900, 780, 1.12), (1000, 760, 1.2)), '#ff7043', 'dust', []),
 (TB(234.5), a_elephants, lambda: bg_land('battle'), ((960, 620, 1.05), (960, 600, 1.15)), '#ff7043', 'dust',
  [('pop', '1,000 जंगी हाथी बेक़ाबू', 4.0, 6.0, 0.14)]),
 (TB(251.6), a_lodi_falls, lambda: bg_land('battle'), ((960, 640, 1.2), (960, 600, 1.0)), '#e57373', 'embers',
  [('pop', 'इब्राहिम लोदी मारा गया', 3.5, 6.0, 0.14), ('sub', 'लगभग 20,000 सैनिक भी', 4.2, 5.5, 0.26)]),
 (TB(263.1), a_victory, lambda: bg_land('battle'), ((960, 600, 1.1), (960, 560, 1.0)), '#ffd54f', 'sparkle', []),
 (TB(274.6), a_timeline, lambda: parchment_bg(), ((960, 560, 1.0), (960, 560, 1.04)), '#ffe0b2', None, []),
 # ---------------- Mughal part 2
 (TC(274.0), a_build, lambda: parchment_bg(), ((1000, 560, 1.0), (1050, 600, 1.15)), '#ffe0b2', None,
  [('chapter', 'चौथा अध्याय', 'साम्राज्य का निर्माण')]),
 (TC(292.7), a_admin, lambda: bg_court(), ((960, 600, 1.0), (960, 580, 1.05)), '#ffb74d', 'sparkle', []),
 (TC(319.1), a_humayun, lambda: bg_land('dusk'), ((960, 600, 1.05), (960, 580, 1.1)), '#ffab91', 'dust',
  [('date', '1530 • बाबर की मौत', 1.0, 4.0), ('name', 'शेरशाह सूरी', 'अफ़ग़ान शासक', 6.0),
   ('date', '1555 • हुमायूँ की वापसी', 13.5, 4.0)]),
 (TC(336.3), a_akbar, lambda: bg_court(), ((960, 560, 1.0), (960, 540, 1.1)), '#ffd54f', 'sparkle',
  [('name', 'अकबर', 'मुग़ल साम्राज्य का स्वर्ण युग', 0.6)]),
 (TC(341.9), a_aurangzeb, lambda: parchment_bg(), ((1000, 560, 1.0), (1050, 600, 1.1)), '#ffe0b2', None,
  [('chapter', 'पाँचवाँ अध्याय', 'दुखद पतन'), ('name', 'औरंगज़ेब', 'साम्राज्य का चरम विस्तार', 8.0)]),
 (TC(358.2), a_crack, lambda: parchment_bg(), ((1050, 600, 1.1), (1000, 560, 1.0)), '#e0c09a', None,
  [('pop', 'मराठा शक्ति का उदय', 11.0, 6.0, 0.13)]),
 (TC(376.1), a_puppet, lambda: bg_court(), ((960, 600, 1.0), (960, 640, 1.2)), '#9e9e9e', 'dust', []),
 (TC(380.2), a_nadir, lambda: bg_land('fire'), ((1000, 600, 1.0), (960, 600, 1.08)), '#ff5722', 'embers',
  [('date', '1739 • नादिर शाह का हमला', 7.5, 6.0), ('pop', 'कोहिनूर + मयूर सिंहासन लूटे गए', 15.0, 6.0, 0.13)]),
 (TC(401.6), a_shrink, lambda: parchment_bg(), ((1050, 620, 1.05), (1075, 650, 1.35)), '#d7ccc8', None, []),
 (TC(418.8), a_1857, lambda: bg_palace_night(), ((960, 600, 1.0), (900, 600, 1.1)), '#78909c', 'dust',
  [('date', '1857 • अंतिम अंत', 2.0, 6.0), ('name', 'बहादुर शाह ज़फ़र', 'अंतिम मुग़ल बादशाह', 4.0)]),
 (TC(432.0), a_whatif, lambda: bg_land('snow'), ((900, 600, 1.15), (1000, 560, 1.0)), '#b3e5fc', 'dust', []),
 (TC(458.1), a_outro, None, ((960, 540, 1.0), (960, 540, 1.05)), '#ffd54f', 'sparkle', []),
]
