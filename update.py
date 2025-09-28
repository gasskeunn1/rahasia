import requests
import re
import os
from datetime import datetime

BASE_URL = "https://hypera.live"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": BASE_URL,
}


def get_channels():
    """Ambil daftar channel dari API stats"""
    url = f"{BASE_URL}/api/stats"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()

    try:
        data = r.json()
    except Exception:
        with open("last_response.html", "w", encoding="utf-8") as f:
            f.write(r.text)
        raise RuntimeError(
            f"API tidak mengembalikan JSON. Status: {r.status_code}, "
            f"panjang response: {len(r.text)}"
        )

    return data.get("channels", [])


def get_stream_url_and_logo(channel_id):
    """Cari link m3u8 + poster dari halaman channel"""
    url = f"{BASE_URL}/{channel_id}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    html = r.text

    # Cari m3u8
    m3u8_match = re.search(r'(https.*?\.m3u8[^"\'\s<]+)', html)
    stream_url = m3u8_match.group(1) if m3u8_match else None

    # Cari poster (logo jpg/png/webp)
    poster_match = re.search(r'(https.*?\.(?:jpg|png|webp))', html)
    poster_url = poster_match.group(1) if poster_match else None

    return stream_url, poster_url


def save_m3u(channels, filename="playlist.m3u"):
    """Simpan daftar channel ke file M3U"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in channels:
            name = ch["name"]
            stream_url = ch.get("url")
            logo = ch.get("logo")
            if stream_url:
                if logo:
                    f.write(f'#EXTINF:-1 tvg-logo="{logo}",{name}\n{stream_url}\n')
                else:
                    f.write(f'#EXTINF:-1,{name}\n{stream_url}\n')


def main():
    errors = []
    channels_data = get_channels()
    playlist = []

    for ch in channels_data:
        channel_id = ch.get("id")
        name = ch.get("name", channel_id)
        print(f"🔍 Cari stream {name}...")

        try:
            stream_url, logo = get_stream_url_and_logo(channel_id)
            if stream_url:
                playlist.append({"name": name, "url": stream_url, "logo": logo})
                print(f"✅ {name}: {stream_url}")
            else:
                errors.append(f"{name} ({channel_id}) -> Stream not found")
                print(f"⚠️ {name}: stream tidak ditemukan")

        except Exception as e:
            errors.append(f"{name} ({channel_id}) -> Error: {e}")
            print(f"❌ {name}: {e}")

    # Simpan playlist
    save_m3u(playlist)

    # Simpan error log
    if errors:
        with open("errors.log", "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now()}]\n")
            f.write("\n".join(errors) + "\n")

    print("🎉 Playlist berhasil diupdate.")


if __name__ == "__main__":
    main()
