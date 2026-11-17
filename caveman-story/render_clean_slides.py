import os
import subprocess
import shutil
import sys

base_dir = r"C:\File D\Stickman\caveman-story"
images_dir = os.path.join(base_dir, "images")
output_dir = os.path.join(base_dir, "output")
cache_dir = os.path.join(output_dir, "audio_cache")
os.makedirs(output_dir, exist_ok=True)
os.makedirs(cache_dir, exist_ok=True)

# Import parse_storyboard để đọc thời lượng và hiệu ứng từ kịch bản
sys.path.insert(0, os.path.join(base_dir, "..", "tools"))
try:
    from parse_storyboard import parse_storyboard
    storyboard_path = os.path.join(base_dir, "..", "Kịch bản loại người xuất hiện.txt")
    if os.path.exists(storyboard_path):
        storyboard_rows = parse_storyboard(storyboard_path)
        print(f"[*] Đã đọc {len(storyboard_rows)} cảnh từ kịch bản.")
    else:
        storyboard_rows = []
except Exception as e:
    print(f"[!] Không đọc được kịch bản: {e}")
    storyboard_rows = []

# Mapping từ loại cảnh sang hiệu ứng camera (zoom/pan/shake)
def get_camera_effect(loai_canh: str, dur: float) -> str:
    """Tra ve filter ffmpeg zoompan dua tren loai canh (hieu ung nhe, khong gay kho chiu)."""
    total_frames = int(round(dur * 30))
    loai_lower = (loai_canh or "").lower()
    import unicodedata
    loai_lower = unicodedata.normalize("NFD", loai_lower)
    loai_lower = "".join(c for c in loai_lower if unicodedata.category(c) != "Mn")
    
    if "zoom in" in loai_lower or "zoom vao" in loai_lower or "zoom nhanh" in loai_lower:
        return f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='min(zoom+0.0003,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1280x720:fps=30"
    elif "zoom out" in loai_lower:
        return f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='max(1.05-0.0003*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1280x720:fps=30"
    elif "pan may tu trai" in loai_lower or "pan tu trai" in loai_lower:
        return f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z=1.03:x='on*(iw*0.03/{total_frames})':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1280x720:fps=30"
    elif "pan may tu phai" in loai_lower or "pan tu phai" in loai_lower:
        return f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z=1.03:x='(1-on/{total_frames})*(iw*0.03)':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1280x720:fps=30"
    elif "pan may tu tren" in loai_lower or "pan tu tren" in loai_lower or "pan may tu duoi" in loai_lower:
        return f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z=1.03:x='iw/2-(iw/zoom/2)':y='(1-on/{total_frames})*(ih*0.03)':d={total_frames}:s=1280x720:fps=30"
    elif "giat nhe" in loai_lower or "impact shake" in loai_lower or "rung man hinh" in loai_lower:
        return f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='1.02':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1280x720:fps=30"
    elif "cutout" in loai_lower or "chia doi" in loai_lower or "split" in loai_lower:
        return f"scale=1280:720"
    else:
        # Mac dinh: zoom in nhe (khoang 3%)
        return f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='min(zoom+0.0002,1.03)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={total_frames}:s=1280x720:fps=30"
    
# Tạo danh sách shots từ kịch bản (nếu có), nếu không dùng mặc định
shots = []
if storyboard_rows:
    for row in storyboard_rows:
        try:
            stt = int(str(row.get("stt", "0")).strip().strip("*"))
            img_name = f"{stt}.png"
            # Đọc thời lượng từ storyboard
            dur_str = row.get("thoi_luong", "3.0s")
            dur = float(str(dur_str).replace("s", "").strip())
            loai_canh = row.get("loai_canh", "")
            shots.append({"img": img_name, "dur": dur, "mode": loai_canh})
        except (ValueError, TypeError):
            continue
    print(f"[*] Đã tạo {len(shots)} shots từ kịch bản.")
else:
    # Fallback: dùng 10 shots mặc định
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
    print(f"[*] Dùng {len(shots)} shots mặc định.")

# 1. Render clips với hiệu ứng camera (zoom/pan/shake)
clean_clips = []
for i, shot in enumerate(shots):
    img_path = os.path.join(images_dir, shot["img"])
    if not os.path.exists(img_path):
        print(f"[!] Bỏ qua cảnh {i+1}: không tìm thấy {shot['img']}")
        continue
    clip_path = os.path.join(output_dir, f"clean_clip_{i+1}.mp4")
    dur = shot["dur"]
    loai_canh = shot.get("mode", "")
    
    # Lấy hiệu ứng camera dựa trên loại cảnh
    vf = get_camera_effect(loai_canh, dur)
    
    cmd = [
        "ffmpeg", "-loop", "1", "-i", img_path,
        "-vf", vf,
        "-t", str(dur),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", "30",
        clip_path, "-y"
    ]
    print(f"[*] Render cảnh {i+1}/{len(shots)} ({dur}s) - {loai_canh[:50]}...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        print(f"[!] Lỗi render cảnh {i+1}: {res.stderr.decode('utf-8', errors='ignore')[:200]}")
        continue
    clean_clips.append(clip_path)

if not clean_clips:
    print("[LỖI] Không render được clip nào!")
    sys.exit(1)

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
print(f"[*] Đã concat {len(clean_clips)} clips.")

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

voice_file = os.path.join(base_dir, "Chương 1.wav")
ass_path = os.path.join(output_dir, "captions.ass")
final_video = os.path.join(output_dir, "video_chuong1_anh_tinh_cat_canh.mp4")

# Tạo ASS subtitles từ aligned_captions.json nếu có
aligned_caps_path = os.path.join(base_dir, "aligned_captions.json")
if os.path.exists(aligned_caps_path):
    import json
    with open(aligned_caps_path, "r", encoding="utf-8") as f:
        captions = json.load(f)
    
    def format_ass_time(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        return f"{h:d}:{m:02d}:{s:05.2f}"
    
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
    print(f"[*] Đã tạo ASS subtitles từ aligned_captions.json ({len(captions)} đoạn)")

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

print("Rendering clean video with camera effects + audio + subtitles...")
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if res.returncode != 0:
    print("Error:", res.stderr.decode('utf-8', errors='ignore')[:500])
else:
    print("SUCCESS! Created:", final_video)