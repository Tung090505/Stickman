import os
import sys
import time
import random
import re
from playwright.sync_api import sync_playwright

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = r"C:\File D\Stickman"
SCRIPT_PATH = os.path.join(BASE_DIR, "Kịch bản loại người xuất hiện.txt")
IMAGES_DIR = os.path.join(BASE_DIR, "caveman-story", "images")
USER_DATA_DIR = os.path.join(BASE_DIR, "gemini_browser_profile")
MODEL_SHEET_IMG = os.path.join(BASE_DIR, "caveman-story", "GROK_REFERENCE_SHEET.png")
os.makedirs(IMAGES_DIR, exist_ok=True)

def load_prompts():
    shots = []
    if not os.path.exists(SCRIPT_PATH):
        print(f"[LỖI] Không tìm thấy file kịch bản tại: {SCRIPT_PATH}")
        return shots
        
    with open(SCRIPT_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.strip().startswith("| **"):
                parts = [x.strip() for x in line.split("|")]
                if len(parts) >= 8:
                    stt_str = parts[1].replace("*", "").strip()
                    prompt_str = parts[7].strip().strip("`")
                    if stt_str.isdigit():
                        shots.append((int(stt_str), prompt_str))
    shots.sort(key=lambda x: x[0])
    return shots

def smooth_scroll_down(page, pixels=500):
    try:
        # 1. Lăn con chuột phần cứng (Mouse Wheel) tạo hiệu ứng trượt quán tính mượt mà
        page.mouse.wheel(0, pixels)
        # 2. Đồng thời kích hoạt hiệu ứng cuộn mượt (smooth scroll) trên các khung chat
        page.evaluate("""(px) => {
            const scrollers = document.querySelectorAll('infinite-scroller, .conversation-container, ms-chat-session, main, [role="main"]');
            scrollers.forEach(el => {
                el.scrollBy({ top: px, behavior: 'smooth' });
            });
            window.scrollBy({ top: px, behavior: 'smooth' });
        }""", pixels)
    except Exception:
        pass

# Gán bí danh để tương thích toàn bộ code
scroll_to_bottom = smooth_scroll_down

def get_current_image_srcs(page):
    try:
        srcs = page.evaluate("""
            () => Array.from(document.querySelectorAll("img[src*='googleusercontent.com'], img[src*='blob:'], .image-container img"))
                .map(i => i.src)
                .filter(s => s && s.length > 10)
        """)
        return set(srcs)
    except Exception:
        return set()

def count_generated_images(page):
    imgs = page.locator("img[src*='googleusercontent.com'], img[src*='blob:'], .image-container img").all()
    valid = [im for im in imgs if im.bounding_box() and im.bounding_box()["width"] > 250]
    return len(valid)

def click_send_button(page):
    time.sleep(1)
    send_candidates = [
        "button[aria-label*='Gửi']",
        "button[aria-label*='Send']",
        "button.send-button",
        "button:has(mat-icon:has-text('send'))",
        "button:has(mat-icon:has-text('arrow_upward'))",
        ".chat-input-area button:last-child",
        "rich-textarea ~ button",
        ".input-area button:last-child"
    ]
    sent = False
    for sel in send_candidates:
        btns = page.locator(sel).all()
        for b in btns:
            if b.is_visible():
                try:
                    b.click()
                    sent = True
                    break
                except Exception:
                    pass
        if sent:
            break
            
    if not sent:
        page.keyboard.press("Enter")
    time.sleep(2)

def attach_reference_sheet(page):
    if not os.path.exists(MODEL_SHEET_IMG):
        print(f"[!] Không tìm thấy file ảnh mẫu tại: {MODEL_SHEET_IMG}")
        return False
        
    print(f"[*] Đang tiến hành nạp ảnh mẫu Grok: {MODEL_SHEET_IMG}")
    
    # 1. Thử nạp trực tiếp qua thẻ input file (cách chuẩn nhất của Playwright)
    try:
        page.set_input_files("input[type='file']", MODEL_SHEET_IMG)
        print("[OK] ĐÃ NẠP TRỰC TIẾP ẢNH MẪU GROK VÀO KHUNG CHAT!")
        time.sleep(3)
        return True
    except Exception as e1:
        print(f"    [!] Nạp trực tiếp input[type=file]: {e1}")

    # 2. Thử bấm dấu '+' ở góc dưới bên trái khung chat
    try:
        plus_candidates = [
            "button:has(mat-icon:has-text('add'))",
            "button[aria-label*='tệp']",
            "button[aria-label*='Thêm']",
            "button[aria-label*='Add']",
            "button:has-text('+')",
            ".input-area button:first-child",
            ".chat-input-area button:first-child"
        ]
        for sel in plus_candidates:
            loc = page.locator(sel)
            if loc.count() > 0:
                for b in loc.all():
                    if b.is_visible():
                        b.click()
                        time.sleep(1.5)
                        try:
                            page.set_input_files("input[type='file']", MODEL_SHEET_IMG)
                            print("[OK] ĐÃ BẤM DẤU '+' VÀ NẠP ẢNH MẪU GROK THÀNH CÔNG!")
                            time.sleep(3)
                            return True
                        except Exception:
                            pass
                        break
    except Exception as e2:
        print(f"    [!] Nạp qua nút '+': {e2}")

    return False

def run_continuous_generator(start_shot=1, end_shot=155):
    all_shots = load_prompts()
    if not all_shots:
        print("[LỖI] Danh sách prompt rỗng!")
        return

    shots_to_run = [s for s in all_shots if start_shot <= s[0] <= end_shot]
    print("=" * 60)
    print(f"[*] CHẾ ĐỘ ĐỒNG NHẤT NHÂN VẬT GROK (TỔNG CỘNG {len(all_shots)} ẢNH)")
    print(f"[*] Sẽ vẽ tự động từ cảnh {start_shot} đến {end_shot} ({len(shots_to_run)} ảnh)...")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            accept_downloads=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto("https://gemini.google.com/app")
        print("[*] Đang vào Gemini... Trình duyệt sẽ mở 1 tab duy nhất!")
        time.sleep(5)

        # -------------------------------------------------------------
        # KHÓA NHÂN VẬT & GHI NHỚ THIẾT KẾ (TỰ ĐỘNG KHI GẶP ACC MỚI / CHAT MỚI)
        # -------------------------------------------------------------
        existing_imgs = count_generated_images(page)
        if existing_imgs == 0:
            print("\n" + "=" * 60)
            print("[*] PHÁT HIỆN PHIÊN CHAT MỚI (HOẶC TÀI KHOẢN GOOGLE MỚI)!")
            print("[*] TIẾN HÀNH NẠP ẢNH MẪU VÀ KHÓA NHÂN VẬT GROK...")
            print("=" * 60)
            
            # 1. Nạp ảnh mẫu GROK_REFERENCE_SHEET.png
            attached = attach_reference_sheet(page)
            if not attached:
                print("\n[LƯU Ý] Nếu ảnh chưa nạp được, bạn có thể kéo thả")
                print(f"        file GROK_REFERENCE_SHEET.png vào ô chat ngay bây giờ!")
                print("        (Chờ 6 giây để bạn thả tay nếu muốn...)\n")
                time.sleep(6)

            # 2. Gửi lệnh GHI NHỚ THIẾT KẾ NHÂN VẬT
            try:
                input_box = page.locator("div[contenteditable='true'], textarea, rich-textarea p").first
                input_box.click()
                time.sleep(1)
                memory_msg = (
                    "GHI NHỚ THIẾT KẾ NHÂN VẬT CHÍNH (MASTER CHARACTER DESIGN):\n"
                    "Đây là ảnh mẫu thiết kế gốc của nhân vật Grok.\n"
                    "- Tên nhân vật: Grok (người tiền sử)\n"
                    "- Nhận dạng cố định: Người que 2D (stickman) như trong ảnh mẫu: đầu tròn trắng trơn (#FFFFFF), 2 mắt chấm tròn đen nhỏ, tóc nâu bù xù. Nét vẽ tay đậm kiểu Casual Navigation / OverSimplified, nền màu ấm, không dùng hiệu ứng 3D.\n"
                    "- Trang phục: Áo da thú màu nâu rách vạt quàng qua 1 bên vai (hoặc hoodie xanh ở cảnh hiện đại), thắt lưng dây thừng, đi chân trần.\n\n"
                    "HÃY GHI NHỚ THIẾT KẾ NÀY. Từ cảnh này trở đi, khi vẽ các cảnh tiếp theo, hãy luôn bám sát diện mạo và phong cách người que này xuyên suốt toàn bộ câu chuyện! Hãy xác nhận 'Đã ghi nhớ Grok'."
                )
                input_box.fill(memory_msg)
                time.sleep(1)
                
                # BẤM NÚT GỬI MÀU XANH
                print("[*] Đang bấm nút gửi lệnh ghi nhớ...")
                click_send_button(page)
                print("[OK] ĐÃ BẤM NÚT GỬI! Đang chờ 10s để Gemini nạp vào bộ nhớ...")
                time.sleep(10)
            except Exception as e:
                print(f"[!] Lỗi khi gửi chỉ thị ghi nhớ: {e}")
        else:
            print(f"\n[*] PHÁT HIỆN PHIÊN CHAT HIỆN TẠI ĐÃ CÓ {existing_imgs} ẢNH!")
            print("[*] Gemini đã ghi nhớ nhân vật Grok từ trước, tiếp tục vẽ nối tiếp...")

        # Tập hợp tất cả các URL ảnh đã tồn tại trước đó để KHÔNG BAO GIỜ tải lại ảnh cũ
        known_srcs = get_current_image_srcs(page)
        print(f"[*] Đã quét và ghi nhớ {len(known_srcs)} ảnh cũ trên trang. Bắt đầu vẽ cảnh mới...")

        for stt, prompt in shots_to_run:
            target_file = os.path.join(IMAGES_DIR, f"{stt}.png")
            if os.path.exists(target_file):
                print(f"[-] Cảnh {stt:02d} đã có ảnh ({stt}.png), bỏ qua...")
                continue

            print(f"\n>>> [{stt:03d}/{end_shot:03d}] ĐANG VẼ CẢNH {stt}...")
            print(f"    Prompt: {prompt[:80]}...")

            try:
                # 1. Tự động cuộn xuống đáy trước khi gõ
                scroll_to_bottom(page)
                time.sleep(1)

                input_box = page.locator("div[contenteditable='true'], textarea, rich-textarea p").first
                input_box.click()
                time.sleep(1)
                input_box.fill(prompt)
                time.sleep(1)
                
                # BẤM NÚT GỬI MÀU XANH
                click_send_button(page)
                print(f"    -> Đã bấm nút gửi Cảnh {stt}! Đang chờ Gemini vẽ bức ảnh MỚI...")
                
                # 2. Cuộn xuống đáy ngay sau khi gửi
                time.sleep(2)
                scroll_to_bottom(page)

                downloaded = False
                # Chờ tối đa 60 giây (30 lần x 2s) cho ảnh mới xuất hiện
                for wait_step in range(30):
                    time.sleep(2)
                    # Luôn tự động cuộn xuống đáy để ảnh hiển thị và không bị khuất
                    scroll_to_bottom(page)
                    
                    # Quét toàn bộ ảnh hiện có trên trang
                    current_imgs = page.locator("img[src*='googleusercontent.com'], img[src*='blob:'], .image-container img").all()
                    
                    # Tìm bức ảnh MỚI (chưa từng có trong known_srcs)
                    new_img = None
                    new_src = None
                    for img in reversed(current_imgs):
                        try:
                            src = img.get_attribute("src") or ""
                            if src and src not in known_srcs:
                                # Kiểm tra xem ảnh đã tải xong kích thước thực chưa
                                is_loaded = page.evaluate("(el) => el.complete && el.naturalWidth > 150", img.element_handle())
                                if is_loaded:
                                    new_img = img
                                    new_src = src
                                    break
                        except Exception:
                            pass
                            
                    if new_img and new_src:
                        print(f"    [OK] Đã phát hiện ảnh MỚI Cảnh {stt}! Đang lưu file gốc...")
                        try:
                            # Cách 1: Tải trực tiếp bằng Python nếu là link HTTP (không bị chặn CSP)
                            if new_src.startswith("http"):
                                import urllib.request
                                req = urllib.request.Request(new_src, headers={"User-Agent": "Mozilla/5.0"})
                                with urllib.request.urlopen(req, timeout=15) as resp, open(target_file, "wb") as f:
                                    f.write(resp.read())
                                downloaded = True
                            
                            # Cách 2: Nếu là blob, trích xuất dữ liệu pixel qua Canvas (không dùng fetch)
                            if not downloaded:
                                import base64
                                b64_str = page.evaluate("""(img) => {
                                    try {
                                        const canvas = document.createElement('canvas');
                                        canvas.width = img.naturalWidth || img.clientWidth || 1280;
                                        canvas.height = img.naturalHeight || img.clientHeight || 720;
                                        const ctx = canvas.getContext('2d');
                                        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                                        return canvas.toDataURL('image/png').split(',')[1];
                                    } catch(e) {
                                        return null;
                                    }
                                }""", new_img.element_handle())
                                if b64_str:
                                    with open(target_file, "wb") as f:
                                        f.write(base64.b64decode(b64_str))
                                    downloaded = True

                            # Cách 3: Chụp trực tiếp element ảnh từ Playwright (chắc chắn 100% thành công)
                            if not downloaded:
                                new_img.scroll_into_view_if_needed()
                                time.sleep(0.5)
                                new_img.screenshot(path=target_file)
                                downloaded = True

                        except Exception as e_dl:
                            print(f"    [!] Lỗi lưu ảnh qua stream, chuyển sang chụp phần tử: {e_dl}")
                            try:
                                new_img.scroll_into_view_if_needed()
                                time.sleep(0.5)
                                new_img.screenshot(path=target_file)
                                downloaded = True
                            except Exception:
                                pass

                        # Kiểm tra file đã được lưu hợp lệ
                        if downloaded and os.path.exists(target_file) and os.path.getsize(target_file) > 1000:
                            known_srcs.add(new_src)
                            size_kb = os.path.getsize(target_file) // 1024
                            print(f"    [XONG 100%] Đã lưu ảnh Cảnh {stt} -> {stt}.png ({size_kb} KB)")
                            break

                if not downloaded:
                    print(f"    [!] Cảnh {stt} chưa lấy được ảnh mới (quá thời gian chờ hoặc Gemini chưa vẽ xong).")

                scroll_to_bottom(page)
                sleep_time = random.uniform(5.0, 8.0)
                print(f"    [Nghỉ {sleep_time:.1f}s trước cảnh tiếp...]")
                time.sleep(sleep_time)

            except Exception as e:
                print(f"    [LỖI] Cảnh {stt}: {e}")
                time.sleep(4)

        print("\n" + "=" * 60)
        print("[HOÀN TẤT] Quá trình tạo và tải ảnh kết thúc!")
        print("=" * 60)
        browser.close()

if __name__ == "__main__":
    start = 1
    end = 155
    if len(sys.argv) >= 3:
        start = int(sys.argv[1])
        end = int(sys.argv[2])
    run_continuous_generator(start, end)
