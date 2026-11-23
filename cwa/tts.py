import sys, os, time, torch, torchaudio as ta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import QAUDIO, VOICE_REF
torch.set_num_threads(4)
from quiz_data import JOBS
OUT = QAUDIO
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
for jid, text in JOBS:
    p = f"{OUT}/{jid}.wav"
    if os.path.exists(p): continue
    t0 = time.time()
    wav = model.generate(text, language_id="hi", audio_prompt_path=VOICE_REF, exaggeration=0.55, cfg_weight=0.45)
    ta.save(p, wav, model.sr); print(jid, round(wav.shape[-1] / model.sr, 1), round(time.time() - t0), flush=True)
print("DONE", flush=True)
