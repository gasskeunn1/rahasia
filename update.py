import os
import requests

# Ambil cookie dari GitHub Secrets
cookies_raw = os.environ.get("HYPERA_COOKIE", "")
COOKIES = {}
for c in cookies_raw.split(";"):
    if "=" in c:
        k, v = c.strip().split("=", 1)
        COOKIES[k] = v

HEADERS = {"User-Agent": "Mozilla/5.0"}

API_URL = "https://hypera.live/api/stats"
OUTPUT_FILE = "tipikroya.m3u"

def fetch_channels():
    try:
        resp = requests.get(API_URL, cookies=COOKIES, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        channels = []
        for ch in data.get("channels", []):
            name = ch.get("name")
            poster = ch.get("poster")
            link = ch.get("stream")  # sesuaikan field stream / m3u8
            if name and link:
                channels.append({
                    "name": name,
                    "poster": poster or "",
                    "link": link
                })
        return channels
    except Exception as e:
        print("Gagal mengambil data:", e)
        return []

def generate_m3u(channels):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in channels:
            f.write(f'#EXTINF:-1 tvg-logo="{ch["poster"]}",{ch["name"]}\n')
            f.write(f'{ch["link"]}\n')
    print(f"Playlist berhasil diperbarui: {OUTPUT_FILE} ({len(channels)} channel)")

def main():
    channels = fetch_channels()
    if not channels:
        print("Tidak ada channel yang diambil.")
        return
    generate_m3u(channels)

if __name__ == "__main__":
    main()
