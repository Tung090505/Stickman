import os, sys, json, subprocess
import torch
import soundfile as sf
import numpy as np
from omnivoice import OmniVoice

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = r"C:\File D\Stickman"
STORY_DIR = os.path.join(BASE_DIR, "caveman-story")
OUTPUT_DIR = os.path.join(STORY_DIR, "scene_audio")
STORYBOARD = os.path.join(BASE_DIR, "Kịch bản loại người xuất hiện.txt")
REF_AUDIO = os.path.join(STORY_DIR, "Kechuyen.wav")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load model on GPU
print("Loading OmniVoice model on GPU...")
model = OmniVoice.from_pretrained(
    r'C:\Users\tunga\AppData\Local\OmniVoice\hf_cache\models--k2-fsa--OmniVoice\snapshots\c5fdb5ccb189668d56333f77ba2629f4cd7535f4',
    device_map="cuda:0",
    dtype=torch.float16
)
print("Model loaded!")

# Read storyboard
sys.path.insert(0, os.path.join(BASE_DIR, 'tools'))
from parse_storyboard import parse_storyboard
rows = parse_storyboard(STORYBOARD)
print(f"Parsed {len(rows)} scenes")

# Trim reference audio to 4s (storytelling voice)
ref_audio_trimmed = os.path.join(STORY_DIR, "Kechuyen_trimmed.wav")
if not os.path.exists(ref_audio_trimmed):
    subprocess.run([
        'ffmpeg', '-y', '-i', REF_AUDIO,
        '-t', '4',  # Trim to 4 seconds
        '-ar', '24000', '-ac', '1',
        ref_audio_trimmed
    ], capture_output=True)
    print("Trimmed reference audio to 4s")

# Generate audio per scene
durations = []
for i, row in enumerate(rows):
    stt = str(row.get('stt', '')).strip().strip('*')
    text = row.get('loi_thoai', '').strip()
    if not text:
        print(f"[!] Scene {stt}: empty text, skipping")
        continue
    
    output_path = os.path.join(OUTPUT_DIR, f"scene_{stt}.wav")
    if os.path.exists(output_path):
        print(f"[-] Scene {stt}: already exists, skipping")
        res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                              '-of', 'default=noprint_wrappers=1:nokey=1', output_path],
                             capture_output=True, text=True)
        dur = float(res.stdout.strip())
        durations.append((stt, dur))
        continue
    
    print(f"[{i+1}/{len(rows)}] Generating scene {stt}: {text[:50]}...")
    
    # Estimate duration
    words = len(text.split())
    estimated_dur = max(1.0, words / 4.5)
    
    audio = model.generate(
        text=text,
        ref_audio=ref_audio_trimmed,
        ref_text="Thật không thể tin được! Anh ấy đã làm vậy sao? Tôi không biết phải làm sao trong tình huống này.",
        language_id='vi',  # Vietnamese
        num_step=32,  # Quality (higher = better but slower)
        speed=1.0,
        duration=estimated_dur,
        postprocess_output=True,   # Remove long silences (fixes breath sounds)
        pad_duration=0,            # Disable padding
        fade_duration=0,           # Disable fade
    )
    
    # Trim leading silence (breath) manually
    audio_arr = audio[0]
    threshold = 0.01
    abs_audio = np.abs(audio_arr)
    non_silent = np.where(abs_audio > threshold)[0]
    if len(non_silent) > 0:
        start_idx = non_silent[0]
        audio[0] = audio_arr[start_idx:]
    
    sf.write(output_path, audio[0], 24000)
    dur = len(audio[0]) / 24000
    durations.append((stt, dur))
    print(f"    -> Saved: scene_{stt}.wav ({dur:.2f}s)")

# Save durations
with open(os.path.join(OUTPUT_DIR, "durations.json"), 'w', encoding='utf-8') as f:
    json.dump(durations, f, indent=2)

print(f"\nDone! Generated {len(durations)} audio files.")
print(f"Total duration: {sum(d[1] for d in durations):.2f}s")