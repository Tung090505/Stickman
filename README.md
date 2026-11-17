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

## 🚀 Quy trình sản xuất video từ A-Z (Chuẩn Thần Chú v5.3)

Quy trình tự động hóa hoàn chỉnh từ khi lên ý tưởng kịch bản đến khi xuất video thành phẩm:

---

### ⚙️ Bước 0: Chuẩn bị một lần (Setup môi trường)
1. **Đăng nhập Gemini:** Nhấp đúp vào [`DANG_NHAP_GEMINI.bat`](file:///C:/File%20D/Stickman/DANG_NHAP_GEMINI.bat) $\rightarrow$ Đăng nhập tài khoản Google $\rightarrow$ Khi thấy khung chat Gemini xuất hiện thì đóng trình duyệt lại (phiên đăng nhập được lưu vĩnh viễn trong `gemini_browser_profile/`).
2. **Cài đặt FFmpeg:** Đảm bảo `ffmpeg` và `ffprobe` đã được thêm vào PATH hệ thống (đã có sẵn trên máy bạn).
3. **Cài đặt Python & Playwright:**
   ```powershell
   pip install playwright
   playwright install chromium
   ```

---

### ✍️ Bước 1: Kêu AI viết kịch bản (Thần chú v5.3)
1. Mở file [`PROMPT_CHO_AI_KHAC_V53.txt`](file:///C:/File%20D/Stickman/PROMPT_CHO_AI_KHAC_V53.txt), copy toàn bộ nội dung.
2. Dán vào **ChatGPT**, **Claude** hoặc **Gemini**.
3. Điền cấu hình ở phần đầu prompt:
   - `TOOL_ẢNH: Gemini`
   - `CHẾ_ĐỘ_GIỌNG: A`
   - `ĐỘ_DÀI_MỤC_TIÊU: 1`
   - `NHÂN_VẬT_CHÍNH: Bob` *(hoặc tên nhân vật bạn chọn)*
4. Ở cuối prompt, dán chủ đề bạn muốn làm (ví dụ: *"Tại sao người cổ đại phát minh ra lửa?"*).
5. **Duyệt kịch bản:**
   - AI sẽ trả về **Bước 0** (bảng phiên âm + dàn ý + hồ sơ nhân vật). Nếu thấy ổn, bạn gõ: `duyệt`.
   - AI sẽ xuất **Hồi 1** (bảng 9 cột nằm trong code block). Gõ `tiếp` để AI xuất tiếp Hồi 2, Hồi 3...

---

### 💾 Bước 2: Lưu file kịch bản
1. Copy toàn bộ **bảng 9 cột** (từ dòng `STT | ...` đến hết dòng cuối cùng của hồi cuối).
2. Dán vào Notepad và lưu thành file:
   👉 **`C:\File D\Stickman\Kịch bản_chuong1.txt`**

> [!IMPORTANT]
> File phải lưu với bảng mã **UTF-8** (để không bị lỗi font tiếng Việt).

---

### 🎨 Bước 3: Tự động tạo ảnh qua Gemini
Mở Terminal (PowerShell / CMD) tại thư mục `C:\File D\Stickman`, chạy lệnh:

```powershell
python tools/auto_generate_images.py --from 1 --to 20
```

- **Cách hoạt động:** Bot Playwright tự khởi động Chrome, gửi từng prompt vào Gemini Web, đợi ảnh vẽ xong và tự động tải về thư mục `caveman-story/images/1.png`, `2.png`, ...
- **Chống khóa tài khoản:** Bot tự động nghỉ ngẫu nhiên 20–28 giây giữa mỗi ảnh để mô phỏng thao tác người thật.
- *(Lưu ý: Nếu đây là lần đầu chạy bot, hãy nhớ chạy `DANG_NHAP_GEMINI.bat` ở Bước 0 trước).*

---

### 🧹 Bước 4: Xóa watermark Gemini (Tùy chọn)
Nhấp đúp chuột vào file:
👉 **[`XOA_LOGO_GEMINI.bat`](file:///C:/File%20D/Stickman/XOA_LOGO_GEMINI.bat)** *(Yêu cầu đã cài Node.js)*

- Toàn bộ ảnh đã tẩy sạch logo ngôi sao sẽ được lưu sang thư mục: `caveman-story/images_clean/`.
- *(Nếu bỏ qua bước này, video vẫn render bình thường nhưng ảnh sẽ còn logo mờ ở góc).*

---

### 🎬 Bước 5: Render video hoàn chỉnh
Chạy lệnh render chính xác các cảnh bạn vừa tạo ảnh:

```powershell
python tools/render_chapter_1.py --from 1 --to 20
```

**Script render sẽ tự động thực hiện:**
- Đọc bảng từ `Kịch bản_chuong1.txt` (Lời thoại thuần Việt, thời lượng ước tính, file SFX, vị trí SFX).
- **Silence Snapping:** Tự động bắt đúng khoảng lặng tự nhiên của giọng đọc, đảm bảo không bao giờ bị cắt chữ giữa câu.
- Tự động ghép: **Hình ảnh** + **Giọng đọc (`Chương 1.wav`)** + **Phụ đề chuẩn ASS**.
- Chèn âm thanh hiệu ứng SFX chuẩn xác theo quy tắc neo từ (nếu không muốn dùng SFX, thêm cờ `--no-sfx`).
- Xuất video Full HD thành phẩm tại: `caveman-story\output\VIDEO_TEST_CHUONG_1.mp4`.

---

### 👁️ Bước 6: Nghiệm thu video
Mở thư mục `caveman-story\output\` và bật file `VIDEO_TEST_CHUONG_1.mp4` lên xem thành quả, hoặc nhấp đúp file:
👉 **[`MO_VIDEO_TEST.bat`](file:///C:/File%20D/Stickman/MO_VIDEO_TEST.bat)**

---

## ⚡ Bảng lệnh tóm tắt (Cheat Sheet - Copy & Chạy)

```powershell
# 1. Tự động vẽ ảnh từ cảnh 1 đến 20:
python tools/auto_generate_images.py --from 1 --to 20

# 2. Xóa watermark Gemini (tùy chọn):
.\XOA_LOGO_GEMINI.bat

# 3. Render video hoàn chỉnh từ cảnh 1 đến 20:
python tools/render_chapter_1.py --from 1 --to 20
```
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
