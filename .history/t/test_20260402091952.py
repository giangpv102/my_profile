import requests
import os
import time

API = "https://api.thanhdieu.com/rand-music.php"
SAVE_DIR = "music"

# tạo folder
os.makedirs(SAVE_DIR, exist_ok=True)

downloaded = set()

def safe_filename(name):
    return "".join(c for c in name if c.isalnum() or c in " _-").rstrip()

def download_song(index):
    try:
        res = requests.get(API)
        data = res.json()

        url = data.get("musicUrl")
        title = data.get("titleTracks", f"song_{index}")

        if not url:
            print("❌ Không có URL")
            return

        if url in downloaded:
            print("⏩ Trùng, bỏ qua")
            return

        downloaded.add(url)

        filename = safe_filename(title) + ".mp3"
        path = os.path.join(SAVE_DIR, filename)

        # tải file
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://thanhdieu.com/"
        }

        audio = requests.get(url, headers=headers, stream=True)
        with open(path, "wb") as f:
            for chunk in audio.iter_content(1024):
                f.write(chunk)

        print(f"✅ Đã tải: {filename}")

    except Exception as e:
        print("❌ Lỗi:", e)


def run(total=100):
    for i in range(total):
        download_song(i)

        # delay tránh bị chặn
        time.sleep(1.5)


if __name__ == "__main__":
    run(2)  # chỉnh số lượng tại đây