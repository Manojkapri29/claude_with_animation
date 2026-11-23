"""Generate realistic sound effects with ElevenLabs (optional). Needs ELEVENLABS_API_KEY in your environment.
Reads sfx_list.txt in your project (name|seconds|prompt) and writes sfx/<name>.wav.
Without a key the renderer simply skips missing effects."""
import os, sys, json, subprocess, urllib.request
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cwa'))
from config import PROJECT, SFX
key = os.environ.get('ELEVENLABS_API_KEY')
if not key:
    sys.exit('Set ELEVENLABS_API_KEY first (never commit it to git).')
for line in open(os.path.join(PROJECT, 'sfx_list.txt'), encoding='utf-8'):
    if not line.strip() or line.startswith('#'):
        continue
    name, dur, text = line.strip().split('|', 2)
    wav = os.path.join(SFX, name + '.wav')
    if os.path.exists(wav):
        continue
    req = urllib.request.Request('https://api.elevenlabs.io/v1/sound-generation', method='POST',
                                 data=json.dumps({'text': text, 'duration_seconds': float(dur), 'prompt_influence': 0.45}).encode(),
                                 headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    mp3 = wav[:-4] + '.mp3'
    open(mp3, 'wb').write(urllib.request.urlopen(req).read())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-ac', '1', '-ar', '24000', wav], check=True)
    os.remove(mp3); print('ok', name)
