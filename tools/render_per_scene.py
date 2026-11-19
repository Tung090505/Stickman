import os, sys, subprocess

BASE_DIR = r"C:\File D\Stickman"
STORY_DIR = os.path.join(BASE_DIR, "caveman-story")
IMAGES_DIR = os.path.join(STORY_DIR, "images")
SCENE_AUDIO_DIR = os.path.join(STORY_DIR, "scene_audio")
OUTPUT_DIR = os.path.join(STORY_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 1. Render each scene: image + audio -> clip ---
clip_files = []
scene_count = 0
for stt in range(1, 51):
    img_path = os.path.join(IMAGES_DIR, f"{stt}.png")
    audio_path = os.path.join(SCENE_AUDIO_DIR, f"scene_{stt:03d}.wav")
    clip_path = os.path.join(OUTPUT_DIR, f"clip_{stt:03d}.mp4")

    if not os.path.exists(img_path):
        print(f"[!] Skip scene {stt}: image not found")
        continue
    if not os.path.exists(audio_path):
        print(f"[!] Skip scene {stt}: audio not found")
        continue

    scene_count += 1
    print(f"Rendering scene {scene_count} (STT {stt})...")

    # Render: image + audio -> clip (duration = audio duration)
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", img_path,
        "-i", audio_path,
        "-vf", "scale=1280:720",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p", "-r", "30",
        "-shortest",  # Duration = shortest input (audio)
        clip_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        print(f"  [!] Error: {res.stderr.decode('utf-8', errors='ignore')[:100]}")
        continue
    clip_files.append(clip_path)

print(f"\n[*] Rendered {len(clip_files)} clips")

# --- 2. Concat all clips -> final video ---
concat_list = os.path.join(OUTPUT_DIR, "concat_list.txt")
with open(concat_list, "w", encoding="utf-8") as f:
    for clip in clip_files:
        f.write(f"file '{clip}'\n")

final_video = os.path.join(OUTPUT_DIR, "video_per_scene.mp4")
subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", concat_list,
    "-c", "copy",
    final_video
], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(f"[*] Concatenated: {final_video}")

# --- 3. Verify ---
res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                      '-of', 'default=noprint_wrappers=1:nokey=1', final_video],
                     capture_output=True, text=True)
print(f"Video duration: {float(res.stdout.strip()):.2f}s")

# Also check audio
audio_res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                            '-of', 'default=noprint_wrappers=1:nokey=1', os.path.join(STORY_DIR, "Chương 1.wav")],
                           capture_output=True, text=True)
if os.path.exists(os.path.join(STORY_DIR, "Chương 1.wav")):
    print(f"Audio duration: {float(audio_res.stdout.strip()):.2f}s")

print("\nSUCCESS! Video created:", final_video)