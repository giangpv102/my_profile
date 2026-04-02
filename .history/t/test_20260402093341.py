import cloudscraper
import os
import time

# Tạo thư mục để lưu nhạc
folder_name = "nhac_tai_ve"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

downloaded_titles = set()
num_songs_to_download = 10 
max_consecutive_errors = 5 
error_count = 0

print(f"Bắt đầu tìm và tải {num_songs_to_download} bài hát bằng Cloudscraper...")

# Khởi tạo scraper để vượt qua tường lửa Cloudflare/Anti-bot
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

while len(downloaded_titles) < num_songs_to_download:
    try:
        # 1. Gọi API bằng scraper thay vì requests
        # Tắt allow_redirects để tránh bị đẩy sang trang lỗi 403.html gây sập DNS
        api_response = scraper.get("https://api.thanhdieu.com/rand-music.php", timeout=15, allow_redirects=False)
        
        # Nếu vẫn bị 403, in thẳng ra để dễ debug
        if api_response.status_code == 403:
            print("[!] Bị tường lửa chặn (Lỗi 403). Đang thử lại...")
            error_count += 1
            time.sleep(3)
            continue
            
        api_response.raise_for_status()
        
        try:
            data = api_response.json()
        except Exception:
            raise ValueError("Phản hồi không phải là JSON hợp lệ (Có thể bị chặn lại bởi trang xác minh).")
            
        music_url = data.get("musicUrl")
        title = data.get("titleTracks", "Unknown_Title").replace("/", "-").replace("\\", "-")
        
        if not music_url:
            raise ValueError("Không tìm thấy link nhạc trong API trả về.")
            
        if title in downloaded_titles:
            continue
            
        print(f"[{len(downloaded_titles) + 1}/{num_songs_to_download}] Đang tải: {title}...")
        
        # 2. Tải file mp3
        mp3_response = scraper.get(music_url, timeout=20)
        mp3_response.raise_for_status()
        
        file_path = os.path.join(folder_name, f"{title}.mp3")
        
        with open(file_path, "wb") as f:
            f.write(mp3_response.content)
            
        downloaded_titles.add(title)
        error_count = 0 
        
        # Vẫn cần nghỉ 2 giây để an toàn
        time.sleep(2) 
        
    except Exception as e:
        print(f"Lỗi: {e}")
        error_count += 1
        
    if error_count >= max_consecutive_errors:
        print(f"\n[!] Dừng khẩn cấp: Lỗi liên tục {max_consecutive_errors} lần. Tường lửa quá mạnh hoặc API đổi cấu trúc.")
        break
        
    if error_count > 0:
        time.sleep(3)

print(f"\nHoàn tất! Đã tải được {len(downloaded_titles)} bài hát.")