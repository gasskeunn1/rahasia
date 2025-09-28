import requests
import os

# URL API Hypera
API_URL = "https://hypera.live/api/stats"

# File M3U output
OUTPUT_FILE = "tipikroya.m3u"

def fetch_channels():
    resp = requests.get(API_URL)
    resp.raise_for_status()
    data = resp.json()
    return data.get("channels", [])

def generate_m3u(channels):
    lines = ["#EXTM3U\n"]
    for ch in channels:
        name = ch.get("name", ch.get("id", "Unknown"))
        logo = ch.get("poster", "")  # poster URL
        m3u8_url = ch.get("url", "")
        if not m3u8_url:
            continue
        lines.append(f'#EXTINF:-1 tvg-logo="{logo}" group-title="Korea", {name}')
        lines.append(m3u8_url)
    return "\n".join(lines)

def main():
    try:
        channels = fetch_channels()
        m3u_content = generate_m3u(channels)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(m3u_content)
        print(f"🎉 Playlist berhasil diperbarui: {OUTPUT_FILE} ({len(channels)} channel)")
    except Exception as e:
        print("❌ Gagal memperbarui playlist:", e)

if __name__ == "__main__":
    main()
