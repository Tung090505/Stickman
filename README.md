# 🎬 Stickman – Tool Tự Động Tạo Video Hoạt Hình Stickman (Caveman Explainer)

Dự án tự động hóa quy trình sản xuất video hoạt hình kiểu stickman hang động (caveman explainer):

1. **Tự động tạo ảnh:** Bot Playwright gửi prompt vào Gemini Web → tải ảnh từng cảnh về `caveman-story/images/`.
2. **Xóa watermark:** Dùng `gemini-watermark-remover` (Node.js) xóa logo Gemini → lưu vào `caveman-story/images_clean/`.
3. **Render video:** Ghép ảnh + âm thanh + phụ đề thành video Full HD bằng FFmpeg → xuất ra `caveman-story/output/`.

## 📂 Cấu trúc dự án

```
Stickman/
├── .gitignore
├── README.md
├── CHAY_TU_DONG_TAO_ANH.bat
├── DANG_NHAP_GEMINI.bat
├── XOA_LOGO_GEMINI.bat
├── Kịch bản loại người xuất hiện.txt
├── PROMPT_CHO_AI_KHAC.txt
├── STYLE_OVERSIMPLIFIED_TEMPLATE.md
├── package-lock.json
├── tools/
│   ├── auto_generate_images.py
│   ├── login_gemini.py
│   └── render_chapter_1.py
├── caveman-story/
│   ├── images/
│   ├── images_clean/
│   ├── output/
│   ├── sounds/
│   ├── render_video.py
│   ├── GROK_REFERENCE_SHEET.png
│   ├── Chương 1.wav
│   └── project.json
├── gemini-watermark-remover/
├── gemini_browser_profile/
├── stickman-video-director/
└── Fooocus/
```

## 🛠 Yêu cầu hệ thống

- **Windows 10/11**
- **Python 3.11+** (đường dẫn khuyên dùng: `C:/Users/<tên>/AppData/Local/Programs/Python/Python311/python.exe`)
- **Node.js** (đường dẫn khuyên dùng: `C:/Program Files/nodejs/node.exe`)
- **Google Chrome** (đã cài đặt)
- **ffmpeg & ffprobe** đã thêm vào PATH hệ thống
- **Tài khoản Google/Gemini**
- Thư viện Python: `playwright` (`pip install playwright` rồi `playwright install chromium`)

## ▶️ Cách chạy dự án (từng bước)

### Bước 0: Đăng nhập Gemini (chỉ cần làm 1 lần)

Nhấp đúp vào `DANG_NHAP_GEMINI.bat`. Cửa sổ Chrome sẽ mở ra trang Gemini. Hãy đăng nhập tài khoản Google. Khi thấy khung chat Gemini xuất hiện, hãy **đóng trình duyệt lại**. Phiên đăng nhập được lưu trong `gemini_browser_profile/`.

> ⚠️ `gemini_browser_profile/` nằm trong `.gitignore` — **không bao giờ push lên GitHub**.

### Bước 1: Tự động tạo ảnh từ script

Nhấp đúp vào `CHAY_TU_DONG_TAO_ANH.bat`. Nhập cảnh bắt đầu (mặc định 1) và kết thúc (mặc định 70). Bot Playwright tự gửi từng prompt vào Gemini Web, chờ ảnh vẽ xong và tải về `caveman-story/images/`. Có độ trễ 20–28s giữa các ảnh để tránh bị chặn. Khi xong, bat tự gọi `XOA_LOGO_GEMINI.bat` để xóa watermark.

### Bước 2: Xóa watermark (nếu chạy riêng lẻ)

Nhấp đúp vào `XOA_LOGO_GEMINI.bat`. Dùng Node.js + `gemini-watermark-remover` quét ảnh trong `caveman-story/images/`, kết quả lưu vào `caveman-story/images_clean/`.

### Bước 3: Render video

Chạy trong terminal tại `C:/File D/Stickman`:
`python tools/render_chapter_1.py`
hoặc `python caveman-story/render_video.py`

Video xuất ra trong `caveman-story/output/` (không push lên git).
## 📜 Các file .bat chính

| File | Chức năng |
|------|-----------|
| `DANG_NHAP_GEMINI.bat` | Đăng nhập Gemini lần đầu, lưu profile Chrome |
| `CHAY_TU_DONG_TAO_ANH.bat` | Tự động tạo ảnh từ script (chạy Bước 0 trước) |
| `XOA_LOGO_GEMINI.bat` | Xóa watermark Gemini khỏi ảnh đã sinh |

## ☁️ Cách up (push) dự án lên GitHub

Repository: `https://github.com/Tung090505/Stickman`

Cài Git: [https://git-scm.com/](https://git-scm.com/)

### Cách 1: Terminal (PowerShell / CMD)

Mở terminal tại `C:/File D/Stickman`, chạy lần lượt:

```powershell
git config --global user.name 'Tung090505'
git config --global user.email 'email_cua_ban@example.com'
git init
git branch -M main
git remote add origin https://github.com/Tung090505/Stickman.git
git add .
git status
git commit -m '🎉 Init: Stickman project - auto caveman explainer video tool'
git push -u origin main
```

Nếu Git hỏi mật khẩu khi push, hãy dùng **Personal Access Token (PAT)** GitHub (không dùng mật khẩu web).

### Cách 2: GitHub Desktop

1. Tải [https://desktop.github.com/](https://desktop.github.com/), đăng nhập GitHub.
2. `File → Add Local Repository...` → chọn `C:/File D/Stickman`.
3. Viết mô tả commit, nhấn `Publish repository`.
4. Tên repo: `Stickman`, tài khoản `Tung090505`, bỏ chọn Keep this code private nếu muốn public.
5. Nhấn `Publish Repository`.
## ⚠️ Lưu ý trước khi push

`.gitignore` đã loại trừ các nội dung sau (không push lên GitHub):

- `gemini_browser_profile/` — profile Chrome đã đăng nhập Gemini
- `Fooocus/`, `gemini-watermark-remover.zip`, `*.7z`, `*.zip`, `*.tar.gz`
- `caveman-story/output/` — video render xuất ra
- `caveman-story/images/test_*` — ảnh test tạm
- `__pycache__/`, `*.pyc`

File lớn (`Kịch bản loại người xuất hiện.txt`, `Chương 1.wav`, `GROK_REFERENCE_SHEET.png`, `prehistoric_caveman.png`, `NotoSans.ttf`) vẫn ở trong repo. Nếu quá lớn, thêm vào `.gitignore` và dùng [Git LFS](https://git-lfs.github.com/).

## 🧩 Troubleshooting

- **ffmpeg không được reconhe:** Cài ffmpeg, thêm thư mục `bin` vào PATH hệ thống, khởi động lại terminal.
- **Playwright chưa cài trình duyệt:** Chạy `playwright install chromium`.
- **Bot không tìm thấy nút Gửi trên Gemini:** Chạy `DANG_NHAP_GEMINI.bat` và đăng nhập thành công trước.
- **Python path trong .bat sai:** Các file `.bat` hardcode `C:/Users/tunga/AppData/Local/Programs/Python/Python311/python.exe`. Nếu cài Python khác nơi, sửa đường dẫn trong `.bat`.

---

✨ Chúc bạn sản xuất được những video stickman triệu view!
