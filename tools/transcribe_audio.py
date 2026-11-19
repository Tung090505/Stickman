import os, sys, json
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, r'C:\File D\Stickman')

import torch
from transformers import pipeline

audio_path = r"C:\File D\Stickman\caveman-story\Chương 1.wav"
output_path = r"C:\File D\Stickman\caveman-story\transcription.json"

device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Loading PhoWhisper on {device}...")

pipe = pipeline(
    "automatic-speech-recognition",
    model="vinai/PhoWhisper-small",
    device=device,
    chunk_length_s=30,
    return_timestamps="word"
)

print(f"Transcribing {audio_path}...")
res = pipe(audio_path, return_timestamps=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=2)

print(f"Done! Saved to {output_path}")
chunks = res.get('chunks', [])
print(f"Total chunks: {len(chunks)}")
for i, c in enumerate(chunks[:5]):
    ts = c.get('timestamp', [0, 0])
    print(f"  [{ts[0]:.2f} - {ts[1]:.2f}] {c.get('text', '')[:50]}")