import os
import requests
from datetime import datetime, timedelta
import subprocess

API_KEY = "AIzaSyCw8KjUb51DAGSMn0g8-gEwHEF4cnwEK6k"

CHANNELS = {
    "omid": {
        "channel_id": "UCdpNcdUH9ObL4XpNx-eDQ2g",
        "folder": "omid"
    },
    "morad": {
        "channel_id": "UCbNeU6MiUdbzxiv_YK3EjQg",
        "folder": "morad"
    }
}

def get_completed_lives(channel_id, days=30):
    """دریافت لایوهای تمام شده"""
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": API_KEY,
        "channelId": channel_id,
        "part": "snippet",
        "type": "video",
        "eventType": "completed",
        "order": "date",
        "maxResults": 15,
        "publishedAfter": (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"API Error: {response.status_code}")
        return []
    
    items = response.json().get("items", [])
    videos = []
    for item in items:
        vid = {
            "id": item["id"]["videoId"],
            "title": item["snippet"]["title"].replace("/", "_").replace("\\", "_").replace(":", "_"),
            "published": item["snippet"]["publishedAt"]
        }
        videos.append(vid)
    return videos

def download_audio(video_id, title, folder):
    output_template = f"{folder}/%(title)s.%(ext)s"
    
    cmd = [
        "yt-dlp",
        "-x", "--audio-format", "mp3",
        "--audio-quality", "0",
        "--embed-metadata",
        "--embed-thumbnail",
        "-o", output_template,
        "--download-archive", "downloaded.log",
        "--no-warnings",
        f"https://www.youtube.com/watch?v={video_id}"
    ]
    
    print(f"📥 در حال دانلود: {title[:70]}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
        if result.returncode == 0:
            print(f"✅ دانلود شد: {title[:60]}")
            return True
        else:
            print(f"❌ خطا: {result.stderr[-400:]}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    for name, info in CHANNELS.items():
        print(f"\n🔍 چک کردن کانال {name} ...")
        videos = get_completed_lives(info["channel_id"], days=30)
        print(f"   پیدا شد: {len(videos)} لایو")
        
        os.makedirs(info["folder"], exist_ok=True)
        
        for video in videos:
            download_audio(video["id"], video["title"], info["folder"])

if __name__ == "__main__":
    main()
