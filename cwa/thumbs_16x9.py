from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import FONTS as FD, OUT
HEAD, BODY = FD + 'RozhaOne-Regular.ttf', FD + 'YatraOne-Regular.ttf'
Y, W_, R = '#ffd21f', '#ffffff', '#c8161d'
def F(p, s): return ImageFont.truetype(p, s, layout_engine=ImageFont.Layout.RAQM)
from thumbs_config import SPEC, NAMES   # your project's thumbnail text
MAXW, TOP, BOT = 1060, 40, 960
def measure(kind, txt, s):
    f = F(HEAD if kind == 't' else BODY, s); b = f.getbbox(txt); return f, b[2] - b[0], b[3] - b[1], b
def build(k):
    art = Image.open(os.path.join(OUT, 'thumbs', f'art{k}.png')).convert('RGB')
    C = Image.new('RGB', (1920, 1080))
    bg = art.resize((1920, round(art.height * 1920 / art.width)), Image.LANCZOS)
    t = max(0, (bg.height - 1080) // 2); bg = bg.crop((0, t, 1920, t + 1080)).filter(ImageFilter.GaussianBlur(30))
    C.paste(ImageEnhance.Brightness(bg).enhance(0.35))
    a = art.resize((round(art.width * 1080 / art.height), 1080), Image.LANCZOS)
    ax = 1920 - a.width
    m = Image.new('L', a.size, 255); d = ImageDraw.Draw(m)
    for i in range(260): d.line([(i, 0), (i, 1080)], fill=int(255 * i / 260))
    C.paste(a, (ax, 0), m)
    # left darkening for text legibility
    g = Image.new('L', (1920, 1080), 0); d = ImageDraw.Draw(g)
    for x in range(1200): d.line([(x, 0), (x, 1080)], fill=int(200 * max(0, 1 - x / 1200)))
    C = Image.composite(Image.new('RGB', C.size, (12, 4, 6)), C, g)
    # fit text block
    spec = SPEC[k]; sc = 1.0
    while True:
        items = []
        for it in spec:
            kind, txt, s = it[0], it[1], int(it[2] * sc * 1.35)
            f, w, h, b = measure(kind, txt, s)
            pad = 0 if kind == 't' else int(s * 0.45)
            items.append((it, f, w, h, b, pad))
        tw = max(w + 2 * p for _, _, w, _, _, p in items)
        th = sum(h + 2 * p for _, _, _, h, _, p in items) + 16 * (len(items) - 1)
        if tw <= MAXW and th <= BOT - TOP: break
        sc *= 0.95
    y = TOP + (BOT - TOP - th) // 2
    d = ImageDraw.Draw(C)
    for it, f, w, h, b, pad in items:
        kind, txt = it[0], it[1]
        x = 70
        if kind == 't':
            sw = max(6, int(f.size * 0.07))
            sh = Image.new('RGBA', C.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).text((x + 8 - b[0], y + 10 - b[1]), txt, font=f, fill=(0, 0, 0, 180), stroke_width=sw, stroke_fill=(0, 0, 0, 180))
            C.paste(Image.new('RGB', C.size, (0, 0, 0)), (0, 0), sh.split()[3].filter(ImageFilter.GaussianBlur(6)))
            d = ImageDraw.Draw(C); d.text((x - b[0], y - b[1]), txt, font=f, fill=it[3], stroke_width=sw, stroke_fill='#120607')
        else:
            bw, bh = w + 2 * pad, h + 2 * pad
            if kind == 'b':
                d.rounded_rectangle((x, y, x + bw, y + bh), radius=18, fill='#f3d58a', outline='#7a4a12', width=6)
                d.text((x + pad - b[0], y + pad - b[1]), txt, font=f, fill='#5a1408')
            else:
                d.polygon([(x - 6, y + 8), (x + bw + 10, y), (x + bw - 4, y + bh - 6), (x + 4, y + bh + 4)], fill=R)
                d.text((x + pad - b[0], y + pad - b[1]), txt, font=f, fill='#ffffff', stroke_width=3, stroke_fill='#5a0a0e')
            h = bh
        y += h + (2 * pad if kind == 't' else 0) + 16
    # brand strip
    fb = F(HEAD, 44); bb = fb.getbbox('कथा और रहस्य'); bw = bb[2] - bb[0] + 60
    d.polygon([(52, 990), (70 + bw, 982), (60 + bw, 1050), (58, 1056)], fill=R)
    d.text((82 - bb[0], 1018 - (bb[3] + bb[1]) // 2), 'कथा और रहस्य', font=fb, fill='#ffffff')
    out = os.path.join(OUT, 'thumbnails-16x9', f'{NAMES[k]}.jpg'); os.makedirs(os.path.dirname(out), exist_ok=True)
    C.save(out, quality=90); return out
outs = [build(k) for k in sorted(SPEC)]
s = Image.new('RGB', (3 * 640, 2 * 360))
for i, o in enumerate(outs): s.paste(Image.open(o).resize((640, 360)), ((i % 3) * 640, (i // 3) * 360))
s.save(os.path.join(OUT, 'thumbnails-16x9', 'contact_sheet.jpg')); print('\n'.join(f'{o} {os.path.getsize(o)//1024}KB' for o in outs))
