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

def get_stream_and_logo(channel_id):
    """Cari URL master .m3u8 dan poster/logo dari halaman channel"""
    try:
        r = requests.get(f"{BASE_URL}/{channel_id}", timeout=15)
        r.raise_for_status()
        html = r.text

        # Ambil URL master .m3u8
        m3u8_match = re.search(r'(https://manifest\.media-delivery\.net/.*?\.m3u8\?token=[^"\s]+)', html)
        stream_url = m3u8_match.group(1) if m3u8_match else None

        # Ambil poster/logo (jpg/png/webp)
        logo_match = re.search(r'(https.*?\.(?:jpg|png|webp))', html)
        logo_url = logo_match.group(1) if logo_match else None

        return stream_url, logo_url
    except Exception as e:
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] ERROR get_stream_and_logo {channel_id}: {e}\n")
        return None, None

def save_playlist(channels):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in channels:
            name = ch.get("name", ch.get("id"))
            schedule = ch.get("schedule", "")
            channel_id = ch.get("id")
            stream_url, logo_url = get_stream_and_logo(channel_id)

            if stream_url:
                extinf_line = f"#EXTINF:-1"
                if logo_url:
                    extinf_line += f' tvg-logo="{logo_url}"'
                extinf_line += f',{name} – {schedule}\n'
                f.write(extinf_line)
                f.write(stream_url + "\n")
                print(f"✅ {name} updated")
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
