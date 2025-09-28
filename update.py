import requests
import re
from datetime import datetime

BASE_URL = "https://hypera.live"
OUTPUT_FILE = "tipikroya.m3u"
ERROR_LOG = "errors.log"

def get_channels():
    """Ambil daftar channel dari API Hypera.live"""
    try:
        r = requests.get(f"{BASE_URL}/api/stats", timeout=15)
        r.raise_for_status()
        data = r.json()
        return data.get("channels", [])
    except Exception as e:
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] ERROR get_channels: {e}\n")
        return []

def fetch_m3u8(url):
    """Ambil konten master .m3u8 tiap channel"""
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.text
    except Exception as e:
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] ERROR fetch_m3u8: {e}\n")
        return None

def get_stream_url(channel_id):
    """Cari URL master .m3u8 dari halaman channel"""
    try:
        r = requests.get(f"{BASE_URL}/{channel_id}", timeout=15)
        r.raise_for_status()
        html = r.text
        match = re.search(r'(https://manifest\.media-delivery\.net/.*?\.m3u8\?token=[^"\s]+)', html)
        return match.group(1) if match else None
    except Exception as e:
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] ERROR get_stream_url {channel_id}: {e}\n")
        return None

def save_playlist(channels):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in channels:
            name = ch.get("name", ch.get("id"))
            channel_id = ch.get("id")
            url = get_stream_url(channel_id)
            if url:
                m3u8_content = fetch_m3u8(url)
                if m3u8_content:
                    f.write(f"#EXTINF:-1,{name}\n")
                    f.write(m3u8_content + "\n")
                    print(f"✅ {name} updated")
                else:
                    print(f"⚠️ {name} fetch failed")
            else:
                print(f"⚠️ {name} no stream URL")

def main():
    channels = get_channels()
    if channels:
        save_playlist(channels)
        print("🎉 tipikroya.m3u berhasil diperbarui!")
    else:
        print("⚠️ Tidak ada channel ditemukan.")

if __name__ == "__main__":
    main()
