from playwright.sync_api import sync_playwright
import json
import os
import time

folder_name = "nhac_tai_ve"
os.makedirs(folder_name, exist_ok=True)

# Số lượng bài hát MỚI bạn muốn tải thêm trong mỗi lần chạy
num_new_songs_to_download = 10
songs_downloaded_this_session = 0

print(f"Đang khởi động Playwright... Sẽ tìm và tải thêm {num_new_songs_to_download} bài hát mới.")

with sync_playwright() as p:
    # Khởi chạy trình duyệt
    browser = p.chromium.launch(headless=True)
    
    # Tạo ngữ cảnh giả lập
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    
    while songs_downloaded_this_session < num_new_songs_to_download:
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
            
            if not music_url:
                continue
                
            # --- ĐIỂM MỚI Ở ĐÂY: Kiểm tra file đã tồn tại trong ổ cứng chưa ---
            file_path = os.path.join(folder_name, f"{title}.mp3")
            if os.path.exists(file_path):
                print(f"[-] Bỏ qua: '{title}' (Đã có sẵn trong thư mục)")
                time.sleep(1) # Nghỉ 1 giây rồi load bài khác
                continue
            # -------------------------------------------------------------------
                
            print(f"[{songs_downloaded_this_session + 1}/{num_new_songs_to_download}] Đang tải: {title}...")
            
            mp3_response = context.request.get(music_url, timeout=180000) 
            
            if mp3_response.ok: 
                with open(file_path, "wb") as f:
                    f.write(mp3_response.body()) 
                
                songs_downloaded_this_session += 1
                print(f"    -> Thành công! Đã lưu: {title}.mp3")
            else:
                print(f"    [!] Bỏ qua bài này do lỗi máy chủ gốc (Mã lỗi: {mp3_response.status})")
                
            time.sleep(1.5)
            
        except Exception as e:
            print(f"    [!] Lỗi mạng hoặc Timeout: Bỏ qua và thử bài mới...")
            time.sleep(2)

    browser.close()

print(f"\nHoàn tất! Đã tải thêm {songs_downloaded_this_session} bài hát mới vào thư mục '{folder_name}'.")