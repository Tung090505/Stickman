import os, sys, json
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
OUTPUT_DIR = os.path.join(BASE_DIR, "caveman-story")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load model
print("Loading OmniVoice model on GPU...")
model = OmniVoice.from_pretrained(
    r'C:\Users\tunga\AppData\Local\OmniVoice\hf_cache\models--k2-fsa--OmniVoice\snapshots\c5fdb5ccb189668d56333f77ba2629f4cd7535f4',
    device_map="cuda:0",
    dtype=torch.float16
)
print("Model loaded!")

# Read text from storyboard or argument
if len(sys.argv) > 1:
    text_file = sys.argv[1]
    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read().strip()
else:
    sys.path.insert(0, os.path.join(BASE_DIR, 'tools'))
    from parse_storyboard import parse_storyboard
    rows = parse_storyboard(os.path.join(BASE_DIR, 'Kịch bản loại người xuất hiện.txt'))
    text = ' '.join(r.get('loi_thoai', '') for r in rows)
    text = text.strip()

words = len(text.split())
estimated_dur = max(1.0, words / 4.5)
print(f"Text: {words} words, estimated duration: {estimated_dur:.1f}s")

# Trim reference audio to 4s
ref_audio = os.path.join(OUTPUT_DIR, "Kechuyen.wav")
ref_audio_trimmed = os.path.join(OUTPUT_DIR, "Kechuyen_trimmed.wav")
if not os.path.exists(ref_audio_trimmed):
    subprocess.run([
        'ffmpeg', '-y', '-i', ref_audio,
        '-t', '4',  # Trim to 4 seconds
        '-ar', '24000', '-ac', '1',
        ref_audio_trimmed
    ], capture_output=True)
    print("Trimmed reference audio to 4s")

# Generate audio
print("Generating audio...")
audio = model.generate(
    text=text,
    ref_audio=ref_audio_trimmed,
    ref_text="Thật không thể tin được! Anh ấy đã làm vậy sao? Tôi không biết phải làm sao trong tình huống này.",
    language_id="vi",  # Vietnamese
    num_step=32,  # Quality
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

# Trim leading silence (breath) manually
audio_arr = audio[0]
threshold = 0.01
abs_audio = np.abs(audio_arr)
non_silent = np.where(abs_audio > threshold)[0]
if len(non_silent) > 0:
    start_idx = non_silent[0]
    audio[0] = audio_arr[start_idx:]
    print(f"  Trimmed {start_idx} leading silence samples ({start_idx/24000:.3f}s)")

# Save
output_path = os.path.join(OUTPUT_DIR, "Chương 1.wav")
sf.write(output_path, audio[0], 24000)
print(f"Saved to: {output_path}")
print("Done!")