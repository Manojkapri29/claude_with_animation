"""Style 10: ICEBERG DIVE — camera sinks from the tip of an iceberg to the dark bottom,
revealing one 'level' per beat. Pure code (Pillow + ffmpeg), 1080x1920, free.
    python reel_styles/iceberg.py examples/iceberg_bharat.json out.mp4
JSON: {"title": "...", "levels": [["label", "small line"], ...], "end": "..."}"""
import json, math, os, subprocess, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'fonts') + '/'
W, H, FPS = 1080, 1920, 30
def F(n, s): return ImageFont.truetype(FD + n, s, layout_engine=ImageFont.Layout.RAQM)
def ease(t): t = max(0, min(1, t)); return t * t * (3 - 2 * t)
def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def world(depth_px):
    """Tall world image: sky 0..700, water below. Returns gradient colour for world y."""
    pass

def render(spec, out):
    lv = spec['levels']; n = len(lv)
    WORLD = 1500 + n * 900 + 900                      # world height
    SEA = 1150                                       # waterline y in world
    T = 2.2 + n * 2.6 + 2.4                          # seconds
    # pre-draw static world (sky, sea gradient, iceberg) once
    wimg = Image.new('RGB', (W, WORLD)); d = ImageDraw.Draw(wimg)
    for y in range(WORLD):
        if y < SEA: c = lerp((120, 190, 235), (200, 232, 250), y / SEA)
        else:
            k = (y - SEA) / (WORLD - SEA); c = lerp((40, 150, 205), (3, 10, 28), k ** 0.8)
        d.line([(0, y), (W, y)], fill=c)
    # iceberg: tip above water, huge body below
    tip = [(540, 640), (610, 760), (700, 900), (780, SEA), (300, SEA), (380, 930), (470, 760)]
    body = [(300, SEA), (780, SEA), (930, SEA + 900), (1010, SEA + 2400), (900, WORLD - 700),
            (620, WORLD - 420), (380, WORLD - 560), (150, WORLD - 1300), (90, SEA + 1900), (170, SEA + 700)]
    ice = Image.new('RGBA', (W, WORLD), (0, 0, 0, 0)); di = ImageDraw.Draw(ice)
    di.polygon(tip, fill=(245, 252, 255, 255)); di.polygon([(540, 640), (610, 760), (700, 900), (780, SEA), (560, SEA)], fill=(215, 236, 248, 255))
    for y in range(SEA, WORLD):                       # body: fades darker with depth
        k = (y - SEA) / (WORLD - SEA); a = int(225 - 120 * k)
    di.polygon(body, fill=(150, 210, 240, 150))
    ice = ice.filter(ImageFilter.GaussianBlur(1.2)); wimg.paste(ice, (0, 0), ice)
    dark = Image.new('L', (W, WORLD), 0); dd = ImageDraw.Draw(dark)
    for y in range(SEA, WORLD): dd.line([(0, y), (W, y)], fill=int(200 * ((y - SEA) / (WORLD - SEA)) ** 1.4))
    wimg = Image.composite(Image.new('RGB', (W, WORLD), (2, 6, 18)), wimg, dark)
    ImageDraw.Draw(wimg).line([(0, SEA), (W, SEA)], fill=(230, 245, 255), width=3)
    fT, fL, fS, fN = F('RozhaOne-Regular.ttf', 78), F('YatraOne-Regular.ttf', 62), F('NotoSansDevanagari.ttf', 38), F('RozhaOne-Regular.ttf', 54)
    levy = [SEA - 300] + [SEA + 500 + i * 900 for i in range(n - 1)]
    random.seed(3); bubbles = [(random.randint(0, W), random.randint(SEA, WORLD), random.uniform(2, 7), random.uniform(40, 120)) for _ in range(140)]
    tmp = out + '.frames'; os.makedirs(tmp, exist_ok=True)
    for f in range(int(T * FPS)):
        t = f / FPS
        # camera: hold on tip, then glide level to level
        seg = max(0, (t - 2.2) / 2.6); i = min(int(seg), n - 1); fr = ease((seg - int(seg)) / 0.55) if seg < n else 1
        cy_a = levy[min(i, n - 1)]; cy_b = levy[min(i + 1, n - 1)]
        cy = (levy[0] if t < 2.2 else cy_a + (cy_b - cy_a) * fr) - 860
        cy = max(0, min(WORLD - H, cy)); y0 = int(cy)
        im = wimg.crop((0, y0, W, y0 + H)).copy(); dr = ImageDraw.Draw(im, 'RGBA')
        for bx, by, r, sp in bubbles:                 # rising bubbles
            yy = (by - t * sp) - y0
            if 0 < yy < H and by > SEA: dr.ellipse([bx - r, yy - r, bx + r, yy + r], outline=(200, 235, 255, 120), width=2)
        # title card
        a = int(255 * ease(t / 0.6)) if t < 2.4 else int(255 * (1 - ease((t - 2.4) / 0.5)))
        if a > 0:
            bb = fT.getbbox(spec['title']); x = (W - (bb[2] - bb[0])) // 2
            dr.text((x - bb[0], 170), spec['title'], font=fT, fill=(255, 255, 255, a), stroke_width=6, stroke_fill=(10, 30, 60, a))
        # level labels (appear when camera reaches them, stay)
        for k, (lab, sub) in enumerate(lv):
            show = 0.6 if k == 0 else 2.2 + (k - 1) * 2.6 + 1.3
            if t < show: continue
            al = ease((t - show) / 0.4); yy = levy[k] - y0
            if not -200 < yy < H + 100: continue
            col = (255, 214, 64) if k == n - 1 else (255, 255, 255)
            txt = f'{k + 1}. {lab}'; bb = fL.getbbox(txt); tw = bb[2] - bb[0]
            px = (W - tw) // 2 - 40; bw = tw + 80
            dr.rounded_rectangle([px, yy - 70, px + bw, yy + 40], 30, fill=(8, 22, 48, int(200 * al)), outline=(255, 255, 255, int(160 * al)), width=3)
            dr.text((px + 40 - bb[0], yy - 58), txt, font=fL, fill=col + (int(255 * al),))
            sb = fS.getbbox(sub); dr.text(((W - (sb[2] - sb[0])) // 2 - sb[0], yy + 62), sub, font=fS, fill=(210, 230, 250, int(230 * al)), stroke_width=3, stroke_fill=(0, 0, 0, int(200 * al)))
        # depth meter
        dm = max(0, int((cy + 860 - SEA) / 9)); dr.text((60, H - 140), f'गहराई: {dm} मीटर', font=fS, fill=(255, 255, 255, 200))
        if t > T - 2.0:                                # ending line
            al = ease((t - (T - 2.0)) / 0.5); eb = fN.getbbox(spec['end'])
            dr.text(((W - (eb[2] - eb[0])) // 2 - eb[0], H - 420), spec['end'], font=fN, fill=(255, 214, 64, int(255 * al)), stroke_width=5, stroke_fill=(0, 0, 0, int(255 * al)))
        im.save(f'{tmp}/{f:05d}.jpg', quality=90)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%05d.jpg',
                    '-f', 'lavfi', '-i', f'sine=frequency=110:duration={T},volume=0.05', '-shortest',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-crf', '20', '-c:a', 'aac', out], check=True)
    subprocess.run(['rm', '-rf', tmp])

if __name__ == '__main__':
    render(json.load(open(sys.argv[1])), sys.argv[2])
