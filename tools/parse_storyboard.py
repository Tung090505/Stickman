# -*- coding: utf-8 -*-
"""
Parser bảng phân cảnh v5.2 cho dự án Stickman.
Đọc file text chứa bảng markdown, trả về list dict theo tên cột.
"""
import re
import unicodedata
from typing import List, Dict


def parse_storyboard(path: str) -> List[Dict]:
    """
    Đọc bảng phân cảnh v5.2 từ file text.
    Trả về list các dict, key là tên cột chuẩn (viết liền, không dấu).
    """
    rows: List[Dict] = []
    header: List[str] = []

    COL_MAP = {
        "STT": "stt",
        "Thời lượng ước tính": "thoi_luong",
        "Thoi luong uoc tinh": "thoi_luong",
        "Loại cảnh, Góc máy & Chuyển động (CapCut)": "loai_canh",
        "Loai canh, Goc may & Chuyen dong (CapCut)": "loai_canh",
        "Loại; Nhãn; Góc máy; Chuyển động": "loai_canh",
        "Loai; Nhan; Goc may; Chuyen dong": "loai_canh",
        "Lời thoại thuần Việt (Đã phiên âm)": "loi_thoai",
        "Loi thoai thuan Viet (Da phien am)": "loi_thoai",
        "Text chèn CapCut": "text_capcut",
        "Text chen CapCut": "text_capcut",
        "Prompt tạo ảnh (English)": "prompt_anh",
        "Prompt tao anh (English)": "prompt_anh",
        "Prompt ảnh": "prompt_anh",
        "Prompt anh": "prompt_anh",
        "Tên file SFX": "ten_sfx",
        "Ten file SFX": "ten_sfx",
        "Từ neo SFX": "tu_neo",
        "Tu neo SFX": "tu_neo",
        "Vị trí SFX": "vi_tri_sfx",
        "Vi tri SFX": "vi_tri_sfx",
    }

    # Thử nhiều encoding khác nhau để tránh lỗi UnicodeDecodeError
    encodings_to_try = ["utf-8-sig", "utf-8", "cp1252", "latin-1"]
    file_handle = None
    for enc in encodings_to_try:
        try:
            file_handle = open(path, "r", encoding=enc)
            # Test read first line
            file_handle.readline()
            file_handle.seek(0)
            break
        except (UnicodeDecodeError, UnicodeError):
            if file_handle:
                file_handle.close()
            file_handle = None
            continue
    
    if file_handle is None:
        raise ValueError(f"Không thể đọc file với bất kỳ encoding nào: {path}")
    
    with file_handle:
        for raw_line in file_handle:
            line = raw_line.strip()
            # Bỏ dòng không phải bảng và dòng kẻ |---|
            # Bỏ dòng kẻ phân cách |---|
            if re.match(r"^\s*\|[\s:\-|]+\|?\s*$", line):
                continue

            # Loại bỏ dấu | đầu/cuối nếu có, sau đó tách cột
            cleaned = line.strip()
            if cleaned.startswith("|"):
                cleaned = cleaned[1:]
            if cleaned.endswith("|"):
                cleaned = cleaned[:-1]
            cells = [c.strip() for c in cleaned.split("|")]

            # Bỏ dòng không đủ cột
            if len(cells) < 2:
                continue

            # Dòng tiêu đề cột: chứa "STT" ở bất kỳ vị trí nào
            if any(c == "STT" for c in cells):
                header = cells
                continue

            # Dòng dữ liệu: STT phải là số (có thể có dấu * surrounding, hoặc prefix "Scene")
            stt_raw = cells[0].strip().strip("*").strip()
            # Loại bỏ prefix như "Scene ", "Cảnh ", "STT "
            stt_clean = re.sub(r"^(Scene|Cảnh|STT|C)\s*", "", stt_raw, flags=re.IGNORECASE).strip()
            if header and cells and stt_clean.isdigit():
                row = {}
                for i, col_name in enumerate(header):
                    if i < len(cells):
                        # Fuzzy matching based on keywords
                        col_lower = col_name.lower()
                        col_norm = unicodedata.normalize('NFD', col_lower)
                        col_norm = ''.join(c for c in col_norm if unicodedata.category(c) != 'Mn')
                        col_norm = col_norm.replace(' ', '').replace(';', '').replace('(', '').replace(')', '').replace('_', '')
                        if 'stt' in col_norm and len(col_norm) < 6:
                            key = 'stt'
                        elif 'thoi' in col_norm or 'luong' in col_norm:
                            key = 'thoi_luong'
                        elif 'loai' in col_norm or 'canh' in col_norm or 'goc' in col_norm or 'chuyen' in col_norm or 'nhan' in col_norm:
                            key = 'loai_canh'
                        elif 'loi' in col_norm or 'thoai' in col_norm:
                            key = 'loi_thoai'
                        elif 'text' in col_norm or 'capcut' in col_norm:
                            key = 'text_capcut'
                        elif 'prompt' in col_norm or 'anh' in col_norm:
                            key = 'prompt_anh'
                        elif 'sfx' in col_norm and 'ten' in col_norm:
                            key = 'ten_sfx'
                        elif 'neo' in col_norm:
                            key = 'tu_neo'
                        elif 'vitri' in col_norm or 'vitr' in col_norm:
                            key = 'vi_tri_sfx'
                        else:
                            key = COL_MAP.get(col_name, col_name.lower().replace(' ', '_'))
                        if key == "stt":
                            row[key] = stt_clean
                        else:
                            row[key] = cells[i]
                rows.append(row)

    return rows


if __name__ == "__main__":
    import json
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else r"C:\File D\Stickman\Kịch bản loại người xuất hiện.txt"
    data = parse_storyboard(path)
    print(f"Tổng số cảnh parsed: {len(data)}")
    for row in data[:5]:
        print(json.dumps(row, ensure_ascii=False, indent=2))