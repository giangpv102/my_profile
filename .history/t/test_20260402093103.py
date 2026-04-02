import requests
import os

# Tạo thư mục để lưu nhạc
folder_name = "nhac_tai_ve"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

downloaded_titles = set()
num_songs_to_download = 10 # Thay đổi số lượng bài hát bạn muốn tải ở đây

print(f"Bắt đầu tìm và tải {num_songs_to_download} bài hát...")

while len(downloaded_titles) < num_songs_to_download:
    try:
        # 1. Lấy thông tin bài hát ngẫu nhiên từ API
        api_response = requests.get("https://api.thanhdieu.com/rand-music.php", timeout=10)
        data = api_response.json()
        
        music_url = data.get("musicUrl")
        # Xóa các ký tự đặc biệt không hợp lệ cho tên file
        title = data.get("titleTracks", "Unknown_Title").replace("/", "-").replace("\\", "-")
        
        # 2. Kiểm tra xem bài này đã tải chưa để tránh tải trùng
        if title in downloaded_titles:
            continue
            
        print(f"[{len(downloaded_titles) + 1}/{num_songs_to_download}] Đang tải: {title}...")
        
        # 3. Tải file mp3 về máy
        mp3_response = requests.get(music_url, timeout=15)
        file_path = os.path.join(folder_name, f"{title}.mp3")
        
        with open(file_path, "wb") as f:
            f.write(mp3_response.content)
            
        downloaded_titles.add(title)
        
    except Exception as e:
        print(f"Lỗi khi tải: {e}")

print("Đã hoàn thành việc tải nhạc!")