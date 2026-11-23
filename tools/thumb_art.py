"""Free realistic thumbnail art. Uses local mflux on an Apple Silicon Mac if installed (unlimited),
otherwise free Hugging Face Spaces (FLUX, daily quota).

    python tools/thumb_art.py            # every entry in thumbs_config.ART
    python tools/thumb_art.py 2 4        # only these numbers
    python tools/thumb_art.py --wide     # 16:9 art (artw{N}.png) for long-video thumbnails

Writes OUT/thumbs/art{N}.png (9:16, 1080x1920). Then run cwa/thumbs_9x16.py / cwa/thumbs_16x9.py.
Optional: export HF_TOKEN=hf_xxx (free account) for a bigger daily GPU quota.
"""
import os, sys, time, shutil, subprocess, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cwa'))
from config import OUT
from thumbs_config import ART            # {N: 'prompt in English, no text'}
from PIL import Image

STYLE = ', cinematic historical film still, dramatic rim light, shallow depth of field, 85mm lens, rich colour grade, highly detailed, no text, no letters, no watermark'
SPACES = [  # tried in order; first is most realistic
    ('mcp-tools/FLUX.1-Krea-dev', dict(guidance_scale=4.5, num_inference_steps=24, api_name='/infer')),
    ('evalstate/flux1_schnell', dict(num_inference_steps=4, api_name='/infer')),
]

LOCAL = shutil.which('mflux-generate-z-image-turbo')   # Mac (Apple Silicon): unlimited, offline. Install: tools/install_mflux_mac.command

def gen_local(prompt, seed, w, h):
    out = os.path.join(tempfile.mkdtemp(), 'a.png')
    subprocess.run([LOCAL, '--prompt', prompt + STYLE, '--width', str(w), '--height', str(h), '--steps', '9',
                    '--seed', str(seed), '-q', os.environ.get('CWA_MFLUX_Q', '8'), '--output', out], check=True)
    return Image.open(out).convert('RGB'), 'mflux Z-Image Turbo (local)'

def gen(prompt, seed, w=768, h=1344):
    if LOCAL and os.environ.get('CWA_IMAGE') != 'hf':
        return gen_local(prompt, seed, w, h)
    from gradio_client import Client
    for space, extra in SPACES:
        for attempt in range(2):
            try:
                c = Client(space, token=os.environ.get('HF_TOKEN') or None, verbose=False)
                r = c.predict(prompt=prompt + STYLE, seed=seed, randomize_seed=False, width=w, height=h, **extra)
                return Image.open(r[0] if isinstance(r, (list, tuple)) else r).convert('RGB'), space
            except Exception as e:
                print(f'  {space} failed ({str(e)[:90]}), retrying...'); time.sleep(5)
    raise SystemExit('All free spaces busy or quota over. Try later or set HF_TOKEN.')

if __name__ == '__main__':
    wide = '--wide' in sys.argv          # 16:9 art -> artw{N}.png (used by thumbs_16x9)
    keys = [int(a) for a in sys.argv[1:] if a.isdigit()] or sorted(ART)
    os.makedirs(os.path.join(OUT, 'thumbs'), exist_ok=True)
    for k in keys:
        if wide:
            im, sp = gen(ART[k] + ', wide shot, main subject on the right side', seed=100 + k, w=1344, h=768)
            im, name = im.resize((1920, 1080), Image.LANCZOS), f'artw{k}.png'
        else:
            im, sp = gen(ART[k], seed=100 + k)
            im, name = im.resize((1080, 1920), Image.LANCZOS), f'art{k}.png'
        p = os.path.join(OUT, 'thumbs', name); im.save(p)
        print(f'{name} <- {sp}: {p}')
