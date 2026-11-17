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

def detect_silences(audio_path, noise_db=-28, min_dur=0.2):
    res = subprocess.run(['ffmpeg', '-i', audio_path, '-af',
                          'silencedetect=noise=%sdB:d=%s' % (noise_db, min_dur),
                          '-f', 'null', '-'], capture_output=True, text=True,
                         encoding='utf-8', errors='ignore')
    starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', res.stderr)]
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', res.stderr)]
    return starts, ends

def build_segments(audio_path, target_count):
    """Tao segments khop voi target_count bang silence detection + merge."""
    audio_dur = get_audio_duration(audio_path)
    starts, ends = detect_silences(audio_path, -28, 0.2)

    # Midpoints = scene change points
    midpoints = [(s + e) / 2 for s, e in zip(starts, ends)]
    change_points = [0.0] + midpoints + [audio_dur]

    # Build raw segments
    raw_segs = []
    for i in range(len(change_points) - 1):
        raw_segs.append({
            'start': change_points[i],
            'end': change_points[i + 1],
            'dur': change_points[i + 1] - change_points[i]
        })

    # Neu so segments > target, merge cac segment ngan nhat
    while len(raw_segs) > target_count:
        min_idx = 1
        min_dur = raw_segs[1]['dur']
        for i in range(1, len(raw_segs) - 1):
            if raw_segs[i]['dur'] < min_dur:
                min_dur = raw_segs[i]['dur']
                min_idx = i

        if min_idx > 0 and (min_idx == len(raw_segs) - 1 or
                             raw_segs[min_idx - 1]['dur'] <= raw_segs[min_idx + 1]['dur']):
            raw_segs[min_idx - 1]['end'] = raw_segs[min_idx]['end']
            raw_segs[min_idx - 1]['dur'] = raw_segs[min_idx - 1]['end'] - raw_segs[min_idx - 1]['start']
            del raw_segs[min_idx]
        else:
            raw_segs[min_idx]['end'] = raw_segs[min_idx + 1]['end']
            raw_segs[min_idx]['dur'] = raw_segs[min_idx]['end'] - raw_segs[min_idx]['start']
            del raw_segs[min_idx + 1]

    return raw_segs, audio_dur

def main():
    rows = parse_storyboard(STORYBOARD)
    target_count = len(rows)
    audio_dur = get_audio_duration(AUDIO)
    print("Audio duration: %.2fs" % audio_dur)
    print("Storyboard scenes: %d" % target_count)

    segments, _ = build_segments(AUDIO, target_count)
    print("Segments after merge: %d" % len(segments))
    print("Total segment duration: %.2fs" % sum(s['dur'] for s in segments))

    # Read original file
    with open(STORYBOARD, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    # Create mapping STT -> new duration
    stt_to_dur = {}
    for i, row in enumerate(rows):
        stt = str(row.get('stt', '')).strip().strip('*')
        if i < len(segments):
            stt_to_dur[stt] = segments[i]['dur']

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

    print("Done! Total: %.2fs (audio: %.2fs)" % (sum(s['dur'] for s in segments), audio_dur))
    print("First 5 scenes:")
    for i in range(min(5, len(rows))):
        print("  STT %s: %.2fs" % (rows[i].get('stt'), segments[i]['dur']))

if __name__ == '__main__':
    main()
