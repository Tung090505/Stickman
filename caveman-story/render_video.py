import os
import subprocess
import json

base_dir = r"C:\File D\Stickman\caveman-story"
images_dir = os.path.join(base_dir, "images")
output_dir = os.path.join(base_dir, "output")
os.makedirs(output_dir, exist_ok=True)

# 1. Shot definitions
shots = [
    {"img": "1.png", "dur": 6.8, "mode": "zoom_in"},
    {"img": "2.png", "dur": 7.2, "mode": "zoom_out"},
    {"img": "3.png", "dur": 6.0, "mode": "pan_right"},
    {"img": "4.png", "dur": 6.4, "mode": "zoom_in"},
    {"img": "5.png", "dur": 3.9, "mode": "pan_up"},
    {"img": "6.png", "dur": 6.2, "mode": "zoom_in"},
    {"img": "7.png", "dur": 7.0, "mode": "zoom_in"},
    {"img": "8.png", "dur": 8.5, "mode": "pan_left"},
    {"img": "9.png", "dur": 12.2, "mode": "zoom_in"},
    {"img": "10.png", "dur": 10.55, "mode": "zoom_in"}
]

# 2. Captions from project.json
with open(os.path.join(base_dir, "project.json"), "r", encoding="utf-8") as f:
    project_data = json.load(f)

captions = project_data.get("captions", [])

# Convert captions to ASS format
def format_ass_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"

ass_path = os.path.join(output_dir, "captions.ass")
with open(ass_path, "w", encoding="utf-8") as f:
    f.write("""[Script Info]
Title: Caveman Story Chapter 1
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,36,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1.5,2,20,20,45,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")
    for cap in captions:
        st = format_ass_time(cap["start"])
        et = format_ass_time(cap["end"])
        txt = cap["text"].replace("\n", "\\N")
        f.write(f"Dialogue: 0,{st},{et},Default,,0,0,0,,{txt}\n")

print(f"Generated ASS subtitles at {ass_path}")

# 3. Render individual clips
clip_files = []
for i, shot in enumerate(shots):
    img_path = os.path.join(images_dir, shot["img"])
    clip_path = os.path.join(output_dir, f"clip_{i+1}.mp4")
    dur = shot["dur"]
    total_frames = int(round(dur * 30))
    mode = shot["mode"]

    if mode == "zoom_in":
        vf = f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='min(zoom+0.0008,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1280x720:fps=30"
    elif mode == "zoom_out":
        vf = f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='max(1.15-0.0008*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1280x720:fps=30"
    elif mode == "pan_right":
        vf = f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z=1.12:x='on*(iw*0.1/{total_frames})':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1280x720:fps=30"
    elif mode == "pan_left":
        vf = f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z=1.12:x='(1-on/{total_frames})*(iw*0.1)':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1280x720:fps=30"
    elif mode == "pan_up":
        vf = f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z=1.12:x='iw/2-(iw/zoom/2)':y='(1-on/{total_frames})*(ih*0.1)':d={total_frames}:s=1280x720:fps=30"
    else:
        vf = f"scale=1280:720,zoompan=z='min(zoom+0.0008,1.12)':d={total_frames}:s=1280x720:fps=30"

    cmd = [
        "ffmpeg", "-loop", "1", "-i", img_path,
        "-vf", vf,
        "-t", str(dur),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        clip_path, "-y"
    ]
    print(f"Rendering shot {i+1}/{len(shots)} ({dur}s)...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        print(f"Error rendering shot {i+1}:", res.stderr.decode('utf-8', errors='ignore'))
        break
    clip_files.append(clip_path)

print(f"All {len(clip_files)} shots rendered successfully!")

# 4. Concat all clips
concat_list_path = os.path.join(output_dir, "concat_list.txt")
with open(concat_list_path, "w", encoding="utf-8") as f:
    for clip in clip_files:
        f.write(f"file '{clip}'\n")

raw_video = os.path.join(output_dir, "video_raw.mp4")
subprocess.run([
    "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_list_path,
    "-c", "copy", raw_video, "-y"
], check=True)
print("Concatenated raw video done.")

# 5. Merge audio and burn subtitles
audio_file = os.path.join(base_dir, "chuong1.wav")
final_video = os.path.join(output_dir, "video_chuong1_hoan_chinh.mp4")

# Note: In Windows ffmpeg, colon in path must be escaped for ass filter: C\:/...
ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")
vf_sub = f"ass='{ass_escaped}'"

print("Burning subtitles and merging audio...")
cmd_final = [
    "ffmpeg", "-i", raw_video, "-i", audio_file,
    "-vf", vf_sub,
    "-c:v", "libx264", "-preset", "fast", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k",
    "-shortest",
    final_video, "-y"
]
res = subprocess.run(cmd_final, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if res.returncode != 0:
    print("Error in final render:", res.stderr.decode('utf-8', errors='ignore'))
else:
    print(f"SUCCESS! Final video created at: {final_video}")
