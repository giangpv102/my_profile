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
    
    # Tạo ngữ cảnh giả lập
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    
    while len(downloaded_titles) < num_songs_to_download:
        try:
            page.goto("https://api.thanhdieu.com/rand-music.php", wait_until="domcontentloaded")
            content = page.locator("body").inner_text()
            
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                print("[!] Đang vướng màn hình xác minh Cloudflare, chờ...")
                time.sleep(4) 
                continue 
                
            music_url = data.get("musicUrl")
            title = data.get("titleTracks", "Unknown").replace("/", "-").replace("\\", "-")
            
            if not music_url or title in downloaded_titles:
                continue
                
            print(f"[{len(downloaded_titles) + 1}/{num_songs_to_download}] Đang tải: {title}...")
            
            # SỬA TẠI ĐÂY: Tăng timeout lên 180000ms (180 giây / 3 phút) để đủ thời gian tải file nặng
            mp3_response = context.request.get(music_url, timeout=180000) 
            
            if mp3_response.ok: 
                file_path = os.path.join(folder_name, f"{title}.mp3")
                with open(file_path, "wb") as f:
                    f.write(mp3_response.body()) 
                
                downloaded_titles.add(title)
                print(f"    -> Thành công! Đã lưu: {title}.mp3")
            else:
                print(f"    [!] Bỏ qua bài này do lỗi máy chủ gốc (Mã lỗi: {mp3_response.status})")
                
            time.sleep(1.5)
            
        except Exception as e:
            # Nếu vẫn bị timeout hoặc lỗi mạng, in ra và đi tiếp
            print(f"    [!] Lỗi mạng hoặc Timeout: Bỏ qua và thử bài mới...")
            time.sleep(2)

    browser.close()

print(f"\nHoàn tất! Đã tải thành công {len(downloaded_titles)} bài hát vào thư mục '{folder_name}'.")