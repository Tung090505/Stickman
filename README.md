# 🎬 Stickman – Tool Tự Động Tạo Video Hoạt Hình Stickman (Caveman Explainer)

## 📋 Tổng Quan

Dự án tự động hóa quy trình sản xuất video hoạt hình kiểu stickman hang động (caveman explainer):

1. **Tự động tạo ảnh:** Bot Playwright gửi prompt vào Gemini Web → tải ảnh từng cảnh về `caveman-story/images/`.
2. **Xóa watermark:** Dùng `gemini-watermark-remover` (Node.js) xóa logo Gemini → lưu vào `caveman-story/images_clean/`.
3. **Tạo giọng đọc:** OmniVoice TTS (GPU) tạo audio cho từng cảnh → `caveman-story/scene_audio/scene_XXX.wav`.
4. **Render video:** Ghép ảnh + giọng đọc thành video Full HD bằng FFmpeg → xuất ra `caveman-story/output/`.

---

## 📂 Cấu Trúc Dự Án

```
Stickman/
├── .gitignore
├── README.md
├── CHAY_TU_DONG_TAO_ANH.bat
├── DANG_NHAP_GEMINI.bat
├── XOA_LOGO_GEMINI.bat
├── Kịch bản loại người xuất hiện.txt    # Kịch bản (storyboard)
├── PROMPT_CHO_AI_KHAC_V53.txt            # Prompt template cho AI tạo kịch bản
├── STYLE_OVERSIMPLIFIED_TEMPLATE.md
├── package-lock.json
├── gemini-watermark-remover.zip           # Tool xóa watermark (Node.js)
├── tools/
│   ├── auto_generate_images.py           # Playwright + Gemini (tạo ảnh)
│   ├── login_gemini.py                   # Launch Chrome + profile
│   ├── parse_storyboard.py               # Parser bảng markdown
│   ├── sync_timeline.py                  # Đồng bộ timeline (audio ↔ storyboard)
│   ├── apply_sfx.py                      # Render video + SFX
│   ├── render_per_scene.py               # Render per-scene (image + audio → clip → video)
│   ├── tts_omnivoice.py                  # TTS 1 file audio (OmniVoice GPU)
│   ├── tts_per_scene.py                  # TTS per scene (OmniVoice GPU)
│   └── storyboard_to_projectjson.py      # Chuyển storyboard → project.json
├── caveman-story/
│   ├── images/                           # Hình ảnh đã tạo (có watermark)
│   ├── images_clean/                     # Hình ảnh sau khi xóa watermark
│   ├── output/                           # Video đã render
│   ├── sounds/                           # Files âm thanh SFX (20 file)
│   ├── render_video.py                   # Renderer chính (static, no effects)
│   ├── render_clean_slides.py            # Renderer phụ (có zoompan nhẹ)
│   ├── mix_audio.py                      # Trộn âm thanh (voice + SFX)
│   ├── update_caps.py                    # Cập nhật caption timing
│   ├── aligned_captions.json             # Caption data
│   ├── FULL_VOICEOVER_TEXT.txt           # Văn bản narration đầy đủ
│   ├── Chương 1.wav                      # File âm chính
│   ├── Kechuyen.wav                      # File audio tham chiếu (voice cloning)
│   ├── GROK_REFERENCE_SHEET.png          # Biểu đồ tham khảo Grok
│   ├── NotoSans.ttf                      # Phông chữ
│   ├── logo.png                          # Logo kênh (PNG, nền trong suốt)
│   └── logo_circle.png                   # Logo hình tròn
└── gemini-watermark-remover/             # Tool xóa watermark (clone từ GitHub)
    ├── bin/gwr.mjs                       # CLI entry point
    ├── node_modules/                     # Node.js dependencies
    └── ...
```

---

## 🔄 Luồng Hoạt Động (Workflow)

### **Bước 1: Tạo Ảnh (AI Gemini)**
```powershell
cd "C:\File D\Stickman"
python tools/auto_generate_images.py --from 1 --to 50
```
- Sử dụng **Playwright** để tự động điều khiển trình duyệt
- Gửi prompt vào **Gemini Web** để tạo ảnh cho từng cảnh
- Tải ảnh về `caveman-story/images/`
- Cần đăng nhập Gemini trước (1 lần)

### **Bước 2: Xóa Watermark**
```powershell
.\XOA_LOGO_GEMINI.bat
```
- Sử dụng `gemini-watermark-remover` (Node.js)
- Xóa logo Gemini khỏi ảnh → lưu vào `caveman-story/images_clean/`
- Cần giải nén/clone tool trước

### **Bước 3: Tạo Giọng Đọc (OmniVoice TTS)**
```powershell
cd "C:\File D\Stickman"
python tools/tts_per_scene.py
```
- Sử dụng **OmniVoice** (GPU) để tạo audio cho từng cảnh
- Mỗi cảnh = 1 file audio (`scene_001.wav` ... `scene_050.wav`)
- Output: `caveman-story/scene_audio/`

### **Bước 4: Render Video (Per Scene)**
```powershell
cd "C:\File D\Stickman\caveman-story"
python ..\tools\render_per_scene.py
```
- Ghép ảnh + giọng đọc thành clip (duration = audio duration)
- Concat tất cả clips → video hoàn chỉnh
- Output: `caveman-story/output/video_per_scene.mp4`

### **Bước 5: (Tùy Chọn) Overlay Logo**
```powershell
ffmpeg -y -i "output\video_per_scene.mp4" -i "logo.png" -filter_complex "[1:v]scale=60:60[logo];[0:v][logo]overlay=1140:578" -c:a copy "output\video_final.mp4"
```

---

## 📋 Luồng Tối Thiểu (Nếu Đã Có Ảnh + Audio)

```powershell
cd "C:\File D\Stickman\caveman-story"
python ..\tools\render_per_scene.py
```

---

## 🎵 Sound Effects (SFX)

### **20 SFX Có Sẵn:**
```
pop.mp3 | Fast Whoosh.mp3 | Wrong answer buzzer.mp3 | Record Scratch.mp3
ding.mp3 | Dramatic Boom.mp3 | Cartoon Punch.mp3 | Tada.mp3
Whoosh Transition.mp3 | sparkle.mp3 | gasp.mp3 | glitch.mp3
Fire Crackle.mp3 | Thunder.mp3 | Heartbeat.mp3 | Wind.mp3
Explosion.mp3 | Water Splash.mp3 | Crickets.mp3 | Time Rewind.mp3
```

### **Cách Dùng SFX:**
- SFX được chọn từ kịch bản (cột "Tên file SFX")
- SFX phát từ đầu cảnh (0.3s sau khi cảnh bắt đầu)
- Volume: 0.5 (normal), 0.8 (Dramatic Boom), 0.1 (Record Scratch)

---

## 🎤 TTS (Text-to-Speech)

### **OmniVoice (GPU):**
- Model: `k2-fsa/OmniVoice` (local cache)
- Voice cloning: Dùng `Kechuyen.wav` làm reference
- Language: Vietnamese (`language_id='vi'`)
- Speed: 1.0 (bình thường)
- Post-processing: Tắt (tránh mất chữ)

### **Cách Dùng:**
```powershell
# TTS 1 file
python tools/tts_omnivoice.py

# TTS per scene (khuyên dùng)
python tools/tts_per_scene.py
```

---

## 📊 Cấu Trúc Kịch Bản (Storyboard)

### **Format:**
```
STT | Thời lượng ước tính | Loại cảnh, Góc máy & Chuyển động | Lời thoại thuần Việt | Text chèn CapCut | Prompt tạo ảnh (English) | Tên file SFX | Từ neo SFX | Vị trí SFX
```

### **Ví Dụ:**
```
01 | 3.0s | Cận cảnh (Close-up). Zoom in từ từ 10%. | Hôm nay bạn chỉ cần ngồi một chỗ là có bác giao hàng tới tận cửa. | NGỒI MỘT CHỖ | Minimalist 2D vector... | pop.mp3 | — | đầu cảnh
```

### **Quy Tắc:**
- **1 cảnh = 1 câu thoại** (không gộp nhiều câu)
- **Số liệu viết bằng chữ** (sáu triệu năm, không viết 6.000.000)
- **Chỉ dùng 4 dấu:** phẩy (,) chấm (.) hỏi (?) chấm than (!)
- **SFX phát từ đầu cảnh** (không dùng từ neo)

---

## 🔧 Cài Đặt & Dependencies

### **Phần Mềm Cần Có:**
- Python 3.11+
- ffmpeg (trên PATH)
- Node.js (cho watermark remover)
- Google Chrome (cho Playwright)

### **Python Packages:**
```
playwright
omnivoice
torch (CUDA)
soundfile
numpy
opencv-python (optional, cho watermark removal)
```

### **Cài Đặt:**
```powershell
pip install omnivoice torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install soundfile numpy opencv-python
playwright install chromium
```

---

## 📝 Ghi Chú

### **Files Quan Trọng:**
| File | Mô tả |
|------|-------|
| `Kịch bản loại người xuất hiện.txt` | Kịch bản (storyboard) |
| `PROMPT_CHO_AI_KHAC_V53.txt` | Prompt template cho AI |
| `caveman-story/Chương 1.wav` | File audio chính |
| `caveman-story/Kechuyen.wav` | File audio tham chiếu (voice cloning) |
| `caveman-story/GROK_REFERENCE_SHEET.png` | Ảnh mẫu nhân vật Grok |
| `tools/tts_per_scene.py` | TTS per scene (OmniVoice GPU) |
| `tools/render_per_scene.py` | Render video (image + audio) |
| `tools/apply_sfx.py` | Render video + SFX |
| `tools/sync_timeline.py` | Đồng bộ timeline (audio ↔ storyboard) |

### **Files Không Cần Push Lên Git:**
- `gemini_browser_profile/` (browser profile)
- `gemini-watermark-remover/` (clone separately)
- `caveman-story/images/` (generated, can be regenerated)
- `caveman-story/output/` (rendered videos)
- `caveman-story/scene_audio/` (generated audio)
- `__pycache__/` (Python cache)

---

## 🎯 Luồng Tối Thiểu (Nếu Đã Có Ảnh + Audio)

```powershell
cd "C:\File D\Stickman\caveman-story"
python ..\tools\render_per_scene.py
```

## 🎯 Luồng Đầy Đủ (Từ Đầu)

```powershell
cd "C:\File D\Stickman"

# 1. Tạo ảnh (tự động)
python tools/auto_generate_images.py --from 1 --to 50

# 2. Xóa watermark
XOA_LOGO_GEMINI.bat

# 3. Tạo audio per scene (GPU)
python tools/tts_per_scene.py

# 4. Render video
cd caveman-story
python ..\tools\render_per_scene.py

# 5. Overlay logo (tùy chọn)
ffmpeg -y -i "output\video_per_scene.mp4" -i "logo.png" -filter_complex "[1:v]scale=60:60[logo];[0:v][logo]overlay=1140:578" -c:a copy "output\video_final.mp4"
```