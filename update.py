import requests
import re
from datetime import datetime

BASE_URL = "https://hypera.live"
M3U_FILE = "tipikroya.m3u"

def get_channels():
    url = f"{BASE_URL}/api/stats"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    return data.get("channels", [])

def refresh_stream_url(channel_id):
    """Ambil link m3u8 terbaru dari halaman channel"""
    url = f"{BASE_URL}/{channel_id}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    html = r.text

    # Cari m3u8 (tokenized)
    m3u8_match = re.search(r'(https.*?\.m3u8[^"\'\s<]+)', html)
    stream_url = m3u8_match.group(1) if m3u8_match else None

    # Cari poster/logo
    poster_match = re.search(r'(https.*?\.(?:jpg|png|webp))', html)
    poster_url = poster_match.group(1) if poster_match else None

    return stream_url, poster_url

def save_m3u(channels):
    with open(M3U_FILE, "w", encoding="utf-8") as f:
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
    errors = []

    try:
        channels_data = get_channels()
    except Exception as e:
        with open("errors.log", "a") as f:
            f.write(f"[{datetime.now()}] ERROR fetch channels: {e}\n")
        return

    for ch in channels_data:
        channel_id = ch.get("id")
        name = ch.get("name", channel_id)

        try:
            stream_url, logo = refresh_stream_url(channel_id)
            if stream_url:
                playlist.append({"name": name, "url": stream_url, "logo": logo})
            else:
                errors.append(f"{name} ({channel_id}) -> Stream not found")
        except Exception as e:
            errors.append(f"{name} ({channel_id}) -> Error: {e}")

    save_m3u(playlist)

    if errors:
        with open("errors.log", "a") as f:
            f.write(f"[{datetime.now()}] Errors:\n" + "\n".join(errors) + "\n")

    print(f"✅ Playlist updated: {len(playlist)} channels")

if __name__ == "__main__":
    main()
