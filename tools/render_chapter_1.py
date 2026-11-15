import os
import subprocess
import json

BASE_DIR = r"C:\File D\Stickman"
STORY_DIR = os.path.join(BASE_DIR, "caveman-story")
IMAGES_DIR = os.path.join(STORY_DIR, "images")
SOUNDS_DIR = os.path.join(STORY_DIR, "sounds")
OUTPUT_DIR = os.path.join(STORY_DIR, "output")
AUDIO_FILE = os.path.join(STORY_DIR, "Chương 1.wav")
OUTPUT_VIDEO = os.path.join(OUTPUT_DIR, "VIDEO_TEST_CHUONG_1.mp4")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Parse Script for Chapter 1 (Shots 1 to 35)
SCRIPT_PATH = os.path.join(BASE_DIR, "Kịch bản loại người xuất hiện.txt")
shots = []
with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip().startswith("| **") and len(line.split("|")) >= 8:
            p = [x.strip() for x in line.split("|")]
            stt = int(p[1].replace("*", ""))
            if stt <= 35:
                t = p[2].replace("s", "").split("-")
                dur = float(t[1].strip()) - float(t[0].strip())
                words = len(p[4].split())
                shots.append({
                    "stt": stt,
                    "planned_dur": dur,
                    "words": words,
                    "text": p[4],
                    "loai": p[3]
                })

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
    print(f"  Cảnh {s['stt']:02d}: {s['start']:5.1f}s -> {s['end']:5.1f}s ({s['dur']:4.1f}s)")

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

# 6. Smart Dynamic SFX Sound Effects (Chon loc dung diem cham gay cuoi / nhan manh)
# Moi cue co offset_ratio: Ty le thoi gian trong canh (0.0: dau cau, 0.5: giua cau, 0.8: cuoi cau)
sfx_cues = [
    # Cảnh 02: Tua ngược về 6 triệu năm trước
    {"stt": 2, "file": "Time rewind whoosh.mp3", "vol": 0.45, "offset_ratio": 0.15},
    # Cảnh 04: Không deadline dí (Dấu X đỏ)
    {"stt": 4, "file": "buzzer.mp3", "vol": 0.35, "offset_ratio": 0.30},
    # Cảnh 05: Không hóa đơn tiền nhà (Dấu X đỏ)
    {"stt": 5, "file": "Wrong answer buzzer.mp3", "vol": 0.35, "offset_ratio": 0.30},
    # Cảnh 07: Trái Đất bỗng đổi tính (Đột ngột, kịch tính)
    {"stt": 7, "file": "Dramatic Sub Boom.mp3", "vol": 0.45, "offset_ratio": 0.45},
    # Cảnh 10: Ở trên cây thì chết đói (Thất vọng não nề)
    {"stt": 10, "file": "Sad Trombone.mp3", "vol": 0.40, "offset_ratio": 0.40},
    # Cảnh 12: Dưới bãi cỏ là con hổ răng kiếm 300 cân
    {"stt": 12, "file": "heartbeat.mp3", "vol": 0.45, "offset_ratio": 0.30},
    # Cảnh 16: Grok thử duỗi thẳng lưng và ĐỨNG DẬY!
    {"stt": 16, "file": "ding.mp3", "vol": 0.45, "offset_ratio": 0.65},
    # Cảnh 18: Đứng thẳng thì... ôi thôi ĐAU CÁI LƯNG! (Tiếng rắc xương cột sống)
    {"stt": 18, "file": "Bone Crack.mp3", "vol": 0.50, "offset_ratio": 0.70},
    # Cảnh 19: Làm gì có Salonpas (Dấu X đỏ)
    {"stt": 19, "file": "buzzer.mp3", "vol": 0.35, "offset_ratio": 0.30},
    # Cảnh 20: Đôi tay ĐÃ ĐƯỢC GIẢI PHÓNG! (Tada hân hoan)
    {"stt": 20, "file": "Tada.mp3", "vol": 0.45, "offset_ratio": 0.40},
    # Cảnh 23: Đập mạnh hai hòn đá... BỐP!
    {"stt": 23, "file": "Cartoon Punch.mp3", "vol": 0.50, "offset_ratio": 0.80},
    # Cảnh 24: Công cụ đầu tiên của loài người (Lóe sáng)
    {"stt": 24, "file": "ding.mp3", "vol": 0.45, "offset_ratio": 0.50},
    # Cảnh 25: Quên dao bếp Nhật đi (Dấu X đỏ)
    {"stt": 25, "file": "buzzer.mp3", "vol": 0.35, "offset_ratio": 0.30},
    # Cảnh 26: Săn thú to ư? Mơ đi cưng! (Tiếng kẹt đĩa phá đám)
    {"stt": 26, "file": "Record Scratch.mp3", "vol": 0.45, "offset_ratio": 0.65},
    # Cảnh 31: RẮC! Ống xương nứt toác, lộ tủy xương (Tiếng gãy xương rắc)
    {"stt": 31, "file": "Bone Crack.mp3", "vol": 0.50, "offset_ratio": 0.15},
    # Cảnh 33: Không cần sữa bột DHA (Dấu X đỏ)
    {"stt": 33, "file": "buzzer.mp3", "vol": 0.35, "offset_ratio": 0.30},
    # Cảnh 35: Bước ngoặt vĩ đại nhất: NGỌN LỬA! (Bùng cháy / sấm sét)
    {"stt": 35, "file": "thunder.mp3", "vol": 0.45, "offset_ratio": 0.65},
]

# Bat/tat SFX: Nguoi dung yeu cau tap trung vao giong doc sach va hinh anh
ENABLE_SFX = False

valid_sfx = []
if ENABLE_SFX:
    for cue in sfx_cues:
        sfx_path = os.path.join(SOUNDS_DIR, cue["file"])
        if os.path.exists(sfx_path):
            shot_info = next((s for s in shots if s["stt"] == cue["stt"]), None)
            if shot_info:
                offset_seconds = shot_info["dur"] * cue.get("offset_ratio", 0.0)
                exact_time_s = shot_info["start"] + offset_seconds
                valid_sfx.append({
                    "stt": cue["stt"],
                    "file": cue["file"],
                    "time_ms": int(exact_time_s * 1000),
                    "exact_time_s": exact_time_s,
                    "path": sfx_path,
                    "vol": cue.get("vol", 0.4)
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
