import os
import shutil
import subprocess

base_dir = r"C:\File D\Stickman\caveman-story"
sounds_dir = os.path.join(base_dir, "sounds")
output_dir = os.path.join(base_dir, "output")
cache_dir = os.path.join(output_dir, "audio_cache")
os.makedirs(cache_dir, exist_ok=True)

sound_map = {
    "Ding.mp3": "ding.mp3",
    "pop.mp3": "pop.mp3",
    "Crickets.mp3": "Crickets.mp3",
    "Wind.mp3": "Wind.mp3",
    "Fire Crackle.mp3": "Fire Crackle.mp3",
    "Thunder.mp3": "Thunder.mp3",
    "Heartbeat.mp3": "Heartbeat.mp3",
    "Explosion.mp3": "Explosion.mp3",
    "Water Splash.mp3": "Water Splash.mp3",
    "Whoosh Transition.mp3": "Whoosh Transition.mp3",
    "gasp.mp3": "gasp.mp3",
    "sparkle.mp3": "sparkle.mp3",
    "glitch.mp3": "glitch.mp3",
}

for orig, clean in sound_map.items():
    src = os.path.join(sounds_dir, orig)
    dst = os.path.join(cache_dir, clean)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copied {orig} -> {clean}")
    else:
        print(f"Warning: {orig} not found!")

voice_file = os.path.join(base_dir, "Chuong 1.wav")
raw_video = os.path.join(output_dir, "video_raw.mp4")
ass_path = os.path.join(output_dir, "captions.ass")
final_video = os.path.join(output_dir, "video_chuong1_am_thanh_song_dong.mp4")

ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:")

filter_complex = (
    f"[0:v]eq=brightness='if(between(t,70.0,70.3),0.6,0)':enable='between(t,70.0,70.3)',ass='{ass_escaped}'[v_out];"
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
    "-i", raw_video,
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

print("Rendering video with 7 SFX sound effects and lightning flash...")
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if res.returncode != 0:
    print("Error rendering:", res.stderr.decode('utf-8', errors='ignore'))
else:
    print(f"SUCCESS! Rendered to {final_video}")
