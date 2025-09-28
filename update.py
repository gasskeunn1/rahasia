import requests
import json
from datetime import datetime

# Contoh endpoint (harus disesuaikan dengan yang bisa diakses)
API_URL = "https://hypera.live/api/stats"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Authorization": "Bearer <TOKEN_ANDA>",  # jika perlu token
}

M3U_FILE = "tipikroya.m3u"

def fetch_channels():
    resp = requests.get(API_URL, headers=HEADERS)
    resp.raise_for_status()

    # Cek apakah JSON valid
    try:
        data = resp.json()
    except json.JSONDecodeError:
        print("Gagal decode JSON, response:", resp.text[:200])
        return []

    channels = []
    for ch in data.get("channels", []):
        if "m3u8_url" in ch:  # ganti sesuai key yang benar
            channels.append({
                "name": ch.get("name") or ch.get("id"),
                "poster": ch.get("poster") or "",
                "url": ch.get("m3u8_url")
            })
    return channels

def generate_m3u(channels):
    lines = ["#EXTM3U"]
    for ch in channels:
        lines.append(f'#EXTINF:-1 tvg-logo="{ch["poster"]}",{ch["name"]}')
        lines.append(ch["url"])
    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Playlist berhasil diperbarui: {M3U_FILE} ({len(channels)} channel)")

def main():
    channels = fetch_channels()
    if channels:
        generate_m3u(channels)
    else:
        print("Tidak ada channel yang diambil.")

if __name__ == "__main__":
    main()
