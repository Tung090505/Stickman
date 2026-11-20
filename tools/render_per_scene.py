import os, sys, subprocess
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = r"C:\File D\Stickman"
STORY_DIR = os.path.join(BASE_DIR, "caveman-story")
IMAGES_DIR = os.path.join(STORY_DIR, "images")
SCENE_AUDIO_DIR = os.path.join(STORY_DIR, "scene_audio")
OUTPUT_DIR = os.path.join(STORY_DIR, "output")
FONT_PATH = "C:/Windows/Fonts/segoeuib.ttf"
STORYBOARD_PATH = os.path.join(BASE_DIR, "Kịch bản loại người xuất hiện.txt")
os.makedirs(OUTPUT_DIR, exist_ok=True)

import re

# --- Parse storyboard for text_capcut ---
text_capcut_map = {}
try:
    sys.path.insert(0, os.path.join(BASE_DIR, "tools"))
    from parse_storyboard import parse_storyboard
    if os.path.exists(STORYBOARD_PATH):
        rows = parse_storyboard(STORYBOARD_PATH)
        for row in rows:
            try:
                stt = int(str(row.get("stt", "0")).strip().strip("*"))
                tc = str(row.get("text_capcut", "")).strip()
                if tc and tc not in ("—", "-", "N/A", ""):
                    # Only show text for difficult terms: Latin letters (3+ chars) or numbers
                    if re.search(r'[A-Za-z]{3,}|\d', tc):
                        text_capcut_map[stt] = tc
            except (ValueError, TypeError):
                continue
        print(f"[*] Loaded text_capcut for {len(text_capcut_map)} scenes (filtered)")
except Exception as e:
    print(f"[!] Could not load storyboard: {e}")

def create_box_image(text):
    """Create rounded rectangle box background (no text) using PIL."""
    font = ImageFont.truetype(FONT_PATH, 44)
    # Measure text
    dummy = Image.new('RGBA', (1, 1))
    d = ImageDraw.Draw(dummy)
    bbox = d.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    padding_x, padding_y = 30, 3
    border_radius = 8
    border_width = 2
    shadow_offset = 3
    box_w = text_w + padding_x * 2
    box_h = text_h + padding_y * 2
    total_w = box_w + shadow_offset + border_width * 2 + 4
    total_h = box_h + shadow_offset + border_width * 2 + 4

    box_img = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(box_img)

    # Shadow
    draw.rounded_rectangle(
        (border_width + 2, border_width + 2 + shadow_offset,
         border_width + 2 + box_w, border_width + 2 + shadow_offset + box_h),
        radius=border_radius, fill=(0, 0, 0, 40))

    # Border (dark gray)
    draw.rounded_rectangle(
        (border_width, border_width, border_width + box_w, border_width + box_h),
        radius=border_radius, fill=(34, 34, 34, 255))

    # Inner (cream background #FAF0DC)
    draw.rounded_rectangle(
        (border_width + border_width, border_width + border_width,
         border_width + box_w - border_width, border_width + box_h - border_width),
        radius=border_radius - 1, fill=(250, 240, 220, 255))

    return box_img, total_w, total_h, text_w, text_h, padding_y, border_width

# --- 1. Render each scene: image + audio (+ text box) -> clip ---
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
    tc_text = text_capcut_map.get(stt)
    has_text = tc_text is not None

    print(f"Rendering scene {scene_count} (STT {stt}){'  [TEXT: ' + tc_text + ']' if has_text else ''}...")

    if has_text:
        # Create box background image
        box_img, total_w, total_h, text_w, text_h, padding_y, border_width = create_box_image(tc_text)
        box_path = os.path.join(OUTPUT_DIR, f"_box_{stt:03d}.png")
        box_img.save(box_path)

        box_px = (1280 - total_w) // 2
        box_py = 720 - total_h - 15
        text_y = box_py + border_width + padding_y

        # Escape text for FFmpeg
        escaped_text = tc_text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")

        vf = (
            f"scale=1280:720,"
            f"[1:v]format=rgba[pill];"  # placeholder
        )
        # Build filter_complex instead
        filter_complex = (
            f"[0:v]scale=1280:720[bg];"
            f"[2:v]format=rgba[pill];"
            f"[bg][pill]overlay={box_px}:{box_py}:enable='gte(t,0.1)'[withbox];"
            f"[withbox]drawtext=text='{escaped_text}':"
            f"fontfile='C\\:/Windows/Fonts/segoeuib.ttf':"
            f"fontsize=44:"
            f"fontcolor=#222222:"
            f"borderw=0:"
            f"x=(w-text_w)/2:"
            f"y={text_y}:"
            f"alpha='if(lt(t,0.1),0,if(lt(t,0.3),(t-0.1)/0.2,1))'[final]"
        )

        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", img_path,
            "-i", audio_path,
            "-i", box_path,
            "-filter_complex", filter_complex,
            "-map", "[final]",
            "-map", "1:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p", "-r", "30",
            "-shortest",
            clip_path
        ]
    else:
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", img_path,
            "-i", audio_path,
            "-vf", "scale=1280:720",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p", "-r", "30",
            "-shortest",
            clip_path
        ]

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0:
        err = res.stderr.decode('utf-8', errors='ignore')[:200]
        print(f"  [!] Error: {err}")
        # Retry without text
        if has_text:
            print(f"  [!] Retrying without text overlay...")
            cmd2 = [
                "ffmpeg", "-y", "-loop", "1", "-i", img_path,
                "-i", audio_path,
                "-vf", "scale=1280:720",
                "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                "-c:a", "aac", "-b:a", "192k",
                "-pix_fmt", "yuv420p", "-r", "30",
                "-shortest",
                clip_path
            ]
            res2 = subprocess.run(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res2.returncode == 0:
                clip_files.append(clip_path)
                continue
        continue
    clip_files.append(clip_path)

    # Clean up temp box image
    if has_text and os.path.exists(box_path):
        os.remove(box_path)

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

text_count = len(text_capcut_map)
print(f"\nSUCCESS! Video created: {final_video}")
print(f"Text overlay: {text_count} scenes with difficult terms")