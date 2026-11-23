"""Paths for one video project. Set CWA_PROJECT to your project folder (default: examples/mughal_panipat)."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT = os.path.abspath(os.environ.get('CWA_PROJECT', os.path.join(ROOT, 'examples', 'mughal_panipat')))
FONTS = os.path.join(ROOT, 'fonts') + '/'
SRC = os.path.join(PROJECT, 'src')        # your narration audio (wav) goes here
SFX = os.path.join(PROJECT, 'sfx')        # sound effects (wav), see tools/make_sfx.py
OUT = os.path.join(PROJECT, 'out')
QAUDIO = os.path.join(PROJECT, 'quiz_audio')
VOICE_REF = os.environ.get('CWA_VOICE_REF', os.path.join(PROJECT, 'voice_ref.wav'))
MODELS = os.path.join(ROOT, 'models')
for d in (OUT, SFX, QAUDIO, MODELS):
    os.makedirs(d, exist_ok=True)
for p in (PROJECT, os.path.dirname(os.path.abspath(__file__))):
    if p not in sys.path:
        sys.path.insert(0, p)
