import os, sys, subprocess, re

sys.path.insert(0, os.path.dirname(__file__))
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from parse_storyboard import parse_storyboard

BASE_DIR = r"C:\File D\Stickman"
STORY_DIR = os.path.join(BASE_DIR, "caveman-story")
IMAGES_DIR = os.path.join(STORY_DIR, "images")
OUTPUT_DIR = os.path.join(STORY_DIR, "output")
SOUNDS_DIR = os.path.join(STORY_DIR, "sounds")
CACHE_DIR = os.path.join(OUTPUT_DIR, "audio_cache")
STORYBOARD = os.path.join(BASE_DIR, "Kịch bản loại người xuất hiện.txt")
AUDIO_FILE = os.path.join(STORY_DIR, "Chương 1.wav")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# --- 1. Parse storyboard ---
rows = parse_storyboard(STORYBOARD)
print(f"[*] Parsed {len(rows)} scenes from storyboard")

# --- 2. Calculate cumulative timing for each scene ---
scenes = []
cumulative_time = 0.0
for row in rows:
    try:
        stt = int(str(row.get("stt", "0")).strip().strip("*"))
    except (ValueError, TypeError):
        continue
    dur_str = row.get("thoi_luong", "2.5s")
    dur = float(str(dur_str).replace("s", "").strip())
    sfx = row.get("ten_sfx", "none").strip()
    img_name = f"{stt}.png"
    img_path = os.path.join(IMAGES_DIR, img_name)

    if not os.path.exists(img_path):
        print(f"[!] Skip scene {stt}: image not found ({img_name})")
        continue

    scenes.append({
        'stt': stt,
        'img': img_name,
        'img_path': img_path,
        'dur': dur,
        'start': cumulative_time,
        'end': cumulative_time + dur,
        'sfx': sfx if sfx.lower() not in ('none', '—', '') else None,
    })
    cumulative_time += dur

print(f"[*] Total scenes: {len(scenes)}, total duration: {cumulative_time:.2f}s")

# --- 3. Collect all SFX occurrences (ALL play at start of scene, 0.3s after start) ---
sfx_occurrences = []
for scene in scenes:
    if scene['sfx']:
        sfx_name = scene['sfx']
        # Fallback mapping for removed SFX
        sfx_fallback = {
            'sad trombone': 'Record Scratch',
            'sad_trombone': 'Record Scratch',
        }
        sfx_lookup = sfx_name.lower().replace('.mp3', '').replace('_', ' ')
        if sfx_lookup in sfx_fallback:
            sfx_lookup = sfx_fallback[sfx_lookup].lower()

        # Find matching file
        sfx_file = None
        sfx_normalized = sfx_lookup + '.mp3'
        for f in os.listdir(SOUNDS_DIR):
            f_normalized = f.lower().replace('_', ' ')
            if f_normalized == sfx_normalized:
                sfx_file = f
                break
        if sfx_file is None:
            for f in os.listdir(SOUNDS_DIR):
                f_base = f.lower().replace('.mp3', '').replace('_', ' ')
                if sfx_lookup in f_base or f_base in sfx_lookup:
                    sfx_file = f
                    break
        if sfx_file is None:
            print(f"[!] SFX not found: {sfx_name} (scene {scene['stt']})")
            continue

        # Transition SFX (whoosh, glitch, wind) play at scene boundary (0s offset)
        # Other SFX play 0.3s after scene start
        sfx_lower_name = sfx_file.lower()
        is_transition = any(k in sfx_lower_name for k in ['whoosh', 'glitch', 'wind', 'transition'])
        if is_transition:
            delay_ms = int(scene['start'] * 1000)  # Exactly at scene boundary
        else:
            delay_ms = int((scene['start'] + 0.3) * 1000)  # 0.3s after start

        # Volume per SFX (weather/ambient SFX quieter)
        weather_sfx = ['Wind.mp3', 'Thunder.mp3', 'Crickets.mp3', 'Water Splash.mp3', 'Fire Crackle.mp3', 'Heartbeat.mp3']
        if sfx_file == 'Record Scratch.mp3':
            vol = 0.1
        elif sfx_file == 'Dramatic Boom.mp3':
            vol = 0.8
        elif sfx_file in weather_sfx:
            vol = 0.2  # Weather/ambient SFX quieter
        else:
            vol = 0.5

        sfx_occurrences.append({
            'scene': scene['stt'],
            'sfx_name': sfx_name,
            'sfx_file': sfx_file,
            'delay_ms': delay_ms,
            'volume': vol,
        })

print(f"[*] Total SFX occurrences: {len(sfx_occurrences)}")
from collections import Counter
unique_sfx = Counter(o['sfx_file'] for o in sfx_occurrences)
print("[*] SFX breakdown:")
for sfx, count in unique_sfx.most_common():
    print(f"    {sfx}: {count} times")

# --- 4. Copy SFX files to cache ---
for occ in sfx_occurrences:
    src = os.path.join(SOUNDS_DIR, occ['sfx_file'])
    dst = os.path.join(CACHE_DIR, occ['sfx_file'])
    if not os.path.exists(dst):
        import shutil
        shutil.copy2(src, dst)

voice_cache = os.path.join(CACHE_DIR, "voice.wav")
if not os.path.exists(voice_cache):
    import shutil
    shutil.copy2(AUDIO_FILE, voice_cache)

# --- 5. Render individual clips ---
clip_files = []
for i, scene in enumerate(scenes):
    clip_path = os.path.join(OUTPUT_DIR, f"clip_{scene['stt']:03d}.mp4")
    vf = "scale=1280:720"
    cmd = [
        "ffmpeg", "-loop", "1", "-i", scene['img_path'],
        "-vf", vf,
        "-t", str(scene['dur']),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        clip_path, "-y"
    ]
    print(f"Rendering shot {i+1}/{len(scenes)} (scene {scene['stt']}, {scene['dur']:.2f}s)...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        print(f"  [!] Error: {res.stderr.decode('utf-8', errors='ignore')[:100]}")
        continue
    clip_files.append((scene, clip_path))

print(f"\n[*] Rendered {len(clip_files)} clips")

# --- 6. Concat all clips ---
concat_list = os.path.join(OUTPUT_DIR, "concat_list.txt")
with open(concat_list, "w", encoding="utf-8") as f:
    for scene, clip in clip_files:
        f.write(f"file '{clip}'\n")

raw_video = os.path.join(OUTPUT_DIR, "video_raw.mp4")
subprocess.run([
    "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_list,
    "-c", "copy", raw_video, "-y"
], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print("[*] Concatenated raw video")

# --- 7. Build filter_complex with all SFX ---
unique_sfx_files = list(set(o['sfx_file'] for o in sfx_occurrences))

inputs = ["-i", raw_video, "-i", voice_cache]
for sfx_file in unique_sfx_files:
    inputs.extend(["-i", os.path.join(CACHE_DIR, sfx_file)])

filter_parts = []
filter_parts.append("[0:v]null[v_out]")
filter_parts.append("[1:a]volume=1.0[a_voice]")

audio_labels = ["a_voice"]
for occ in sfx_occurrences:
    idx = unique_sfx_files.index(occ['sfx_file']) + 2
    label = f"a_sfx_{occ['scene']}_{occ['sfx_file'].replace(' ', '_').replace('.mp3', '')}"
    delay = occ['delay_ms']
    vol = occ['volume']
    filter_parts.append(
        f"[{idx}:a]volume={vol},adelay={delay}|{delay}[{label}]"
    )
    audio_labels.append(label)

n_inputs = len(audio_labels)
mix_str = "".join(f"[{l}]" for l in audio_labels)
filter_parts.append(f"{mix_str}amix=inputs={n_inputs}:duration=first:dropout_transition=0:normalize=0[a_out]")

filter_complex = ";".join(filter_parts)

# --- 8. Render final video with SFX ---
final_video = os.path.join(OUTPUT_DIR, "video_with_sfx.mp4")
cmd = ["ffmpeg"]
cmd.extend(inputs)
cmd.extend([
    "-filter_complex", filter_complex,
    "-map", "[v_out]",
    "-map", "[a_out]",
    "-c:v", "libx264", "-preset", "fast", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k",
    "-shortest",
    final_video, "-y"
])

print(f"\n[*] Rendering final video with {len(sfx_occurrences)} SFX...")
print(f"[*] Unique SFX files: {len(unique_sfx_files)}")
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if res.returncode != 0:
    print("Error:", res.stderr.decode('utf-8', errors='ignore')[:500])
else:
    print(f"\nSUCCESS! Final video with SFX: {final_video}")

print("\n[*] Done!")