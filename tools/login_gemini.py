import os
import sys
import subprocess

USER_DATA_DIR = r"C:\File D\Stickman\gemini_browser_profile"
os.makedirs(USER_DATA_DIR, exist_ok=True)

# Tìm đường dẫn Google Chrome thật trên máy Windows
chrome_paths = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
]

chrome_exe = None
for p in chrome_paths:
    if os.path.exists(p):
        chrome_exe = p
        break

if not chrome_exe:
    # Nếu không có Chrome thật, mở bằng trình duyệt mặc định của Windows
    print("[*] Đang mở web Gemini bằng trình duyệt của bạn...")
    import webbrowser
    webbrowser.open("https://gemini.google.com/app")
else:
    print(f"[*] Tìm thấy Chrome tại: {chrome_exe}")
    print("[*] Đang mở Chrome với hồ sơ riêng: gemini_browser_profile...")
    cmd = [
        chrome_exe,
        f"--user-data-dir={USER_DATA_DIR}",
        "https://gemini.google.com/app"
    ]
    subprocess.Popen(cmd)

print("\n" + "=" * 60)
print(" CỬA SỔ CHROME ĐÃ ĐƯỢC BẬT LÊN MÀN HÌNH!")
print(" Hãy đăng nhập tài khoản Google của bạn trên cửa sổ đó nhé.")
print("=" * 60)
