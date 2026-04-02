import os
import json

music_dir = "assets/music"
output_file = "assets/js/playlist.js"

if not os.path.exists(music_dir):
    print(f"❌ Thư mục {music_dir} không tồn tại!")
    exit(1)

playlist = []
for filename in sorted(os.listdir(music_dir)):
    if filename.endswith(".mp3"):
        title = os.path.splitext(filename)[0]
        playlist.append({
            "titleTracks": title,
            "musicUrl": f"./{music_dir}/{filename}"
        })

js_content = f"// File này được tạo tự động bởi update_playlist.py\nconst myPlaylist = {json.dumps(playlist, indent=2, ensure_ascii=False)};\n"

with open(output_file, "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"✅ Đã cập nhật {output_file} với {len(playlist)} bài hát.")
