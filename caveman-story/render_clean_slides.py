import os
import subprocess
import shutil

base_dir = r"C:\File D\Stickman\caveman-story"
images_dir = os.path.join(base_dir, "images")
output_dir = os.path.join(base_dir, "output")
cache_dir = os.path.join(output_dir, "audio_cache")
os.makedirs(output_dir, exist_ok=True)
os.makedirs(cache_dir, exist_ok=True)

# 10 Shots durations (exactly matching Chapter 1)
shots = [
    {"img": "1.png", "dur": 6.8},
    {"img": "2.png", "dur": 7.2},
    {"img": "3.png", "dur": 6.0},
    {"img": "4.png", "dur": 6.4},
    {"img": "5.png", "dur": 3.9},
    {"img": "6.png", "dur": 6.2},
    {"img": "7.png", "dur": 7.0},
    {"img": "8.png", "dur": 8.5},
    {"img": "9.png", "dur": 12.2},
    {"img": "10.png", "dur": 10.55}
]

# 1. Render clean, crisp static clips (NO zoompan, NO cheesy motion)
clean_clips = []
for i, shot in enumerate(shots):
    img_path = os.path.join(images_dir, shot["img"])
    clip_path = os.path.join(output_dir, f"clean_clip_{i+1}.mp4")
    dur = shot["dur"]
    
    # Scale crisply to 1280x720 without any zooming/panning
    vf = "scale=1280:720"
    
    cmd = [
        "ffmpeg", "-loop", "1", "-i", img_path,
        "-vf", vf,
        "-t", str(dur),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", "30",
        clip_path, "-y"
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    clean_clips.append(clip_path)

# 2. Concat into raw clean video
concat_txt = os.path.join(output_dir, "clean_concat.txt")
with open(concat_txt, "w", encoding="utf-8") as f:
    for c in clean_clips:
        f.write(f"file '{c}'\n")

clean_raw = os.path.join(output_dir, "clean_video_raw.mp4")
subprocess.run([
    "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_txt,
    "-c", "copy", clean_raw, "-y"
], check=True)

# 3. Sound files
sound_map = {
    "Ding.mp3": "ding.mp3",
    "pop.mp3": "pop.mp3",
    "Tiếng dế.mp3": "crickets.mp3",
    "Tiếng gió.mp3": "wind.mp3",
    "Tiếng lửa.mp3": "fire.mp3",
    "Tiếng sấm.mp3": "thunder.mp3",
    "Tiếng tim đập.mp3": "heartbeat.mp3"
}
sounds_dir = os.path.join(base_dir, "sounds")
for orig, clean in sound_map.items():
    src = os.path.join(sounds_dir, orig)
    dst = os.path.join(cache_dir, clean)
    if os.path.exists(src):
        shutil.copy2(src, dst)

voice_file = os.path.join(base_dir, "chuong1.wav")
ass_path = os.path.join(output_dir, "captions.ass")
final_video = os.path.join(output_dir, "video_chuong1_anh_tinh_cat_canh.mp4")

ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")

filter_complex = (
    f"[0:v]ass='{ass_escaped}'[v_out];"
    "[1:a]volume=1.0[a_voice];"
    "[2:a]atrim=0:21.5,afade=t=in:st=0:d=1.5,afade=t=out:st=19.5:d=2.0,volume=0.20,adelay=5000|5000[a_crickets];"
    "[3:a]volume=0.35,adelay=6800|6800[a_pop1];"
    "[3:a]volume=0.35,adelay=8000|8000[a_pop2];"
    "[4:a]afade=t=in:st=0:d=1.0,afade=t=out:st=6.5:d=1.5,volume=0.45,adelay=17000|17000[a_heart];"
    "[5:a]atrim=0:13.0,afade=t=in:st=0:d=1.5,afade=t=out:st=11.0:d=2.0,volume=0.30,adelay=30000|30000[a_wind];"
    "[6:a]volume=0.45,adelay=61500|61500[a_ding];"
    "[7:a]volume=0.90,adelay=70000|70000[a_thunder];"
    "[8:a]atrim=0:3.55,afade=t=in:st=0:d=0.5,afade=t=out:st=2.5:d=1.0,volume=0.45,adelay=71200|71200[a_fire];"
    "[a_voice][a_crickets][a_pop1][a_pop2][a_heart][a_wind][a_ding][a_thunder][a_fire]amix=inputs=9:duration=first:dropout_transition=0:normalize=0[a_out]"
)

cmd = [
    "ffmpeg",
    "-i", clean_raw,
    "-i", voice_file,
    "-i", os.path.join(cache_dir, "crickets.mp3"),
    "-i", os.path.join(cache_dir, "pop.mp3"),
    "-i", os.path.join(cache_dir, "heartbeat.mp3"),
    "-i", os.path.join(cache_dir, "wind.mp3"),
    "-i", os.path.join(cache_dir, "ding.mp3"),
    "-i", os.path.join(cache_dir, "thunder.mp3"),
    "-i", os.path.join(cache_dir, "fire.mp3"),
    "-filter_complex", filter_complex,
    "-map", "[v_out]",
    "-map", "[a_out]",
    "-c:v", "libx264", "-preset", "fast", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k",
    final_video, "-y"
]

print("Rendering clean static cut video...")
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if res.returncode != 0:
    print("Error:", res.stderr.decode('utf-8', errors='ignore'))
else:
    print("SUCCESS! Created:", final_video)
