import requests
import re
from datetime import datetime

BASE_URL = "https://hypera.live"  # ganti sesuai sumber

def get_channels():
    """Ambil daftar channel dari API stats"""
    try:
        r = requests.get(f"{BASE_URL}/api/stats", timeout=15)
        r.raise_for_status()
        data = r.json()
        return data.get("channels", [])
    except Exception as e:
        with open("errors.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] ERROR ambil channels: {e}\n")
        return []

def get_stream_url_and_logo(channel_id):
    """Cari link m3u8 (dengan token terbaru) dan poster dari halaman channel"""
    url = f"{BASE_URL}/{channel_id}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    html = r.text

    # Cari m3u8
    m3u8_match = re.search(r'(https://.*?\.m3u8[^\s"\']+)', html)
    stream_url = m3u8_match.group(1) if m3u8_match else None

    # Cari poster/logo
    poster_match = re.search(r'(https://.*?\.(?:jpg|png|webp))', html)
    poster_url = poster_match.group(1) if poster_match else None

    return stream_url, poster_url

def save_m3u(channels, filename="tipikroya.m3u"):
    """Simpan playlist ke file M3U"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in channels:
            name = ch["name"]
            url = ch.get("url")
            logo = ch.get("logo")
            if url:
                if logo:
                    f.write(f'#EXTINF:-1 tvg-logo="{logo}",{name}\n{url}\n')
                else:
                    f.write(f'#EXTINF:-1,{name}\n{url}\n')

def main():
    playlist = []
    channels_data = get_channels()

    for ch in channels_data:
        channel_id = ch.get("id")
        name = ch.get("name", channel_id)
        try:
            stream_url, logo = get_stream_url_and_logo(channel_id)
            if stream_url:
                playlist.append({"name": name, "url": stream_url, "logo": logo})
                print(f"[OK] {name}: {stream_url}")
            else:
                print(f"[SKIP] {name}: stream tidak ditemukan")
        except Exception as e:
            print(f"[ERROR] {name}: {e}")

    save_m3u(playlist)
    print(f"🎉 Playlist berhasil diperbarui: tipikroya.m3u ({len(playlist)} channel)")

if __name__ == "__main__":
    main()
