"""Free realistic thumbnail art via Hugging Face Spaces (no GPU, no install beyond gradio_client).

    python tools/thumb_art.py            # every entry in thumbs_config.ART
    python tools/thumb_art.py 2 4        # only these numbers

Writes OUT/thumbs/art{N}.png (9:16, 1080x1920). Then run cwa/thumbs_9x16.py / cwa/thumbs_16x9.py.
Optional: export HF_TOKEN=hf_xxx (free account) for a bigger daily GPU quota.
"""
import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cwa'))
from config import OUT
from thumbs_config import ART            # {N: 'prompt in English, no text'}
from gradio_client import Client
from PIL import Image

STYLE = ', cinematic historical film still, dramatic rim light, shallow depth of field, 85mm lens, rich colour grade, highly detailed, no text, no letters, no watermark'
SPACES = [  # tried in order; first is most realistic
    ('mcp-tools/FLUX.1-Krea-dev', dict(guidance_scale=4.5, num_inference_steps=24, api_name='/infer')),
    ('evalstate/flux1_schnell', dict(num_inference_steps=4, api_name='/infer')),
]

def gen(prompt, seed):
    for space, extra in SPACES:
        for attempt in range(2):
            try:
                c = Client(space, token=os.environ.get('HF_TOKEN') or None, verbose=False)
                r = c.predict(prompt=prompt + STYLE, seed=seed, randomize_seed=False, width=768, height=1344, **extra)
                return Image.open(r[0] if isinstance(r, (list, tuple)) else r).convert('RGB'), space
            except Exception as e:
                print(f'  {space} failed ({str(e)[:90]}), retrying...'); time.sleep(5)
    raise SystemExit('All free spaces busy or quota over. Try later or set HF_TOKEN.')

if __name__ == '__main__':
    keys = [int(a) for a in sys.argv[1:]] or sorted(ART)
    os.makedirs(os.path.join(OUT, 'thumbs'), exist_ok=True)
    for k in keys:
        im, sp = gen(ART[k], seed=100 + k)
        im = im.resize((1080, 1920), Image.LANCZOS)   # for sharper output: python cwa/upscale.py <in> <out>
        p = os.path.join(OUT, 'thumbs', f'art{k}.png'); im.save(p)
        print(f'art{k} <- {sp}: {p}')
