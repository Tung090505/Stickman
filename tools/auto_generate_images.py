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
IMAGES_DIR = os.path.join(BASE_DIR, "caveman-story", "images")
USER_DATA_DIR = os.path.join(BASE_DIR, "gemini_browser_profile")
MODEL_SHEET_IMG = os.path.join(BASE_DIR, "caveman-story", "GROK_REFERENCE_SHEET.png")
os.makedirs(IMAGES_DIR, exist_ok=True)

sys.path.insert(0, os.path.dirname(__file__))
from parse_storyboard import parse_storyboard

def find_default_script():
    candidates = [
        os.path.join(BASE_DIR, "Kịch bản loại người xuất hiện.txt"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return candidates[0]

def load_prompts(start=1, end=9999, script_path=None):
    actual_path = script_path or find_default_script()
    shots = []
    if not os.path.exists(actual_path):
        print(f"[LOI] Khong tim thay file kich ban tai: {actual_path}")
        return shots

    print(f"[*] Dang doc kich ban tu: {actual_path}")
    rows = parse_storyboard(actual_path)
    for row in rows:
        try:
            stt = int(row.get("stt", "0").strip("*"))
        except Exception:
            continue
        if start <= stt <= end:
            prompt = row.get("prompt_anh", "").strip().strip("`")
            if prompt:
                shots.append((stt, prompt))
    shots.sort(key=lambda x: x[0])
    return shots

def smooth_scroll_down(page, pixels=500):
    try:
        page.mouse.wheel(0, pixels)
        page.evaluate("""(px) => {
            const scrollers = document.querySelectorAll('infinite-scroller, .conversation-container, ms-chat-session, main, [role="main"]');
            scrollers.forEach(el => {
                el.scrollBy({ top: px, behavior: 'smooth' });
            });
            window.scrollBy({ top: px, behavior: 'smooth' });
        }""", pixels)
    except Exception:
        pass

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
    try:
        page.set_input_files("input[type='file']", MODEL_SHEET_IMG)
        print("[OK] ĐÃ NẠP TRỰC TIẾP ẢNH MẪU GROK VÀO KHUNG CHAT!")
        time.sleep(3)
        return True
    except Exception as e1:
        print(f"    [!] Nạp trực tiếp input[type=file]: {e1}")
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

def try_download_button(page, new_img, target_file):
    """Click the Download button for the NEW image only."""
    downloaded = False
    try:
        # Scroll to the new image
        new_img.scroll_into_view_if_needed()
        time.sleep(1)
        
        bbox = new_img.bounding_box()
        if not bbox:
            return False
        
        img_cx = bbox['x'] + bbox['width'] / 2
        img_cy = bbox['y'] + bbox['height'] / 2
        
        # Hover over the new image to reveal download button
        new_img.hover()
        time.sleep(2)
        
        # Find download button by specific aria-label (fast)
        download_btns = page.locator("button[aria-label*='Tải hình ảnh']").all()
        
        # Find the one closest to the new image
        closest_btn = None
        closest_dist = float('inf')
        for b in download_btns:
            if b.is_visible():
                btn_bbox = b.bounding_box()
                if btn_bbox:
                    btn_cx = btn_bbox['x'] + btn_bbox['width'] / 2
                    btn_cy = btn_bbox['y'] + btn_bbox['height'] / 2
                    dist = ((btn_cx - img_cx)**2 + (btn_cy - img_cy)**2)**0.5
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_btn = b
        
        if closest_btn:
            try:
                with page.expect_download(timeout=15000) as download_info:
                    closest_btn.click()
                download = download_info.value
                download.save_as(target_file)
                if os.path.exists(target_file) and os.path.getsize(target_file) > 1000:
                    print(f"    [OK] Tải qua nút Download thành công!")
                    return True
            except Exception as e:
                print(f"    [!] Click failed: {e}")
    except Exception as e:
        print(f"    [!] Error: {e}")
    return False

def run_continuous_generator(start_shot=1, end_shot=155, script_path=None):
    all_shots = load_prompts(start=start_shot, end=end_shot, script_path=script_path)
    if not all_shots:
        print("[LỖI] Danh sách prompt rỗng!")
        return

    shots_to_run = all_shots
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

        existing_imgs = count_generated_images(page)
        if existing_imgs == 0:
            print("\n" + "=" * 60)
            print("[*] PHÁT HIỆN PHIÊN CHAT MỚI (HOẶC TÀI KHOẢN GOOGLE MỚI)!")
            print("[*] TIẾN HÀNH NẠP ẢNH MẪU VÀ KHÓA NHÂN VẬT GROK...")
            print("=" * 60)
            
            attached = attach_reference_sheet(page)
            if not attached:
                print("\n[LƯU Ý] Nếu ảnh chưa nạp được, bạn có thể kéo thả")
                print(f"        file GROK_REFERENCE_SHEET.png vào ô chat ngay bây giờ!")
                print("        (Chờ 6 giây để bạn thả tay nếu muốn...)\n")
                time.sleep(6)

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
                print("[*] Đang bấm nút gửi lệnh ghi nhớ...")
                click_send_button(page)
                print("[OK] ĐÃ BẤM NÚT GỬI! Đang chờ 10s để Gemini nạp vào bộ nhớ...")
                time.sleep(10)
            except Exception as e:
                print(f"[!] Lỗi khi gửi chỉ thị ghi nhớ: {e}")
        else:
            print(f"\n[*] PHÁT HIỆN PHIÊN CHAT HIỆN TẠI ĐÃ CÓ {existing_imgs} ẢNH!")
            print("[*] Gemini đã ghi nhớ nhân vật Grok từ trước, tiếp tục vẽ nối tiếp...")

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
                scroll_to_bottom(page)
                time.sleep(1)

                input_box = page.locator("div[contenteditable='true'], textarea, rich-textarea p").first
                input_box.click()
                time.sleep(1)
                input_box.fill(prompt)
                time.sleep(1)
                
                click_send_button(page)
                print(f"    -> Đã bấm nút gửi Cảnh {stt}! Đang chờ Gemini vẽ bức ảnh MỚI...")

                time.sleep(2)
                scroll_to_bottom(page)

                downloaded = False
                for wait_step in range(30):
                    time.sleep(2)
                    scroll_to_bottom(page)
                    
                    current_imgs = page.locator("img[src*='googleusercontent.com'], img[src*='blob:'], .image-container img").all()
                    
                    new_img = None
                    new_src = None
                    for img in reversed(current_imgs):
                        try:
                            src = img.get_attribute("src") or ""
                            if src and src not in known_srcs:
                                is_loaded = page.evaluate("(el) => el.complete && el.naturalWidth > 150", img.element_handle())
                                if is_loaded:
                                    new_img = img
                                    new_src = src
                                    break
                        except Exception:
                            pass
                            
                    if new_img and new_src:
                        print(f"    [OK] Đã phát hiện ảnh MỚI Cảnh {stt}! Đang tải qua nút Download...")
                        # CHỈ dùng nút Download (tải ảnh gốc không watermark)
                        downloaded = try_download_button(page, new_img, target_file)
                        
                        if not downloaded:
                            print(f"    [!] Không tìm thấy nút Download cho ảnh mới. Bỏ qua cảnh {stt}.")
                            downloaded = False

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
    import argparse
    parser = argparse.ArgumentParser(description="Auto generate images with Gemini")
    parser.add_argument("pos_start", nargs="?", type=int, default=None, help="STT bat dau (positional)")
    parser.add_argument("pos_end", nargs="?", type=int, default=None, help="STT ket thuc (positional)")
    parser.add_argument("--from", type=int, dest="start", default=None, help="STT bat dau")
    parser.add_argument("--to", type=int, dest="end", default=None, help="STT ket thuc")
    parser.add_argument("--script", type=str, default=None, help="Duong dan file kich ban (.txt)")
    args, _ = parser.parse_known_args()

    start = args.start if args.start is not None else (args.pos_start if args.pos_start is not None else 1)
    end = args.end if args.end is not None else (args.pos_end if args.pos_end is not None else 155)
    script_file = args.script or find_default_script()
    run_continuous_generator(start, end, script_path=script_file)