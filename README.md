# Stickman - Tu Dong Tao Video Hoat Hinh Stickman (Caveman Explainer)

Du an tu dong hoa quy trinh san xuat video hoat hinh kieu stickman hang dong (caveman explainer).

## Luong Hoat Dong (Workflow)

### Buoc 1: Tao Anh (AI Gemini)
```powershell
cd "C:\File D\Stickman"
python tools/auto_generate_images.py --from 1 --to 50
```
- Su dung Playwright tu dong dieu khien trinh duyet
- Gui prompt vao Gemini Web de tao anh cho tung canh
- Tai anh ve caveman-story/images/
- Can dang nhap Gemini truoc (1 lan)

### Buoc 2: Xoa Watermark
```powershell
.\XOA_LOGO_GEMINI.bat
```
- Su dung gemini-watermark-remover (Node.js)
- Xoa logo Gemini khoi anh -> luu vao caveman-story/images_clean/

### Buoc 3: Tao Giong Doc (OmniVoice TTS)
```powershell
cd "C:\File D\Stickman"
python tools/tts_per_scene.py
```
- Su dung OmniVoice (GPU) de tao audio cho tung canh
- Moi canh = 1 file audio (scene_001.wav ... scene_050.wav)
- Voice cloning tu Kechuyen.wav
- Output: caveman-story/scene_audio/

### Buoc 4: Render Video (Per Scene)
```powershell
cd "C:\File D\Stickman\caveman-story"
python ..\tools\render_per_scene.py
```
- Ghep anh + giong doc thanh clip (duration = audio duration)
- Concat tat ca clips -> video hoan chinh
- Output: caveman-story/output/video_per_scene.mp4

### Buoc 5: (Tuy Chon) Overlay Logo
```powershell
ffmpeg -y -i "output\video_per_scene.mp4" -i "logo.png" -filter_complex "[1:v]scale=60:60[logo];[0:v][logo]overlay=1140:578" -c:a copy "output\video_final.mp4"
```

## Luong Toi Thieu (Neu Da Co Anh + Audio)
```powershell
cd "C:\File D\Stickman\caveman-story"
python ..\tools\render_per_scene.py
```

## Cau Truc Du An
```
Stickman/
├── .gitignore
├── README.md
├── CHAY_TU_DONG_TAO_ANH.bat
├── DANG_NHAP_GEMINI.bat
├── XOA_LOGO_GEMINI.bat
├── Kịch bản loại người xuất hiện.txt    # Kich ban (storyboard)
├── PROMPT_CHO_AI_KHAC_V53.txt            # Prompt template cho AI
├── STYLE_OVERSIMPLIFIED_TEMPLATE.md
├── package-lock.json
├── tools/
│   ├── auto_generate_images.py           # Playwright + Gemini (tao anh)
│   ├── login_gemini.py                   # Launch Chrome + profile
│   ├── parse_storyboard.py               # Parser bang markdown
│   ├── sync_timeline.py                  # Dong bo timeline (audio ↔ storyboard)
│   ├── apply_sfx.py                      # Render video + SFX
│   ├── render_per_scene.py               # Render per-scene (image + audio -> clip -> video)
│   ├── tts_omnivoice.py                  # TTS 1 file audio (OmniVoice GPU)
│   ├── tts_per_scene.py                  # TTS per scene (OmniVoice GPU)
│   └── storyboard_to_projectjson.py      # Chuyen storyboard -> project.json
├── caveman-story/
│   ├── images/                           # Hinh anh da tao (co watermark)
│   ├── images_clean/                     # Hinh anh sau khi xoa watermark
│   ├── output/                           # Video da render
│   ├── sounds/                           # Files am thanh SFX (20 file)
│   ├── render_video.py                   # Renderer chinh (static, no effects)
│   ├── render_clean_slides.py            # Renderer phu (co zoompan nhe)
│   ├── mix_audio.py                      # Tron am thanh (voice + SFX)
│   ├── update_caps.py                    # Cap nhat caption timing
│   ├── aligned_captions.json             # Caption data
│   ├── FULL_VOICEOVER_TEXT.txt           # Van ban narration day du
│   ├── Chương 1.wav                      # File am chinh
│   ├── Kechuyen.wav                      # File audio tham chieu (voice cloning)
│   ├── GROK_REFERENCE_SHEET.png          # Bieu do tham khao Grok
│   ├── NotoSans.ttf                      # Phong chu
│   ├── logo.png                          # Logo kenh (PNG, nen trong suot)
│   └── logo_circle.png                   # Logo hinh tron
└── gemini-watermark-remover/             # Tool xoa watermark (clone tu GitHub)
    ├── bin/gwr.mjs                       # CLI entry point
    ├── node_modules/                     # Node.js dependencies
    └── ...
```

## Sound Effects (SFX)
### 20 SFX Co San:
```
pop.mp3 | Fast Whoosh.mp3 | Wrong answer buzzer.mp3 | Record Scratch.mp3
ding.mp3 | Dramatic Boom.mp3 | Cartoon Punch.mp3 | Tada.mp3
Whoosh Transition.mp3 | sparkle.mp3 | gasp.mp3 | glitch.mp3
Fire Crackle.mp3 | Thunder.mp3 | Heartbeat.mp3 | Wind.mp3
Explosion.mp3 | Water Splash.mp3 | Crickets.mp3 | Time Rewind.mp3
```
### Cach Dung SFX:
- SFX duoc chon tu kich ban (cot "Ten file SFX")
- SFX phat tu dau canh (0.3s sau khi canh bat dau)
- Volume: 0.5 (normal), 0.8 (Dramatic Boom), 0.1 (Record Scratch)

## TTS (Text-to-Speech)
### OmniVoice (GPU):
- Model: k2-fsa/OmniVoice (local cache)
- Voice cloning: Dung Kechuyen.wav lam reference
- Language: Vietnamese (language_id='vi')
- Speed: 1.0 (binh thuong)
- Post-processing: Bat (xoa silence dai, fix breath sounds)
- Manual trim leading silence (fix "lay hoi")

### Cach Dung:
```powershell
# TTS 1 file
python tools/tts_omnivoice.py

# TTS per scene (khuyen dung)
python tools/tts_per_scene.py
```

## Cau Truc Kich Ban (Storyboard)
### Format:
```
STT | Thoi luong uoc tinh | Loai canh, Goc may & Chuyen dong | Loi thoai thuan Viet | Text chen CapCut | Prompt tao anh (English) | Ten file SFX | Tu neo SFX | Vi tri SFX
```
### Quy Tac:
- 1 canh = 1 cau thoai (khong gop nhieu cau)
- So lieu viet bang chu (sau trieu nam, khong viet 6.000.000)
- Chi dung 4 dau: phay (,) cham (.) hoi (?) cham than (!)
- SFX phat tu dau canh (khong dung tu neo)

## Cai Dat & Dependencies
### Phan Mem Can Co:
- Python 3.11+
- ffmpeg (tren PATH)
- Node.js (cho watermark remover)
- Google Chrome (cho Playwright)

### Python Packages:
```
playwright
omnivoice
torch (CUDA)
soundfile
numpy
opencv-python (optional, cho watermark removal)
```

### Cai Dat:
```powershell
pip install omnivoice torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
pip install soundfile numpy opencv-python
playwright install chromium
```

## Ghi Chu
### Files Quan Trong:
| File | Mo ta |
|------|-------|
| Kịch bản loại người xuất hiện.txt | Kich ban (storyboard) |
| PROMPT_CHO_AI_KHAC_V53.txt | Prompt template cho AI |
| caveman-story/Chương 1.wav | File am chinh |
| caveman-story/Kechuyen.wav | File am tham chieu (voice cloning) |
| caveman-story/GROK_REFERENCE_SHEET.png | Anh mau nhan vat Grok |
| tools/tts_per_scene.py | TTS per scene (OmniVoice GPU) |
| tools/render_per_scene.py | Render video (image + audio) |
| tools/apply_sfx.py | Render video + SFX |
| tools/sync_timeline.py | Dong bo timeline (audio ↔ storyboard) |

### Files Khong Can Push Len Git:
- gemini_browser_profile/ (browser profile)
- gemini-watermark-remover/ (clone separately)
- caveman-story/images/ (generated, can be regenerated)
- caveman-story/output/ (rendered videos)
- caveman-story/scene_audio/ (generated audio)
- __pycache__/ (Python cache)

## Luong Toi Thieu (Neu Da Co Anh + Audio)
```powershell
cd "C:\File D\Stickman\caveman-story"
python ..\tools\render_per_scene.py
```

## Luong Day Du (Tu Dau)
```powershell
cd "C:\File D\Stickman"

# 1. Tao anh (tu dong)
python tools/auto_generate_images.py --from 1 --to 50

# 2. Xoa watermark
XOA_LOGO_GEMINI.bat

# 3. Tao audio per scene (GPU)
python tools/tts_per_scene.py

# 4. Render video
cd caveman-story
python ..\tools\render_per_scene.py

# 5. Overlay logo (tuy chon)
ffmpeg -y -i "output\video_per_scene.mp4" -i "logo.png" -filter_complex "[1:v]scale=60:60[logo];[0:v][logo]overlay=1140:578" -c:a copy "output\video_final.mp4"
```