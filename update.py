import requests
from datetime import datetime

BASE_URL = "https://hypera.live"
OUTPUT_FILE = "tipikroya.m3u"
ERROR_LOG = "errors.log"

def get_channels():
    """Ambil daftar channel dari API stats"""
    try:
        r = requests.get(f"{BASE_URL}/api/stats", timeout=15)
        r.raise_for_status()
        return r.json().get("channels", [])
    except Exception as e:
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] ERROR fetch_channels: {e}\n")
        return []

def get_stream_url(channel_id):
    """Ambil URL m3u8 channel (pastikan endpoint streaming tersedia)"""
    try:
        url = f"{BASE_URL}/api/delivery/stream/{channel_id}/playlist.m3u8"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.url  # kembalikan URL m3u8 valid
    except Exception as e:
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] ERROR stream {channel_id}: {e}\n")
        return None

def save_m3u(channels):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in channels:
            name = ch.get("name")
            channel_id = ch.get("id")
            stream_url = get_stream_url(channel_id)
            if stream_url:
                f.write(f'#EXTINF:-1,{name}\n{stream_url}\n')
                print(f"✅ {name}: {stream_url}")
            else:
                print(f"⚠️ {name}: stream tidak ditemukan")

def main():
    channels = get_channels()
    if not channels:
        print("❌ Tidak ada channel dari API")
        return
    save_m3u(channels)
    print("🎉 Playlist berhasil diupdate.")

if __name__ == "__main__":
    main()
