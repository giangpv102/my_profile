from playwright.sync_api import sync_playwright
import json
import os
import time
import requests

folder_name = "nhac_tai_ve"
os.makedirs(folder_name, exist_ok=True)

downloaded_titles = set()
num_songs_to_download = 10

print("Đang khởi động Playwright (Trình duyệt Chrome chạy ngầm) để vượt Cloudflare...")

with sync_playwright() as p:
    # Mở trình duyệt ẩn (Nếu muốn nhìn tận mắt nó vượt Cloudflare, đổi headless=False)
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    while len(downloaded_titles) < num_songs_to_download:
        try:
            # Truy cập thẳng vào API
            page.goto("https://api.thanhdieu.com/rand-music.php", wait_until="domcontentloaded")
            
            # Lấy toàn bộ text hiển thị trên trang (chính là JSON trả về)
            content = page.locator("body").inner_text()
            
            try:
                # Cố gắng dịch text thành JSON
                data = json.loads(content)
            except json.JSONDecodeError:
                # Nếu không phải JSON, nghĩa là Cloudflare đang bắt chờ 3-5s để xác minh
                print("[!] Đang vướng màn hình xác minh Cloudflare, chờ trình duyệt tự giải quyết...")
                time.sleep(4) 
                continue # Bỏ qua vòng lặp này, thử lại
                
            music_url = data.get("musicUrl")
            title = data.get("titleTracks", "Unknown").replace("/", "-").replace("\\", "-")
            
            if not music_url or title in downloaded_titles:
                continue
                
            print(f"[{len(downloaded_titles) + 1}/{num_songs_to_download}] Đang tải: {title}...")
            
            # Link mp3 thường là link tĩnh lưu ở server khác, dùng thư viện requests tải cho nhanh và nhẹ
            res = requests.get(music_url, timeout=20)
            if res.status_code == 200:
                with open(os.path.join(folder_name, f"{title}.mp3"), "wb") as f:
                    f.write(res.content)
                downloaded_titles.add(title)
            else:
                print(f"[!] Không thể tải file mp3, mã HTTP: {res.status_code}")
                
            # Nghỉ ngơi 1.5 giây để tránh bị Cloudflare tóm lại
            time.sleep(1.5)
            
        except Exception as e:
            print(f"Lỗi: {e}")
            time.sleep(3)

    browser.close()

print(f"\nHoàn tất! Đã tải thành công {len(downloaded_titles)} bài hát.")