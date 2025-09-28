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

def generate_playlist(channels):
    """Buat playlist M3U dari data channel"""
    playlist = []
    for ch in channels:
        name = ch.get("name")
        stream_url = ch.get("stream_url") or ch.get("url")  # sesuaikan field API
        logo = ch.get("logo")
        if stream_url:
            playlist.append({
                "name": name,
                "url": stream_url,
                "logo": logo
            })
    return playlist

def save_m3u(playlist):
    """Simpan playlist ke file tipikroya.m3u"""
    if not playlist:
        print("⚠️ Playlist kosong, file tidak dibuat")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in playlist:
            name = ch["name"]
            url = ch["url"]
            logo = ch.get("logo")
            if logo:
                f.write(f'#EXTINF:-1 tvg-logo="{logo}",{name}\n{url}\n')
            else:
                f.write(f'#EXTINF:-1,{name}\n{url}\n')
    print(f"🎉 Playlist berhasil disimpan ke {OUTPUT_FILE}")

def main():
    channels = fetch_channels()
    if not channels:
        print("❌ Tidak ada channel dari API")
        return

    playlist = generate_playlist(channels)
    save_m3u(playlist)

if __name__ == "__main__":
    main()
