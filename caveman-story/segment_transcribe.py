import os
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
import json
import soundfile as sf
import numpy as np
from transformers import pipeline

audio_path = r'C:\File D\Stickman\caveman-story\chuong1.wav'
data, sr = sf.read(audio_path)
total_dur = len(data) / sr

# Silence boundaries found via ffmpeg
pauses = [
    (0.0, 3.0),
    (3.0, 6.8),
    (6.8, 26.4),
    (26.4, 30.3),
    (30.3, 33.1),
    (33.1, 39.9),
    (39.9, 56.4),
    (56.4, 60.6),
    (60.6, 64.2),
    (64.2, 67.2),
    (67.2, 70.0),
    (70.0, 74.75)
]

pipe = pipeline(
    'automatic-speech-recognition',
    model='vinai/PhoWhisper-small',
    device='cuda:0'
)

segments = []
for idx, (st, en) in enumerate(pauses):
    chunk_data = data[int(st * sr):int(en * sr)]
    if len(chunk_data) < sr * 0.3:
        continue
    tmp_path = rf'C:\File D\Stickman\caveman-story\temp_chunk_{idx}.wav'
    sf.write(tmp_path, chunk_data, sr)
    res = pipe(tmp_path)
    text = res['text'].strip()
    try:
        os.remove(tmp_path)
    except:
        pass
    if text:
        segments.append({
            'start': round(st, 2),
            'end': round(en, 2),
            'text': text
        })

with open(r'C:\File D\Stickman\caveman-story\aligned_captions.json', 'w', encoding='utf-8') as f:
    json.dump(segments, f, ensure_ascii=False, indent=2)

print('SUCCESS')
