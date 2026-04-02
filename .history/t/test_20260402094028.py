from playwright.sync_api import sync_playwright
import json
import os
import time

folder_name = "nhac_tai_ve"
os.makedirs(folder_name, exist_ok=True)

downloaded_titles = set()
num_songs_to_download = 10

print("Đang khởi động Playwright (Trình duyệt Chrome chạy ngầm) để vượt Cloudflare...")

with sync_playwright() as p:
    # Khởi chạy trình duyệt
    browser = p.chromium.launch(headless=True)
    
    # Tạo một phiên làm việc (context) giả lập y hệt Google Chrome
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    
    while len(downloaded_titles) < num_songs_to_download:
        try:
            # 1. Truy cập API để lấy dữ liệu JSON
            page.goto("https://api.thanhdieu.com/rand-music.php", wait_until="domcontentloaded")
            content = page.locator("body").inner_text()
            
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                print("[!] Đang vướng màn hình xác minh Cloudflare, chờ trình duyệt tự giải quyết...")
                time.sleep(4) 
                continue 
                
            music_url = data.get("musicUrl")
            title = data.get("titleTracks", "Unknown").replace("/", "-").replace("\\", "-")
            
            if not music_url or title in downloaded_titles:
                continue
                
            print(f"[{len(downloaded_titles) + 1}/{num_songs_to_download}] Đang tải: {title}...")
            
            # 2. Tải file mp3 bằng chính ngữ cảnh của trình duyệt (thay vì requests)
            # context.request.get() sẽ mang theo đầy đủ vân tay, cookies, headers của Chrome
            mp3_response = context.request.get(music_url, timeout=30000) # timeout 30 giây
            
            if mp3_response.ok: # Nếu mã HTTP là 200 (Thành công)
                file_path = os.path.join(folder_name, f"{title}.mp3")
                with open(file_path, "wb") as f:
                    f.write(mp3_response.body()) # Ghi dữ liệu file mp3
                
                downloaded_titles.add(title)
            else:
                print(f"[!] Không thể tải file mp3, mã lỗi máy chủ: {mp3_response.status}")
                
            # Nghỉ ngơi 1.5 giây để tránh bị chặn IP
            time.sleep(1.5)
            
        except Exception as e:
            print(f"Lỗi: {e}")
            time.sleep(3)

    browser.close()

print(f"\nHoàn tất! Đã tải thành công {len(downloaded_titles)} bài hát.")