import os
import sys
import subprocess
import json

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

base_dir = r"C:\File D\Stickman\caveman-story"
images_dir = os.path.join(base_dir, "images")
output_dir = os.path.join(base_dir, "output")
os.makedirs(output_dir, exist_ok=True)

# 1. Shot definitions - doc tu kich ban neu co
sys.path.insert(0, os.path.join(base_dir, "..", "tools"))
try:
    from parse_storyboard import parse_storyboard
    storyboard_path = os.path.join(base_dir, "..", "Kịch bản loại người xuất hiện.txt")
    if os.path.exists(storyboard_path):
        storyboard_rows = parse_storyboard(storyboard_path)
        shots = []
        for row in storyboard_rows:
            try:
                stt = int(str(row.get("stt", "0")).strip().strip("*"))
                img_name = f"{stt}.png"
                dur_str = row.get("thoi_luong", "3.0s")
                dur = float(str(dur_str).replace("s", "").strip())
                shots.append({"img": img_name, "dur": dur})
            except (ValueError, TypeError):
                continue
        print(f"[*] Đã tạo {len(shots)} shots từ kịch bản.")
    else:
        shots = [{"img": "1.png", "dur": 3.0}]
        print(f"[*] Dùng {len(shots)} shots mặc định.")
except Exception as e:
    print(f"[!] Không đọc được kịch bản: {e}")
    shots = [{"img": "1.png", "dur": 3.0}]

# 2. Render individual clips (KHONG hieu ung, KHONG phu de)
clip_files = []
for i, shot in enumerate(shots):
    img_path = os.path.join(images_dir, shot["img"])
    if not os.path.exists(img_path):
        print(f"[!] Bỏ qua cảnh {i+1}: không tìm thấy {shot['img']}")
        continue
    clip_path = os.path.join(output_dir, f"clip_{i+1}.mp4")
    dur = shot["dur"]

    # Chi scale, khong zoom/pan/shake
    vf = "scale=1280:720"

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
        print(f"Error rendering shot {i+1}:", res.stderr.decode('utf-8', errors='ignore')[:200])
        continue
    clip_files.append(clip_path)

print(f"All {len(clip_files)} shots rendered successfully!")

# 3. Concat all clips
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

# 4. Merge audio (KHONG phu de)
audio_file = os.path.join(base_dir, "Chương 1.wav")
final_video = os.path.join(output_dir, "video_chuong1_hoan_chinh.mp4")

print("Merging audio (no subtitles)...")
cmd_final = [
    "ffmpeg", "-i", raw_video, "-i", audio_file,
    "-c:v", "libx264", "-preset", "fast", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k",
    "-shortest",
    final_video, "-y"
]
res = subprocess.run(cmd_final, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if res.returncode != 0:
    print("Error in final render:", res.stderr.decode('utf-8', errors='ignore')[:500])
else:
    print(f"SUCCESS! Final video created at: {final_video}")