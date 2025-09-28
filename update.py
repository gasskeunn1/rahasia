import requests
from datetime import datetime

BASE_URL = "https://hypera.live"
OUTPUT_FILE = "tipikroya.m3u"
ERROR_LOG = "errors.log"

def fetch_channels():
    """Ambil daftar channel dari API stats"""
    try:
        r = requests.get(f"{BASE_URL}/api/stats", timeout=15)
        r.raise_for_status()
        data = r.json()
        channels = data.get("channels", [])
        return channels
    except Exception as e:
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] ERROR fetch_channels: {e}\n")
        return []

def fetch_stream(channel_id):
    """Ambil m3u8 dan poster dari halaman channel"""
    try:
        r = requests.get(f"{BASE_URL}/{channel_id}", timeout=15)
        r.raise_for_status()
        html = r.text
        # Cari m3u8
        import re
        m3u8_match = re.search(r'(https.*?\.m3u8[^"\'\s<]+)', html)
        stream_url = m3u8_match.group(1) if m3u8_match else None

        poster_match = re.search(r'(https.*?\.(?:jpg|png|webp))', html)
        logo = poster_match.group(1) if poster_match else None

        return stream_url, logo
    except Exception as e:
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] ERROR fetch_stream {channel_id}: {e}\n")
        return None, None

def save_m3u(channels):
    """Simpan file tipikroya.m3u"""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
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
    channels = fetch_channels()

    if not channels:
        print("⚠️ Tidak ada channel dari API")
        return

    for ch in channels:
        channel_id = ch.get("id")
        name = ch.get("name", channel_id)
        stream_url, logo = fetch_stream(channel_id)
        if stream_url:
            playlist.append({"name": name, "url": stream_url, "logo": logo})
            print(f"✅ {name}: {stream_url}")
        else:
            print(f"⚠️ {name}: stream tidak ditemukan")

    if playlist:
        save_m3u(playlist)
        print(f"🎉 Playlist berhasil disimpan ke {OUTPUT_FILE}")
    else:
        print("⚠️ Playlist kosong, file tidak dibuat")

if __name__ == "__main__":
    main()
