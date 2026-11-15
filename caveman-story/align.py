import os
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
import json
from transformers import pipeline

pipe = pipeline(
    'automatic-speech-recognition',
    model='vinai/PhoWhisper-small',
    device='cuda:0',
    chunk_length_s=20,
    stride_length_s=3,
    return_timestamps=True
)

res = pipe(r'C:\File D\Stickman\caveman-story\chuong1.wav')
chunks = res.get('chunks', [])
print(f'Chunks count: {len(chunks)}')
for i, c in enumerate(chunks):
    ts = c.get('timestamp')
    t_text = c.get('text', '').strip()
    print(f'{i}: {ts} -> {t_text[:40]}')

with open(r'C:\File D\Stickman\caveman-story\chunks.json', 'w', encoding='utf-8') as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)
print('Done!')
