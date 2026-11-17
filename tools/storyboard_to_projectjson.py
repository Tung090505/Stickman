# -*- coding: utf-8 -*-
"""
Chuyen bang phan canh v5.2 thanh project.json dung cho caveman-story/render_video.py
Su dung: python tools/storyboard_to_projectjson.py "duong dan file kinh ban" [output.json]
"""
import io
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from parse_storyboard import parse_storyboard


def estimate_seconds(loi_thoai: str, che_do: str = "A") -> float:
    """
    Uoc tin giay theo cong thuc v5.2: so tieng / 4, cong 0.5 moi '...' (che do A),
    lam tron len boi so 0.5.
    """
    words = loi_thoai.split()
    syllables = 0
    for w in words:
        syllables += max(1, len(w.split("-")))

    dur = syllables / 4.0
    if che_do == "A":
        dur += 0.5 * loi_thoai.count("...")
    # Lam tron len 0.5
    dur = round(dur * 2) / 2
    return max(1.0, dur)


def build_project_json(rows: list, audio_duration: float = None) -> dict:
    captions = []
    current_time = 0.0

    for row in rows:
        dur = estimate_seconds(row.get("loi_thoai", ""), che_do="A")
        start = round(current_time, 2)
        end = round(current_time + dur, 2)
        text = row.get("loi_thoai", "").replace("\n", "\\N")
        captions.append({
            "start": start,
            "end": end,
            "text": text
        })
        current_time = end

    project = {
        "captions": captions,
        "total_duration": round(current_time, 2),
        "audio_duration": audio_duration or round(current_time, 2)
    }
    return project


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else r"C:\File D\Stickman\Kịch bản loại người xuất hiện.txt"
    output = sys.argv[2] if len(sys.argv) > 2 else r"C:\File D\Stickman\caveman-story\project.json"

    rows = parse_storyboard(path)
    project = build_project_json(rows)

    with io.open(output, "w", encoding="utf-8") as f:
        json.dump(project, f, ensure_ascii=False, indent=2)

    print(f"OK: {output} voi {len(project['captions'])} captions, tong {project['total_duration']}s")