import os
import sys
import subprocess
import json
import re
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from parse_storyboard import parse_storyboard

BASE_DIR = r"C:\File D\Stickman"
STORY_DIR = os.path.join(BASE_DIR, "caveman-story")
IMAGES_DIR = os.path.join(STORY_DIR, "images")
SOUNDS_DIR = os.path.join(STORY_DIR, "sounds")
OUTPUT_DIR = os.path.join(STORY_DIR, "output")
AUDIO_FILE = os.path.join(STORY_DIR, "Chương 1.wav")
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, "VIDEO_TEST_CHUONG_1.mp4")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Anh xa ten SFX chuan (v5.2) -> ten file thuc te trong thu muc sounds/
SFX_FILES = {
    "pop.mp3": "pop.mp3",
    "fast_whoosh.mp3": "Fast Whoosh.mp3",
    "wrong_answer_buzzer.mp3": "Wrong answer buzzer.mp3",
    "record_scratch.mp3": "Record Scratch.mp3",
    "ding.mp3": "ding.mp3",
    "dramatic_boom.mp3": "Dramatic Boom.mp3",
    "cartoon_punch.mp3": "Cartoon Punch.mp3",
    "tada.mp3": "Tada.mp3",
    "whoosh_slow.mp3": "Whoosh Transition.mp3",
    "sparkle.mp3": "sparkle.mp3",
    "gasp.mp3": "gasp.mp3",
    "fire_crackle.mp3": "Fire Crackle.mp3",
    "thunder.mp3": "Thunder.mp3",
    "heartbeat.mp3": "Heartbeat.mp3",
    "explosion.mp3": "Explosion.mp3",
    "water_splash.mp3": "Water Splash.mp3",
    "wind.mp3": "Wind.mp3",
    "crickets.mp3": "Crickets.mp3",
    "glitch.mp3": "glitch.mp3",
}

# 1. Parse Script tu bang v5.2 (ho tro khoang canh qua --from/--to)
def find_default_script():
    candidates = [
        os.path.join(BASE_DIR, "Kịch bản_chuong1.txt"),
        os.path.join(BASE_DIR, "Kịch bản loại người xuất hiện.txt"),
        os.path.join(BASE_DIR, "Kịch bản thử v5.2.txt"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return candidates[0]

parser = argparse.ArgumentParser()
parser.add_argument("--script", type=str, default=None, help="Duong dan file kich ban v5.2/v5.3")
parser.add_argument("--from", type=int, default=1, dest="start_stt", help="STT bat dau")
parser.add_argument("--to", type=int, default=99999, dest="end_stt", help="STT ket thuc")
parser.add_argument("--no-sfx", action="store_true", help="Tat SFX")
args, _ = parser.parse_known_args()

script_file = args.script or find_default_script()
print(f"[*] Dang doc kich ban tu: {script_file}")
rows = parse_storyboard(script_file)
shots = []
for row in rows:
    try:
        stt = int(row.get("stt", "0").strip("*"))
    except Exception:
        continue
    if not (args.start_stt <= stt <= args.end_stt):
        continue

    try:
        dur = float(row.get("thoi_luong", "3.0"))
    except Exception:
        dur = 3.0

    text = row.get("loi_thoai", "")
    words = len(text.split())

    ten_sfx_raw = row.get("ten_sfx", "none").strip()
    ten_sfx = SFX_FILES.get(ten_sfx_raw, ten_sfx_raw if ten_sfx_raw != "none" else "none")

    tu_neo = row.get("tu_neo", "-").strip()
    vi_tri = row.get("vi_tri_sfx", "-").strip()

    shots.append({
        "stt": stt,
        "planned_dur": dur,
        "words": words,
        "text": text,
        "loai": row.get("loai_canh", ""),
        "ten_sfx": ten_sfx if ten_sfx_raw != "none" else None,
        "tu_neo": tu_neo if tu_neo != "-" else "",
        "vi_tri": vi_tri if vi_tri != "-" else "",
    })

shots.sort(key=lambda x: x["stt"])

# 2. Get exact Audio Duration
cmd_dur = [
    "ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1", AUDIO_FILE
]
audio_dur = float(subprocess.check_output(cmd_dur).decode().strip())
print(f"[*] Thoi luong audio Chuong 1: {audio_dur:.2f}s")

# 3. Calculate dynamic duration and SNAP TO NATURAL SILENCES
import re
print("[*] Dang phan tich cac khoang ngung nghi tu nhien trong giong doc...")
cmd_silence = [
    'ffmpeg', '-i', AUDIO_FILE,
    '-af', 'silencedetect=noise=-28dB:d=0.2',
    '-f', 'null', '-'
]
res_silence = subprocess.run(cmd_silence, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', res_silence.stderr)]
ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', res_silence.stderr)]
silence_midpoints = [(s + e) / 2 for s, e in zip(starts, ends)]
print(f"[*] Tim thay {len(silence_midpoints)} diem ngung nghi trong audio!")

total_planned_dur = sum(s["planned_dur"] for s in shots)
total_words = sum(s["words"] for s in shots)

# Uoc tinh thoi diem ket thuc theo so tu
cum_time = 0.0
for s in shots:
    w = 0.7 * (s["words"] / total_words) + 0.3 * (s["planned_dur"] / total_planned_dur)
    cum_time += w * audio_dur
    s["est_end"] = cum_time

# Khoa diem chuyen anh vao dung khoang lang (khong bao gio bi cat loi thoai giua chung)
last_boundary = 0.0
for i, s in enumerate(shots[:-1]):
    target = s["est_end"]
    # Tim diem ngung cach bien truoc it nhat 1.2s va gan moc muc tieu
    candidates = [m for m in silence_midpoints if m > last_boundary + 1.2 and abs(m - target) < 2.8]
    if candidates:
        # Uu tien khoang lang ngay sau khi cau noi vua dut (m >= target - 0.2)
        best = min(candidates, key=lambda m: abs(m - target) if m >= target - 0.2 else abs(m - target) + 1.2)
        s["end"] = round(best, 2)
    else:
        s["end"] = round(target, 2)
    
    s["start"] = round(last_boundary, 2)
    s["dur"] = round(s["end"] - s["start"], 2)
    last_boundary = s["end"]

shots[-1]["start"] = round(last_boundary, 2)
shots[-1]["end"] = round(audio_dur, 2)
shots[-1]["dur"] = round(audio_dur - last_boundary, 2)

for s in shots:
    print(f"  Canh {s['stt']:02d}: {s['start']:5.1f}s -> {s['end']:5.1f}s ({s['dur']:4.1f}s)")

# 4. Generate SRT Subtitles
SRT_FILE = os.path.join(OUTPUT_DIR, "subtitles_chuong_1.srt")
def format_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

with open(SRT_FILE, "w", encoding="utf-8") as f:
    for i, s in enumerate(shots):
        f.write(f"{i+1}\n")
        f.write(f"{format_srt_time(s['start'])} --> {format_srt_time(s['end'])}\n")
        f.write(f"{s['text']}\n\n")

print(f"[*] Da tao file phu de: {SRT_FILE}")

# 5. Create Concat Input List for Images
CONCAT_FILE = os.path.join(OUTPUT_DIR, "images_concat.txt")
with open(CONCAT_FILE, "w", encoding="utf-8") as f:
    for s in shots:
        img_path = os.path.join(IMAGES_DIR, f"{s['stt']}.png")
        if not os.path.exists(img_path):
            print(f"[!] Canh bao: Khong tim thay {img_path}")
        f.write(f"file '{img_path.replace(chr(92), '/')}'\n")
        f.write(f"duration {s['dur']}\n")
    # FFmpeg concat requires last image to be listed again without duration
    last_img = os.path.join(IMAGES_DIR, f"{shots[-1]['stt']}.png")
    f.write(f"file '{last_img.replace(chr(92), '/')}'\n")

# 6. Smart Dynamic SFX Sound Effects (doc tu bang v5.2, neo theo tu)
ENABLE_SFX = not args.no_sfx

def _offset_from_vi_tri(vi_tri: str, dur: float) -> float:
    """Chuyen vi tri chen (truoc/sau/dau canh) thanh offset giay trong canh."""
    v = vi_tri.lower()
    if v == "dau canh" or v == "dau":
        return 0.0
    if v == "sau":
        return dur * 0.85
    if v == "truoc":
        return dur * 0.15
    return dur * 0.5

valid_sfx = []
if ENABLE_SFX:
    for s in shots:
        ten_sfx = s.get("ten_sfx")
        if not ten_sfx:
            continue
        sfx_path = os.path.join(SOUNDS_DIR, ten_sfx)
        if not os.path.exists(sfx_path):
            print(f"[!] Khong tim thay SFX: {sfx_path}")
            continue
        dur = s.get("dur", s.get("planned_dur", 3.0))
        offset_seconds = _offset_from_vi_tri(s.get("vi_tri", ""), dur)
        exact_time_s = s["start"] + offset_seconds
        valid_sfx.append({
            "stt": s["stt"],
            "file": ten_sfx,
            "time_ms": int(exact_time_s * 1000),
            "exact_time_s": exact_time_s,
            "path": sfx_path,
            "vol": 0.45,
            "tu_neo": s.get("tu_neo", "")
        })

print(f"[*] Che do SFX: {'BAT' if ENABLE_SFX else 'TAT HOAN TOAN (Video sach chi co Hinh + Giong to ro)'}")

# Build FFmpeg command
filter_complex = []
input_args = ["-f", "concat", "-safe", "0", "-i", CONCAT_FILE, "-i", AUDIO_FILE]

for i, sfx in enumerate(valid_sfx):
    input_args.extend(["-i", sfx["path"]])
    idx = i + 2
    filter_complex.append(f"[{idx}:a]adelay={sfx['time_ms']}|{sfx['time_ms']},volume={sfx['vol']}[sfx{i}];")

if valid_sfx:
    mix_inputs = "".join(f"[sfx{i}]" for i in range(len(valid_sfx)))
    filter_complex.append(f"[1:a]volume=1.85,alimiter=limit=0.95[vocal];[vocal]{mix_inputs}amix=inputs={len(valid_sfx)+1}:duration=first:normalize=0[aout]")
    audio_map = "[aout]"
else:
    filter_complex.append("[1:a]volume=1.85,alimiter=limit=0.95[vocal]")
    audio_map = "[vocal]"

# Bo hoan toan phu de theo yeu cau cua nguoi dung, chi giu video sach Full HD
video_filter = "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black"

filter_str = "".join(filter_complex)

cmd = ["ffmpeg", "-y"] + input_args
if filter_str:
    cmd.extend(["-filter_complex", f"{filter_str};[0:v]{video_filter}[vout]", "-map", "[vout]", "-map", audio_map])
else:
    cmd.extend(["-vf", video_filter, "-map", "0:v", "-map", audio_map])

cmd.extend([
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
    "-c:a", "aac", "-b:a", "192k",
    "-t", str(audio_dur),
    OUTPUT_VIDEO
])

subprocess.run(cmd, check=True)
print(f"\n[THANH CONG 100%] Video Chuong 1 (am thanh to ro, sach phu de) da render xong tai:\n{OUTPUT_VIDEO}")
