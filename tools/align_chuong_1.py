import os
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
import json
import torch
from transformers import pipeline

audio_path = r"C:\File D\Stickman\caveman-story\Chương 1.wav"
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

out_json = r"C:\File D\Stickman\caveman-story\chuong1_phowhisper.json"
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=2)

print(f"Done! Saved {len(res.get('chunks', []))} chunks to {out_json}")
for i, c in enumerate(res.get("chunks", [])[:10]):
    print(f"[{c['timestamp'][0]:.2f} - {c['timestamp'][1]}] {c['text']}")
