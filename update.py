import requests
import re
import os
from datetime import datetime

BASE_URL = "https://hypera.live"

def get_channels():
    """Ambil daftar channel dari API stats"""
    url = f"{BASE_URL}/api/stats"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json().get("channels", [])

def get_stream_url_and_logo(channel_id):
    """Cari link m3u8 + poster dari halaman channel"""
    url = f"{BASE_URL}/{channel_id}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    html = r.text

    # Cari m3u8 (tokenized)
    m3u8_match = re.search(r'(https.*?\.m3u8[^"\'\s<]+)', html)
    stream_url = m3u8_match.group(1) if m3u8_match else None

    # Cari poster (logo jpg/png/webp)
    poster_match = re.search(r'(https.*?\.(?:jpg|png|webp))', html)
    poster_url = poster_match.group(1) if poster_match else None

    return stream_url, poster_url

def save_m3u(channels, filename):
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

def save_index_html(channels, filename="index.html"):
    """Simpan daftar channel ke HTML untuk dipreview"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html><head><meta charset='utf-8'><title>Playlist</title></head><body>")
        f.write("<h1>Daftar Channel</h1><ul>")
        for ch in channels:
            logo = f"<img src='{ch['logo']}' width='50'>" if ch.get("logo") else ""
            f.write(f"<li>{logo} {ch['name']}</li>")
        f.write("</ul></body></html>")

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

    if not playlist:
        print("❌ Tidak ada channel valid, skip save.")
        return

    # Simpan playlist utama
    save_m3u(playlist, "playlist.m3u")

    # Simpan playlist versi random (timestamp)
    ts_name = f"playlist_{int(datetime.now().timestamp())}.m3u"
    save_m3u(playlist, ts_name)

    # Simpan index.html
    save_index_html(playlist)

    # Simpan error log
    if errors:
        with open("errors.log", "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now()}]\n")
            f.write("\n".join(errors) + "\n")

    print("🎉 Playlist berhasil diupdate.")

if __name__ == "__main__":
    main()
