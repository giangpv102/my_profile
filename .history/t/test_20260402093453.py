import os
import time
from curl_cffi import requests

# Tạo thư mục để lưu nhạc
folder_name = "nhac_tai_ve"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

downloaded_titles = set()
num_songs_to_download = 10 
max_consecutive_errors = 5 
error_count = 0

print(f"Bắt đầu tìm và tải {num_songs_to_download} bài hát bằng curl_cffi (Giả lập Chrome 120)...")

# Thêm Headers để mô phỏng giống hệt một request từ website của họ
headers = {
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://thanhdieu.com/",
    "Origin": "https://thanhdieu.com"
}

while len(downloaded_titles) < num_songs_to_download:
    try:
        # Sử dụng tham số impersonate="chrome120" để giả lập vân tay mạng của Chrome
        api_response = requests.get(
            "https://api.thanhdieu.com/rand-music.php", 
            impersonate="chrome120", 
            headers=headers,
            timeout=15
        )
        
        # Bắt lỗi HTTP nếu có
        if api_response.status_code != 200:
            print(f"[!] Lỗi HTTP {api_response.status_code}. Đang thử lại...")
            error_count += 1
            time.sleep(3)
            continue
            
        try:
            data = api_response.json()
        except Exception:
            print("[!] Bị chặn bởi trang xác minh HTML. Đang đổi IP/Thử lại...")
            error_count += 1
            time.sleep(3)
            continue
            
        music_url = data.get("musicUrl")
        title = data.get("titleTracks", "Unknown_Title").replace("/", "-").replace("\\", "-")
        
        if not music_url:
            print("[!] API không trả về link nhạc. Bỏ qua...")
            continue
            
        if title in downloaded_titles:
            continue
            
        print(f"[{len(downloaded_titles) + 1}/{num_songs_to_download}] Đang tải: {title}...")
        
        # Tải file mp3 với cùng một "dấu vân tay" trình duyệt
        mp3_response = requests.get(
            music_url, 
            impersonate="chrome120", 
            headers=headers,
            timeout=30
        )
        
        if mp3_response.status_code == 200:
            file_path = os.path.join(folder_name, f"{title}.mp3")
            with open(file_path, "wb") as f:
                f.write(mp3_response.content)
                
            downloaded_titles.add(title)
            error_count = 0 
            time.sleep(2) # Nghỉ 2 giây để tránh spam
        else:
            print(f"[!] Lỗi khi tải file nhạc: {mp3_response.status_code}")
            error_count += 1
        
    except Exception as e:
        print(f"Lỗi kết nối: {e}")
        error_count += 1
        
    if error_count >= max_consecutive_errors:
        print(f"\n[!] Dừng khẩn cấp: Lỗi liên tục {max_consecutive_errors} lần. Bảo mật quá chặt.")
        break
        
    if error_count > 0:
        time.sleep(4)

print(f"\nHoàn tất! Đã tải được {len(downloaded_titles)} bài hát.")