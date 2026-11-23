"""Transcribe your narration and map word times onto the final timeline.
Writes words_final.json (keyword captions) and seg_starts.json (cut points) into the project.
Usage: CWA_PROJECT=projects/my_video python tools/transcribe.py"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'cwa'))
from config import PROJECT, SRC
import scenes as S
from faster_whisper import WhisperModel

model = WhisperModel('small', device='cpu', compute_type='int8')
cache, words, starts = {}, [], []
for fname, s0, s1, at in S.SEGMENTS:
    if fname not in cache:
        segs, _ = model.transcribe(os.path.join(SRC, fname), language=os.environ.get('CWA_LANG', 'hi'),
                                   word_timestamps=True, condition_on_previous_text=False)
        cache[fname] = [(s.start, [(w.start, w.word.strip()) for w in s.words]) for s in segs]
    for seg_start, ws in cache[fname]:
        if s0 <= seg_start < s1:
            starts.append(at + seg_start - s0)
        for t, w in ws:
            if s0 <= t < s1:
                words.append((at + t - s0, w))
words.sort(); starts.sort()
json.dump(words, open(os.path.join(PROJECT, 'words_final.json'), 'w'), ensure_ascii=False)
json.dump(starts, open(os.path.join(PROJECT, 'seg_starts.json'), 'w'))
print(len(words), 'words,', len(starts), 'phrases. Now pick KEYS (caption words) in render_long.py.')
