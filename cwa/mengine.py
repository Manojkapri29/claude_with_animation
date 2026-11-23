"""Mughal-era characters, props, crowds, maps and backgrounds on top of engine.py."""
import math, random
import skia
from engine import *

# ------------------------------------------------------------------ characters
LOOKS.update({
    'babur_boy': Look(robe=True, tilak=False, kind='youth', skin='#e8b48c', cloth='#2e6da4', cloth2='#f2c232', hair='#2b1d16', hat='turban',
                      hat_col='#f5f0e1', s=0.8, brow='calm'),
    'babur': Look(robe=True, tilak=False, kind='man', skin='#e2ad84', cloth='#1f5f8b', cloth2='#f2c232', hair='#2b1d16', hat='turban',
                  hat_col='#fafafa', plume=True, beard='#3e2723', mous='#3e2723', s=1.05, brow='calm'),
    'lodi': Look(robe=True, tilak=False, kind='man', skin='#c98f63', cloth='#8e1b1b', cloth2='#f2c232', hair='#1d1410', hat='turban',
                 hat_col='#2e7d32', plume=True, beard='#1d1410', mous='#1d1410', s=1.1, brow='angry'),
    'daulat': Look(robe=True, tilak=False, kind='man', skin='#cf9a70', cloth='#5d4037', cloth2='#c9a227', hair='#1d1410', hat='turban',
                   hat_col='#fff3e0', beard='#4e342e', mous='#4e342e', brow='sly'),
    'gunner': Look(robe=True, tilak=False, kind='man', skin='#e0ac82', cloth='#283593', cloth2='#b71c1c', hair='#1d1410', hat='fez',
                   mous='#2b1d16', brow='calm'),
    'timur': Look(robe=True, tilak=False, kind='man', skin='#d9a47a', cloth='#4a148c', cloth2='#f2c232', hair='#1d1410', hat='turban',
                  hat_col='#212121', beard='#212121', mous='#212121', s=1.05, brow='angry'),
    'genghis': Look(robe=True, tilak=False, kind='man', skin='#e3b07f', cloth='#6d4c41', cloth2='#bf360c', hair='#1d1410', hat='helmet',
                    beard='#3e2723', mous='#3e2723', s=1.05, brow='angry'),
    'humayun': Look(robe=True, tilak=False, kind='man', skin='#e2ad84', cloth='#00695c', cloth2='#f2c232', hair='#1d1410', hat='turban',
                    hat_col='#fff8e1', beard='#3e2723', mous='#3e2723', brow='sad'),
    'shersha': Look(robe=True, tilak=False, kind='man', skin='#c98f63', cloth='#33691e', cloth2='#f2c232', hair='#1d1410', hat='turban',
                    hat_col='#5d4037', beard='#1d1410', mous='#1d1410', brow='angry'),
    'akbar': Look(robe=True, tilak=False, kind='man', skin='#d9a47a', cloth='#f2c232', cloth2='#b71c1c', hair='#1d1410', hat='turban',
                  hat_col='#fafafa', plume=True, mous='#1d1410', s=1.1, halo='#fff2b0'),
    'aurangzeb': Look(robe=True, tilak=False, kind='man', skin='#d9a47a', cloth='#eceff1', cloth2='#2e7d32', hair='#f5f5f5', hat='turban',
                      hat_col='#ffffff', beard='#f5f5f5', mous='#f5f5f5', s=1.05, brow='angry'),
    'zafar': Look(robe=True, tilak=False, kind='man', skin='#d9a47a', cloth='#9e9e9e', cloth2='#5d4037', hair='#f5f5f5', hat='turban',
                  hat_col='#bdbdbd', beard='#f5f5f5', mous='#f5f5f5', s=0.95, brow='sad'),
    'nadir': Look(robe=True, tilak=False, kind='man', skin='#d6a27a', cloth='#b71c1c', cloth2='#212121', hair='#1d1410', hat='persian',
                  beard='#1d1410', mous='#1d1410', s=1.12, brow='angry'),
    'maratha': Look(robe=True, kind='man', skin='#b9825a', cloth='#fff3e0', cloth2='#ef6c00', hair='#1d1410', hat='saffron',
                    mous='#1d1410', s=1.05, brow='angry'),
    'british': Look(robe=True, tilak=False, kind='man', skin='#f1c9a5', cloth='#c62828', cloth2='#fafafa', hair='#8d6e63', hat='redcoat',
                    mous='#8d6e63', brow='calm'),
    'noble': Look(robe=True, tilak=False, kind='man', skin='#d9a47a', cloth='#6a1b9a', cloth2='#f2c232', hair='#1d1410', hat='turban',
                  hat_col='#f8bbd0', mous='#1d1410', brow='sly'),
    'farmer': Look(robe=True, kind='man', skin='#b9825a', cloth='#fff8e1', cloth2='#8d6e63', hair='#1d1410', hat='turban',
                   hat_col='#ffcc80', mous='#1d1410', s=0.95),
    'queen': Look(kind='woman', skin='#e8b48c', cloth='#ad1457', cloth2='#f2c232', hair='#1d1410', dupatta='#f2c232'),
    'uzbek': Look(robe=True, tilak=False, kind='man', skin='#d9a47a', cloth='#455a64', cloth2='#bf360c', hair='#1d1410', hat='helmet',
                  beard='#1d1410', s=1.0, brow='angry'),
})

def rider(cv, name, x, y, t, scale=1.0, facing=1, gallop=1.0, gesture=0.3, horse_col='#8d5a3b', mouth=0.0, seed=0):
    """Person riding a horse. (x,y) = ground under horse."""
    draw_horse2(cv, x, y, t, scale=scale, facing=facing, gallop=gallop, col=horse_col, seed=seed)
    bob = 8 * math.sin(t * 8 + seed) * gallop * scale
    draw_person(cv, name, x - 10 * facing * scale, y - 8 * scale + bob, t, scale=0.62 * scale, facing=facing,
                gesture=gesture, no_lower=True, mouth=mouth, seed=seed)

def draw_horse2(cv, x, y, t, scale=1.0, facing=1, gallop=1.0, col='#8d5a3b', seed=0):
    cv.save()
    cv.translate(x, y)
    cv.scale(scale * facing, scale)
    sp = 9
    bob = 6 * math.sin(t * sp + seed) * gallop
    cv.translate(0, bob)
    dark = mix(col, '#000000', 0.35)
    for i, lx in enumerate((-80, -55, 55, 80)):
        a = math.sin(t * sp + i * 1.7 + seed) * 28 * gallop
        cv.save()
        cv.translate(lx, -60)
        cv.rotate(a)
        cv.drawLine(0, 0, 0, 60, P(INK, stroke=16))
        cv.drawLine(0, 0, 0, 60, P(col if i % 2 else dark, stroke=11))
        cv.restore()
    body = smooth_path([(-110, -100), (-80, -128), (50, -130), (95, -110), (100, -70), (30, -55), (-90, -58)], closed=True)
    fill_outline(cv, body, P(shader=lin(0, -130, 0, -55, [mix(col, '#ffffff', 0.2), col, dark])), 3)
    neck = smooth_path([(60, -120), (100, -185), (130, -195), (135, -165), (100, -95)], closed=True)
    fill_outline(cv, neck, P(col), 3)
    head = smooth_path([(120, -205), (172, -185), (180, -165), (160, -158), (125, -165)], closed=True)
    fill_outline(cv, head, P(col), 3)
    cv.drawCircle(145, -186, 3.5, P(INK))
    for k in range(5):
        cv.drawLine(95 + k * 8, -190 + k * 18, 80 + k * 6, -178 + k * 18 + 6 * math.sin(t * 6 + k), P('#2b1d16', stroke=7))
    for k in range(3):
        cv.drawPath(smooth_path([(-108, -110), (-150, -100 + k * 6), (-165 + 8 * math.sin(t * 7 + k), -60 + k * 8)]),
                    P('#2b1d16', stroke=8))
    # saddle cloth
    cv.drawPath(smooth_path([(-40, -128), (30, -128), (25, -85), (-35, -85)], closed=True), P('#b71c1c'))
    cv.drawPath(smooth_path([(-40, -128), (30, -128), (25, -85), (-35, -85)], closed=True), P('#f2c232', stroke=3))
    cv.restore()

# ------------------------------------------------------------------ crowd soldiers (cheap)
SOLD = {
    'mughal': ('#1f5f8b', '#9e9e9e', 'helmet'),
    'lodi': ('#8e1b1b', '#2e7d32', 'turban'),
    'uzbek': ('#455a64', '#9e9e9e', 'helmet'),
    'maratha': ('#fff3e0', '#ef6c00', 'turban'),
    'british': ('#c62828', '#212121', 'hat'),
    'persian': ('#b71c1c', '#212121', 'tall'),
}

def mini(cv, x, y, t, s=1.0, kind='mughal', facing=1, phase=0.0, march=1.0, weapon='spear', fall=0.0):
    body, head, hat = SOLD[kind]
    cv.save()
    cv.translate(x, y)
    if fall:
        cv.rotate(-80 * fall * facing)
    cv.scale(s * facing, s)
    st = math.sin(t * 7 + phase) * march
    cv.drawLine(-6, -30, -6 - 8 * st, 0, P(INK, stroke=6))
    cv.drawLine(6, -30, 6 + 8 * st, 0, P(INK, stroke=6))
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-14, -72, 14, -26), 8, 8), P(body))
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-14, -72, 14, -26), 8, 8), P(INK, stroke=2.5))
    cv.drawCircle(0, -84, 12, P('#d9a47a'))
    cv.drawCircle(0, -84, 12, P(INK, stroke=2.5))
    if hat == 'helmet':
        cv.drawPath(poly([(-13, -86), (0, -108), (13, -86)]), P(head))
    elif hat == 'turban':
        cv.drawOval(skia.Rect.MakeLTRB(-14, -102, 14, -86), P(head))
    elif hat == 'tall':
        cv.drawRect(skia.Rect.MakeLTRB(-10, -112, 10, -90), P(head))
    else:
        cv.drawRect(skia.Rect.MakeLTRB(-16, -98, 16, -92), P(head))
    if weapon == 'spear':
        cv.drawLine(16, -110, 16, 0, P('#6d4c41', stroke=3))
        cv.drawPath(poly([(12, -110), (16, -124), (20, -110)]), P('#cfd8dc'))
    elif weapon == 'gun':
        cv.drawLine(4, -54, 40, -64, P('#3e2723', stroke=5))
    elif weapon == 'bow':
        cv.drawArc(skia.Rect.MakeLTRB(10, -80, 30, -30), -80, 160, False, P('#6d4c41', stroke=3))
    elif weapon == 'sword':
        cv.drawLine(14, -50, 34, -90, P('#cfd8dc', stroke=4))
    cv.restore()

def army(cv, x0, x1, y, rows, t, kind='mughal', facing=1, s=0.8, march=1.0, speed=0.0, seed=0, weapon='spear',
         fall=0.0, density=1.0):
    rnd = random.Random(seed)
    n = int((x1 - x0) / (34 * s) * density)
    for r in range(rows):
        yy = y - r * 26 * s
        ss = s * (1 - r * 0.06)
        for i in range(n):
            xx = x0 + (x1 - x0) * (i + 0.5 * (r % 2)) / n + rnd.uniform(-6, 6) + speed * t * facing
            f = fall if rnd.random() < 0.6 else 0
            mini(cv, xx, yy, t, ss, kind, facing, phase=rnd.uniform(0, 6.28), march=march, weapon=weapon, fall=f)

def mini_rider(cv, x, y, t, s=1.0, kind='mughal', facing=1, phase=0.0, gallop=1.0, weapon='sword'):
    cv.save()
    cv.translate(x, y)
    cv.scale(s * facing, s)
    b = 5 * math.sin(t * 10 + phase) * gallop
    for i, lx in enumerate((-30, -20, 22, 32)):
        a = math.sin(t * 10 + i * 1.7 + phase) * 30 * gallop
        cv.save(); cv.translate(lx, -30 + b); cv.rotate(a)
        cv.drawLine(0, 0, 0, 30, P('#3e2723', stroke=6)); cv.restore()
    cv.drawOval(skia.Rect.MakeLTRB(-44, -62 + b, 44, -28 + b), P('#6d4c41'))
    cv.drawPath(smooth_path([(30, -55 + b), (54, -84 + b), (66, -76 + b), (46, -46 + b)], closed=True), P('#6d4c41'))
    cv.restore()
    mini(cv, x - 4 * facing * s, y - 40 * s + b * s, t, s * 0.85, kind, facing, phase, march=0, weapon=weapon)

def cavalry(cv, x0, x1, y, rows, t, kind='mughal', facing=1, s=0.9, speed=0.0, seed=0):
    rnd = random.Random(seed)
    n = max(1, int((x1 - x0) / (90 * s)))
    for r in range(rows):
        for i in range(n):
            xx = x0 + (x1 - x0) * (i + 0.5 * (r % 2)) / n + speed * t * facing + rnd.uniform(-10, 10)
            mini_rider(cv, xx, y - r * 30 * s, t, s * (1 - r * 0.07), kind, facing, rnd.uniform(0, 6.28))

# ------------------------------------------------------------------ props
def draw_cannon(cv, x, y, t, s=1.0, facing=1, fire=-1.0, col='#5d4037'):
    """fire: seconds since last shot (<0 = none)."""
    cv.save()
    cv.translate(x, y)
    cv.scale(s * facing, s)
    recoil = -14 * max(0, 1 - fire / 0.25) if 0 <= fire < 0.25 else 0
    cv.save()
    cv.translate(recoil, 0)
    cv.save(); cv.translate(-10, -58); cv.rotate(-12)
    barrel = poly([(-70, -16), (90, -11), (90, 11), (-70, 16)])
    fill_outline(cv, barrel, P(shader=lin(0, -16, 0, 16, ['#8d8d8d', '#3e3e3e', '#1c1c1c'])), 3)
    for bx in (-40, 20, 80):
        cv.drawLine(bx, -15, bx, 15, P('#b8860b', stroke=5))
    cv.restore()
    cv.restore()
    for wx in (-30, 30):
        cv.drawCircle(wx, -26, 26, P(col))
        cv.drawCircle(wx, -26, 26, P(INK, stroke=3))
        for k in range(6):
            a = math.radians(60 * k)
            cv.drawLine(wx, -26, wx + 24 * math.cos(a), -26 + 24 * math.sin(a), P(INK, stroke=2))
    cv.restore()
    if 0 <= fire < 1.6:
        mx, my = x + facing * 82 * s, y - 78 * s
        if fire < 0.18:
            glow(cv, mx, my, 120 * s, '#ffe082', 0.95)
            cv.drawPath(poly([(mx, my - 20 * s), (mx + facing * 110 * s, my), (mx, my + 20 * s)]),
                        P(C('#ffca28', 0.9), blend=skia.BlendMode.kScreen))
        rr = 30 + 120 * min(1, fire / 1.2)
        for k in range(5):
            sx = mx + facing * (20 + k * 30) * s * (0.4 + fire)
            sy = my - k * 8 * s - fire * 40 * s
            cv.drawCircle(sx, sy, rr * s * (0.6 + 0.1 * k),
                          P(shader=rad(sx, sy, rr * s, [C('#eeeeee', 0.55 * (1 - fire / 1.6)), C('#9e9e9e', 0)])))

def draw_wagon(cv, x, y, s=1.0, col='#8d6e43'):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    box = poly([(-70, -95), (70, -95), (64, -40), (-64, -40)])
    fill_outline(cv, box, P(shader=lin(0, -95, 0, -40, [mix(col, '#ffffff', 0.15), col, mix(col, '#000000', 0.3)])), 3)
    for k in range(-50, 70, 30):
        cv.drawLine(k, -92, k, -42, P(C('#3e2723', 0.5), stroke=2))
    for wx in (-40, 40):
        cv.drawCircle(wx, -26, 24, P('#5d4037'))
        cv.drawCircle(wx, -26, 24, P(INK, stroke=3))
        cv.drawCircle(wx, -26, 6, P('#3e2723'))
    cv.restore()

def wagon_wall(cv, x0, x1, y, t, s=0.8, link=1.0, gunners=True, fire_t=-1.0):
    n = int((x1 - x0) / (150 * s))
    pts = []
    for i in range(n):
        wx = x0 + (x1 - x0) * (i + 0.5) / n
        draw_wagon(cv, wx, y, s)
        pts.append(wx)
    for i in range(len(pts) - 1):
        k = max(0, min(1, link * len(pts) - i))
        if k > 0:
            a, b = pts[i] + 60 * s, pts[i + 1] - 60 * s
            cv.drawPath(smooth_path([(a, y - 60 * s), ((a + b) / 2, y - 45 * s), (a + (b - a) * k, y - 60 * s)]),
                        P('#5d3a1a', stroke=6 * s))
        if gunners and i % 2 == 0 and i + 1 < len(pts):
            gx = (pts[i] + pts[i + 1]) / 2
            mini(cv, gx, y - 4, t, s * 0.9, 'mughal', 1, phase=i, march=0, weapon='gun')
            if fire_t >= 0:
                ft = (fire_t + i * 0.37) % 2.2
                if ft < 0.15:
                    glow(cv, gx + 36 * s, y - 60 * s, 40 * s, '#ffe082', 0.9)
                if ft < 1.2:
                    cv.drawCircle(gx + (40 + ft * 60) * s, y - (62 + ft * 20) * s, (10 + ft * 30) * s,
                                  P(C('#e0e0e0', 0.5 * (1 - ft / 1.2))))

def draw_flag(cv, x, y, h, t, col='#2e7d32', col2='#f2c232', emblem='sun', s=1.0, facing=1):
    cv.drawLine(x, y, x, y - h * s, P('#5d4037', stroke=6 * s))
    w = 120 * s
    pts = []
    for i in range(9):
        u = i / 8
        pts.append((x + facing * w * u, y - h * s + 10 * s * math.sin(t * 5 - u * 4) * u))
    for i in range(8, -1, -1):
        u = i / 8
        pts.append((x + facing * w * u, y - h * s + 70 * s + 10 * s * math.sin(t * 5 - u * 4) * u))
    fill_outline(cv, smooth_path(pts, closed=True), P(col), 3 * s)
    cx, cy = x + facing * w * 0.45, y - h * s + 36 * s + 5 * s * math.sin(t * 5 - 1.8) * 0.45
    if emblem == 'sun':
        cv.drawCircle(cx, cy, 16 * s, P(col2))
    elif emblem == 'moon':
        cv.drawCircle(cx, cy, 16 * s, P(col2))
        cv.drawCircle(cx + 6 * s, cy - 3 * s, 13 * s, P(col))
    elif emblem == 'cross':
        cv.drawRect(skia.Rect.MakeXYWH(cx - 3 * s, cy - 16 * s, 6 * s, 32 * s), P(col2))
        cv.drawRect(skia.Rect.MakeXYWH(cx - 16 * s, cy - 3 * s, 32 * s, 6 * s), P(col2))

def draw_throne(cv, x, y, s=1.0, peacock=False, t=0.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    if peacock:
        for i in range(13):
            a = math.radians(-160 + i * 140 / 12)
            ex, ey = 230 * math.cos(a), -260 + 230 * math.sin(a)
            cv.drawLine(0, -260, ex, ey, P('#1565c0', stroke=10))
            cv.drawCircle(ex, ey, 22, P('#00897b'))
            cv.drawCircle(ex, ey, 11, P('#1a237e'))
            cv.drawCircle(ex, ey, 5, P('#f2c232'))
    back = smooth_path([(-120, 0), (-120, -300), (-60, -380), (0, -400), (60, -380), (120, -300), (120, 0)], closed=True)
    fill_outline(cv, back, P(shader=lin(-120, -400, 120, 0, ['#fff59d', '#f2c232', '#a66c00'])), 4)
    cv.drawRect(skia.Rect.MakeLTRB(-150, -150, 150, -110), P('#b71c1c'))
    cv.drawRect(skia.Rect.MakeLTRB(-150, -150, 150, -110), P(INK, stroke=3))
    for gx in (-80, 0, 80):
        cv.drawCircle(gx, -300, 12, P('#e53935'))
    cv.restore()
    glow(cv, x, y - 250 * s, 260 * s, '#fff59d', 0.3)

def draw_diamond(cv, x, y, s=1.0, t=0.0):
    glow(cv, x, y, 160 * s, '#e1f5fe', 0.7)
    top = poly([(x - 60 * s, y - 20 * s), (x - 30 * s, y - 50 * s), (x + 30 * s, y - 50 * s), (x + 60 * s, y - 20 * s)])
    bot = poly([(x - 60 * s, y - 20 * s), (x + 60 * s, y - 20 * s), (x, y + 60 * s)])
    fill_outline(cv, top, P(shader=lin(x - 60 * s, y - 50 * s, x + 60 * s, y - 20 * s, ['#ffffff', '#b3e5fc'])), 3)
    fill_outline(cv, bot, P(shader=lin(x, y - 20 * s, x, y + 60 * s, ['#e1f5fe', '#4fc3f7'])), 3)
    for k in range(4):
        a = t * 2 + k * 1.57
        cv.drawCircle(x + 70 * s * math.cos(a), y - 10 * s + 40 * s * math.sin(a), 4 * s, P(C('#ffffff', 0.9)))

def draw_crown2(cv, x, y, s=1.0, a=1.0):
    glow(cv, x, y - 40 * s, 200 * s, '#ffd54f', 0.5 * a)
    cr = poly([(x - 90 * s, y), (x - 100 * s, y - 80 * s), (x - 50 * s, y - 40 * s), (x, y - 110 * s),
               (x + 50 * s, y - 40 * s), (x + 100 * s, y - 80 * s), (x + 90 * s, y)])
    fill_outline(cv, cr, P(shader=lin(x, y - 110 * s, x, y, ['#fff59d', '#f2c232', '#a66c00'])), 4)
    for gx, gc in ((-50, '#e53935'), (0, '#1e88e5'), (50, '#43a047')):
        cv.drawCircle(x + gx * s, y - 22 * s, 10 * s, P(gc))

def draw_tent(cv, x, y, s=1.0, col='#f5e6c8'):
    tp = poly([(x - 220 * s, y), (x, y - 260 * s), (x + 220 * s, y)])
    fill_outline(cv, tp, P(shader=lin(x - 220 * s, 0, x + 220 * s, 0, [mix(col, '#ffffff', 0.2), col, mix(col, '#000', 0.3)])), 4)
    cv.drawPath(poly([(x - 40 * s, y), (x, y - 120 * s), (x + 40 * s, y)]), P('#3e2723'))

def draw_chess(cv, x, y, s=1.0, t=0.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    for i in range(8):
        for j in range(5):
            c = '#f5e6c8' if (i + j) % 2 == 0 else '#5d4037'
            cv.drawPath(poly([(-400 + i * 100 - j * 40, -j * 60), (-300 + i * 100 - j * 40, -j * 60),
                              (-340 + i * 100 - (j + 1) * 40 + 40, -(j + 1) * 60),
                              (-440 + i * 100 - (j + 1) * 40 + 40, -(j + 1) * 60)]), P(c))
    cv.restore()

def draw_pawn(cv, x, y, s=1.0, col='#212121', glowk=0.0, label=None):
    if glowk:
        glow(cv, x, y - 80 * s, 160 * s, '#ffd54f', 0.6 * glowk)
    base = poly([(x - 50 * s, y), (x + 50 * s, y), (x + 34 * s, y - 30 * s), (x - 34 * s, y - 30 * s)])
    body = poly([(x - 30 * s, y - 30 * s), (x + 30 * s, y - 30 * s), (x + 14 * s, y - 100 * s), (x - 14 * s, y - 100 * s)])
    for pth in (base, body):
        fill_outline(cv, pth, P(shader=lin(x - 50 * s, 0, x + 50 * s, 0, [mix(col, '#ffffff', 0.35), col])), 3)
    cv.drawCircle(x, y - 125 * s, 30 * s, P(shader=rad(x - 10 * s, y - 135 * s, 40 * s, [mix(col, '#ffffff', 0.4), col])))
    cv.drawCircle(x, y - 125 * s, 30 * s, P(INK, stroke=3))

# ------------------------------------------------------------------ backgrounds
def L(p, fn):
    return (p, fn)

def bg_palace_night():
    def sky(cv, c):
        bg_sky(cv, '#05071a', '#141a44', '#2b2350')
        stars(cv, c['t'], n=180)
        cv.drawCircle(1500, 170, 55, P(shader=rad(1500, 170, 55, ['#ffffff', '#e8eaf6'])))
        glow(cv, 1500, 170, 240, '#c5cae9', 0.35)

    def palace(cv, c):
        col = '#0e0f24'
        cv.drawRect(skia.Rect.MakeLTRB(-1400, 560, 3400, 2600), P(col))
        for cx, w, h in [(400, 300, 260), (960, 520, 380), (1550, 300, 260)]:
            cv.drawRect(skia.Rect.MakeLTRB(cx - w / 2, 560 - h, cx + w / 2, 560), P(col))
            cv.drawPath(smooth_path([(cx - w * 0.32, 560 - h), (cx - w * 0.3, 560 - h - w * 0.35), (cx, 560 - h - w * 0.55),
                                     (cx + w * 0.3, 560 - h - w * 0.35), (cx + w * 0.32, 560 - h)], closed=True), P(col))
            cv.drawLine(cx, 560 - h - w * 0.55, cx, 560 - h - w * 0.68, P(col, stroke=6))
        for mx in (180, 700, 1220, 1760):
            cv.drawRect(skia.Rect.MakeLTRB(mx - 16, 230, mx + 16, 560), P(col))
            cv.drawCircle(mx, 225, 22, P(col))
        for wx in range(250, 1700, 140):
            k = 0.6 + 0.4 * math.sin(c['t'] * 3 + wx)
            cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(wx, 470, wx + 30, 530), 15, 15), P(C('#ffb74d', 0.6 * k)))

    def ground(cv, c):
        cv.drawRect(skia.Rect.MakeLTRB(-1400, 860, 3400, 2600), P(shader=lin(0, 860, 0, 1200, ['#2a2140', '#0b0918'])))
    return [(0.05, sky), (0.4, palace), (0.9, ground)]

def bg_court(warm=True):
    def wall(cv, c):
        cv.drawRect(skia.Rect.MakeLTRB(-1400, -1400, 3400, 2600), P(shader=lin(0, 0, 0, 900, ['#7a2e1f', '#a8432a'])))
        for i, ax in enumerate(range(-300, 2400, 300)):
            arch = smooth_path([(ax - 110, 860), (ax - 110, 380), (ax - 70, 300), (ax, 250), (ax + 70, 300), (ax + 110, 380),
                                (ax + 110, 860)], closed=True)
            cv.drawPath(arch, P(shader=lin(0, 250, 0, 860, ['#3b120b', '#5e1d10'])))
            cv.drawPath(arch, P('#e0b15a', stroke=6))
        cv.drawRect(skia.Rect.MakeLTRB(-1400, 120, 3400, 160), P('#e0b15a'))

    def floor(cv, c):
        cv.drawRect(skia.Rect.MakeLTRB(-1400, 860, 3400, 2600), P(shader=lin(0, 860, 0, 1200, ['#8e1b1b', '#4a0e0e'])))
        for i in range(-10, 30):
            cv.drawLine(i * 140, 860, i * 140 - 400, 1400, P(C('#f2c232', 0.25), stroke=3))
        cv.drawRect(skia.Rect.MakeLTRB(-1400, 860, 3400, 880), P('#f2c232'))
        rays(cv, 960, -100, c['t'], col='#ffe0a3', a=0.12, n=6, spread=60, length=1400)
    return [(0.3, wall), (0.9, floor)]

def bg_land(kind='fergana', t_override=None):
    pal = {
        'fergana': (('#4f8fd6', '#a9d6f5', '#f4e6c2'), '#6a8fb5', '#7aa35a', '#9cbf62', '#4e6b2e', 'day'),
        'snow': (('#5a7bb5', '#b9cfe8', '#eef3fa'), '#c9d6e6', '#dfe8f2', '#f4f8fc', '#c4d2e2', 'snow'),
        'kabul': (('#5f8ac0', '#d9c3a0', '#f2d9a8'), '#a1856a', '#b89a74', '#d9bd8c', '#a8865a', 'dry'),
        'dusk': (('#2b1d4a', '#c25a4a', '#f2a65a'), '#5b3a55', '#6b4a3a', '#a07a4a', '#5a3a22', 'dusk'),
        'battle': (('#7a6a8a', '#d9a878', '#f0d6a8'), '#8a7a6a', '#9a8a6a', '#c9b07a', '#8a6a3a', 'dust'),
        'river': (('#4f8fd6', '#a9d6f5', '#f4e6c2'), '#6a8fb5', '#8aa36a', '#b6c27a', '#6b7a3a', 'day'),
        'fire': (('#1a0505', '#7a1a0a', '#e0602a'), '#2a0e0a', '#3a120a', '#4a2a1a', '#1a0a05', 'fire'),
        'night': (('#05071a', '#141a44', '#2b2350'), '#151a3a', '#1a2236', '#232a3a', '#0e1420', 'night'),
    }[kind]
    skyc, far, mid, g1, g2, mood = pal

    def sky(cv, c):
        bg_sky(cv, *skyc)
        t = c['t']
        if mood in ('night',):
            stars(cv, t)
        elif mood in ('day', 'dry', 'snow'):
            draw_sun(cv, 1550, 170, 60, t, a=0.8)
        elif mood == 'dusk':
            draw_sun(cv, 960, 620, 110, t, a=0.9)
        for i in range(4):
            cc = '#ffffff' if mood not in ('fire', 'night', 'dusk') else '#5a3030'
            cloud(cv, (i * 640 + t * 10) % 2800 - 400, 160 + 70 * (i % 2), 1.2, cc, 0.5)

    def mts(cv, c):
        mountains(cv, 700, far, 3, amp=380 if kind in ('snow', 'kabul') else 240)
        if kind == 'snow':
            mountains(cv, 700, '#ffffff', 3, amp=380)  # snow caps by over-draw
            mountains(cv, 760, '#b8c8dc', 7, amp=260)
        if kind == 'kabul':
            for i, x in enumerate(range(1100, 1800, 70)):
                h = 60 + 40 * ((i * 7) % 3)
                cv.drawRect(skia.Rect.MakeLTRB(x, 760 - h, x + 60, 760), P('#c9a57a'))
                cv.drawRect(skia.Rect.MakeLTRB(x, 760 - h, x + 60, 760), P(C('#6d4c41', 0.6), stroke=2))
            cv.drawRect(skia.Rect.MakeLTRB(1300, 520, 1560, 760), P('#b8946a'))
            for k in range(6):
                cv.drawRect(skia.Rect.MakeLTRB(1300 + k * 46, 500, 1324 + k * 46, 520), P('#b8946a'))

    def near(cv, c):
        mountains(cv, 800, mid, 11, amp=120)
        ground(cv, 860, g1, g2)
        if kind == 'river':
            cv.drawPath(smooth_path([(-1400, 960), (300, 930), (1000, 960), (1800, 925), (3400, 955)]),
                        P(C('#4f9bd6', 0.95), stroke=110))
            for i in range(8):
                x = (c['t'] * 60 + i * 300) % 2400 - 200
                cv.drawLine(x, 940, x + 80, 940, P(C('#e3f2fd', 0.7), stroke=3))
        if kind == 'fergana':
            for x in (-200, 200, 1650, 2050):
                draw_tree(cv, x, 870, 1.2, col='#4caf50', t=c['t'])
    layers = [(0.05, sky), (0.3, mts), (0.85, near)]
    return layers

def parchment_bg():
    rnd = random.Random(4)
    spots = [(rnd.uniform(-200, 2100), rnd.uniform(-100, 1200), rnd.uniform(40, 160)) for _ in range(40)]

    def paper(cv, c):
        cv.drawRect(skia.Rect.MakeLTRB(-1400, -1400, 3400, 2600), P(shader=rad(960, 540, 1300, ['#f4e3bf', '#e2c58f', '#b8915a'])))
        for x, y, r in spots:
            cv.drawCircle(x, y, r, P(C('#a67c46', 0.06)))
        cv.drawRect(skia.Rect.MakeLTRB(60, 60, 1860, 1020), P('#7a4e1f', stroke=6))
        cv.drawRect(skia.Rect.MakeLTRB(80, 80, 1840, 1000), P(C('#7a4e1f', 0.6), stroke=2))
    return [(0.6, paper)]

# ------------------------------------------------------------------ map
PLACES = {'फ़रग़ना': (760, 230), 'समरक़ंद': (640, 280), 'काबुल': (690, 470), 'सिंधु नदी': (820, 600),
          'पानीपत': (1040, 600), 'दिल्ली': (1075, 650), 'आगरा': (1100, 720), 'फ़ारस': (330, 520)}

def draw_map(cv, t, route=0.0, empire=0.0, empire_col='#2e7d32', crack=0.0, shrink=0.0, highlight=None):
    # land masses (stylized)
    land = smooth_path([(240, 160), (900, 120), (1300, 200), (1500, 420), (1450, 600), (1350, 820), (1180, 980),
                        (1100, 1010), (1000, 900), (930, 760), (820, 700), (600, 640), (380, 620), (220, 450)], closed=True)
    cv.drawPath(land, P(C('#e9d3a3', 0.9)))
    cv.drawPath(land, P('#7a4e1f', stroke=4))
    # mountains row (Hindu Kush)
    for i in range(9):
        x = 560 + i * 45
        cv.drawPath(poly([(x - 24, 430), (x, 380), (x + 24, 430)]), P(C('#8d6e63', 0.8)))
        cv.drawPath(poly([(x - 8, 395), (x, 380), (x + 8, 395)]), P('#ffffff'))
    # rivers
    cv.drawPath(smooth_path([(780, 420), (800, 520), (820, 620), (790, 760), (760, 840)]), P('#4f8fd6', stroke=6))
    cv.drawPath(smooth_path([(1040, 560), (1080, 680), (1180, 800), (1300, 880)]), P('#4f8fd6', stroke=5))
    if empire > 0:
        cx, cy = 1075, 650
        k = empire * (1 - shrink * 0.93)
        rnd = random.Random(2)
        pts = []
        for j in range(16):
            a = j / 16 * 6.283
            r = (90 + 330 * k) * (0.8 + 0.35 * rnd.random())
            pts.append((cx + r * math.cos(a) * 1.0, cy + r * math.sin(a) * 0.9))
        cv.save()
        cv.clipPath(land, doAntiAlias=True)
        cv.drawPath(smooth_path(pts, closed=True), P(C(empire_col, 0.35)))
        cv.drawPath(smooth_path(pts, closed=True), P(C(empire_col, 0.9), stroke=4))
        if crack > 0:
            rnd2 = random.Random(5)
            for j in range(int(10 * crack)):
                x, y = cx + rnd2.uniform(-300, 300), cy + rnd2.uniform(-250, 250)
                pp = [(x, y)]
                for k2 in range(5):
                    x += rnd2.uniform(-60, 60); y += rnd2.uniform(-60, 60); pp.append((x, y))
                path = skia.Path(); path.moveTo(*pp[0])
                for q in pp[1:]:
                    path.lineTo(*q)
                cv.drawPath(path, P(C('#3e2723', 0.9), stroke=4))
        cv.restore()
    # route Fergana -> Kabul -> Panipat
    rp = [PLACES['फ़रग़ना'], (720, 340), PLACES['काबुल'], (860, 540), PLACES['पानीपत']]
    if route > 0:
        path = smooth_path(rp)
        meas = skia.PathMeasure(path, False)
        L_ = meas.getLength()
        seg = skia.Path()
        meas.getSegment(0, L_ * min(1, route), seg, True)
        pe = skia.DashPathEffect.Make([22, 14], -t * 40)
        pp = P('#b71c1c', stroke=8)
        pp.setPathEffect(pe)
        cv.drawPath(seg, pp)
        pos = meas.getPosTan(L_ * min(1, route))
        if pos:
            (px, py), _ = pos
            glow(cv, px, py, 50, '#ff5252', 0.8)
            cv.drawCircle(px, py, 12, P('#b71c1c'))
    for name, (x, y) in PLACES.items():
        hl = highlight and name in highlight
        cv.drawCircle(x, y, 10 if hl else 7, P('#3e2723'))
        if hl:
            glow(cv, x, y, 60, '#ffd54f', 0.7)
        draw_text(cv, name, x + 16, y - 4, 34 if hl else 28, 'title', '#3e2723', anchor='l')
