import os, sys, re, subprocess

sys.path.insert(0, os.path.dirname(__file__))
from parse_storyboard import parse_storyboard

BASE_DIR = r"C:\File D\Stickman"
STORYBOARD = os.path.join(BASE_DIR, "Kịch bản loại người xuất hiện.txt")
AUDIO = os.path.join(BASE_DIR, "caveman-story", "Chương 1.wav")

def get_audio_duration(audio_path):
    res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                          '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
                         capture_output=True, text=True)
    return float(res.stdout.strip())

def main():
    rows = parse_storyboard(STORYBOARD)
    audio_dur = get_audio_duration(AUDIO)
    print("Audio duration: %.2fs" % audio_dur)
    print("Storyboard scenes: %d" % len(rows))

    # Equal distribution: each scene gets same duration
    # This is the simplest approach - no assumptions about speech rate
    equal_dur = audio_dur / len(rows)
    scene_durs = [equal_dur] * len(rows)
    
    print("Equal duration per scene: %.2fs" % equal_dur)
    print("Total: %.2fs" % sum(scene_durs))

    # Read original file
    with open(STORYBOARD, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    # Create mapping STT -> new duration
    stt_to_dur = {}
    for i, row in enumerate(rows):
        stt = str(row.get('stt', '')).strip().strip('*')
        if i < len(scene_durs):
            stt_to_dur[stt] = scene_durs[i]

    # Write new file
    new_lines = []
    for line in lines:
        stripped = line.strip()
        cells = [c.strip() for c in stripped.strip('|').split('|')]
        if len(cells) >= 2 and cells[0].strip('*').isdigit():
            stt = cells[0].strip().strip('*')
            if stt in stt_to_dur:
                new_dur = stt_to_dur[stt]
                cells[1] = "%.2fs" % new_dur
                new_line = '| ' + ' | '.join(cells) + ' |\n'
                new_lines.append(new_line)
                continue
        new_lines.append(line)

    with open(STORYBOARD, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print("Done! Total: %.2fs (audio: %.2fs)" % (sum(scene_durs), audio_dur))
    print("First 5 scenes:")
    for i in range(min(5, len(rows))):
        print("  STT %s: %.2fs" % (rows[i].get('stt'), scene_durs[i]))

if __name__ == '__main__':
    main()
