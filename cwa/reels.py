import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import OUT
from mengine import *
from PIL import Image
from reels_config import REELS   # your project's reel cuts
def overlay(lines, path):
    surf = skia.Surface(1080, 1920); cv = surf.getCanvas(); cv.clear(skia.ColorTRANSPARENT)
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, 1080, 560), P(shader=lin(0, 0, 0, 560, [C('#120608', 0.85), C('#120608', 0.0)])))
    draw_text(cv, 'कथा और रहस्य', 540, 150, 44, 'deco', '#e8c766')
    cv.drawRect(skia.Rect.MakeXYWH(390, 185, 300, 4), P('#f2c232'))
    draw_text(cv, lines[0], 540, 290, 96, 'title', '#ffd54f', stroke=6, maxw=1000)
    draw_text(cv, lines[1], 540, 420, 58, 'title', '#ffffff', stroke=4, maxw=1000)
    cv.drawRect(skia.Rect.MakeLTRB(0, 1380, 1080, 1920), P(shader=lin(0, 1380, 0, 1920, [C('#120608', 0.0), C('#120608', 0.85)])))
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(190, 1520, 700, 110), 55, 55)
    cv.drawRRect(r, P(C('#b71c1c', 0.95))); cv.drawRRect(r, P('#f2c232', stroke=4))
    draw_text(cv, 'पूरी कहानी चैनल पर देखें', 540, 1575, 50, 'title', '#ffffff')
    draw_text(cv, 'मुग़ल साम्राज्य: उदय • पानीपत • पतन', 540, 1700, 40, 'body', '#ffe9a8')
    Image.fromarray(surf.makeImageSnapshot().toarray()[..., [2, 1, 0, 3]]).save(path)
SRC = os.environ.get('CWA_FINAL', os.path.join(OUT, 'final.mp4'))
for name, a, b, lines in REELS:
    png = os.path.join(OUT, f'{name}.png'); overlay(lines, png)
    d = b - a
    fc = ("[0:v]crop=1920:952:0:64,split[a][b];"
          "[a]scale=-2:1920,crop=1080:1920,boxblur=30:2,eq=brightness=-0.18[bg];"
          "[b]crop=1270:952:325:0,scale=1080:810[fg];"
          "[bg][fg]overlay=0:560[v1];[v1][1:v]overlay=0:0,"
          f"fade=t=in:st=0:d=0.4,fade=t=out:st={d-0.5:.2f}:d=0.5[v]")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{a}', '-t', f'{d}', '-i', SRC, '-loop', '1', '-i', png,
                    '-filter_complex', fc, '-map', '[v]', '-map', '0:a', '-af', f'afade=t=in:d=0.3,afade=t=out:st={d-0.6:.2f}:d=0.6',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
                    '-t', f'{d}', '-movflags', '+faststart', os.path.join(OUT, f'{name}.mp4')], check=True)
    print(name, round(d, 1))
