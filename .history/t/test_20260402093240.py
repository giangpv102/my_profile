import requests
import os
import time

# Tạo thư mục để lưu nhạc
folder_name = "nhac_tai_ve"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

downloaded_titles = set()
num_songs_to_download = 10 
max_consecutive_errors = 5 # Dừng script nếu lỗi liên tục 5 lần
error_count = 0

print(f"Bắt đầu tìm và tải {num_songs_to_download} bài hát...")

# Bổ sung Headers để giả lập trình duyệt Chrome thật, tránh bị chặn (Lỗi 403)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://thanhdieu.com/"
}

while len(downloaded_titles) < num_songs_to_download:
    try:
        # 1. Lấy thông tin bài hát với headers
        api_response = requests.get("https://api.thanhdieu.com/rand-music.php", headers=headers, timeout=10)
        api_response.raise_for_status() # Báo lỗi ngay nếu mã HTTP không phải 200 (Thành công)
        
        data = api_response.json()
        
        music_url = data.get("musicUrl")
        title = data.get("titleTracks", "Unknown_Title").replace("/", "-").replace("\\", "-")
        
        if not music_url:
            raise ValueError("Không tìm thấy link nhạc trong API trả về.")
            
        # Kiểm tra trùng lặp
        if title in downloaded_titles:
            continue
            
        print(f"[{len(downloaded_titles) + 1}/{num_songs_to_download}] Đang tải: {title}...")
        
        # 2. Tải file mp3
        mp3_response = requests.get(music_url, headers=headers, timeout=15)
        mp3_response.raise_for_status()
        
        file_path = os.path.join(folder_name, f"{title}.mp3")
        
        with open(file_path, "wb") as f:
            f.write(mp3_response.content)
            
        downloaded_titles.add(title)
        error_count = 0 # Reset bộ đếm lỗi nếu tải thành công
        
        # Nghỉ 1.5 giây giữa các lần tải để tránh làm quá tải server và bị khóa IP
        time.sleep(1.5) 
        
    except requests.exceptions.RequestException as e:
        print(f"Lỗi kết nối/tải file: {e}")
        error_count += 1
    except Exception as e:
        print(f"Lỗi không xác định: {e}")
        error_count += 1
        
    # Xử lý nếu lỗi liên tục quá nhiều
    if error_count >= max_consecutive_errors:
        print(f"\n[!] Đã xảy ra lỗi liên tục {max_consecutive_errors} lần. API có thể đang sập hoặc chặn IP của bạn.")
        print("Chương trình tự động dừng để an toàn.")
        break
        
    # Nếu bị lỗi, nghỉ 3 giây trước khi thử lại để tránh spam
    if error_count > 0:
        time.sleep(3)

print(f"\nHoàn tất! Đã tải được {len(downloaded_titles)} bài hát.")