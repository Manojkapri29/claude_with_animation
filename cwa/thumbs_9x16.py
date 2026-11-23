"""9:16 Shorts thumbnails: art{N}.png full-bleed + big Hindi text on top + channel strip.
    python cwa/thumbs_9x16.py          # all in thumbs_config.SPEC
    python cwa/thumbs_9x16.py 2 3
Text spec format is the same as thumbs_16x9 (t = big text, b = banner, r = red strip)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config import FONTS as FD, OUT
from thumbs_config import SPEC, NAMES
HEAD, BODY = FD + 'RozhaOne-Regular.ttf', FD + 'YatraOne-Regular.ttf'
R = '#c8161d'
BRAND = os.environ.get('CWA_BRAND', 'कथा और रहस्य')
W, H, MAXW, TOP, BOT = 1080, 1920, 980, 70, 1000

def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)

def build(k):
    art = Image.open(os.path.join(OUT, 'thumbs', f'art{k}.png')).convert('RGB')
    s = max(W / art.width, H / art.height)
    art = art.resize((round(art.width * s), round(art.height * s)), Image.LANCZOS)
    x0, y0 = (art.width - W) // 2, (art.height - H) // 2
    C = art.crop((x0, y0, x0 + W, y0 + H))
    g = Image.new('L', (W, H), 0); d = ImageDraw.Draw(g)          # dark top for text
    for y in range(1150): d.line([(0, y), (W, y)], fill=int(215 * (1 - y / 1150) ** 1.3))
    for y in range(1700, H): d.line([(0, y), (W, y)], fill=int(170 * (y - 1700) / 220))
    C = Image.composite(Image.new('RGB', C.size, (10, 4, 6)), C, g)
    sc = 1.0
    while True:
        items = []
        for it in SPEC[k]:
            kind, txt, sz = it[0], it[1], int(it[2] * sc * 1.25)
            f = F(HEAD if kind == 't' else BODY, sz); b = f.getbbox(txt)
            pad = 0 if kind == 't' else int(sz * 0.4)
            items.append((it, f, b[2] - b[0], b[3] - b[1], b, pad))
        tw = max(w + 2 * p for _, _, w, _, _, p in items)
        th = sum(h + 2 * p for _, _, _, h, _, p in items) + 18 * (len(items) - 1)
        if tw <= MAXW and th <= BOT - TOP: break
        sc *= 0.95
    y = TOP
    for it, f, w, h, b, pad in items:
        kind, txt = it[0], it[1]
        bw = w + 2 * pad; x = (W - bw) // 2
        d = ImageDraw.Draw(C)
        if kind == 't':
            sw = max(6, int(f.size * 0.07))
            sh = Image.new('L', C.size, 0)
            ImageDraw.Draw(sh).text((x + 8 - b[0], y + 10 - b[1]), txt, font=f, fill=180, stroke_width=sw, stroke_fill=180)
            C.paste((0, 0, 0), (0, 0, W, H), sh.filter(ImageFilter.GaussianBlur(6)))
            d = ImageDraw.Draw(C); d.text((x - b[0], y - b[1]), txt, font=f, fill=it[3], stroke_width=sw, stroke_fill='#120607')
            y += h + 18
        else:
            bh = h + 2 * pad
            if kind == 'b':
                d.rounded_rectangle((x, y, x + bw, y + bh), radius=18, fill='#f3d58a', outline='#7a4a12', width=6)
                d.text((x + pad - b[0], y + pad - b[1]), txt, font=f, fill='#5a1408')
            else:
                d.polygon([(x - 6, y + 8), (x + bw + 10, y), (x + bw - 4, y + bh - 6), (x + 4, y + bh + 4)], fill=R)
                d.text((x + pad - b[0], y + pad - b[1]), txt, font=f, fill='#ffffff', stroke_width=3, stroke_fill='#5a0a0e')
            y += bh + 18
    fb = F(HEAD, 46); bb = fb.getbbox(BRAND); bw = bb[2] - bb[0] + 60; bx = (W - bw) // 2
    d.polygon([(bx, 1810), (bx + bw + 10, 1802), (bx + bw, 1872), (bx + 4, 1878)], fill=R)
    d.text((bx + 30 - bb[0], 1840 - (bb[3] + bb[1]) // 2), BRAND, font=fb, fill='#ffffff')
    out = os.path.join(OUT, 'thumbnails-9x16', NAMES[k].replace('-16x9', '') + '.jpg')
    os.makedirs(os.path.dirname(out), exist_ok=True); C.save(out, quality=90); return out

if __name__ == '__main__':
    for k in [int(a) for a in sys.argv[1:]] or sorted(SPEC): print(build(k))
