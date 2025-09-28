import requests
import datetime

API_URL = "https://hypera.live/api/stats"
OUTPUT_FILE = "tipikroya.m3u"

# Optional: bisa tambahkan User-Agent supaya tidak ditolak
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def fetch_channels():
    resp = requests.get(API_URL, headers=HEADERS)
    if not resp.text.strip():
        raise RuntimeError("Response kosong, gagal ambil JSON")
    try:
        data = resp.json()
    except ValueError:
        print("Isi response (untuk debug):", resp.text[:500])
        raise
    return data.get("channels", [])

def generate_m3u(channels):
    lines = ["#EXTM3U"]
    for ch in channels:
        name = ch.get("schedule_en") or ch.get("schedule")
        logo = ch.get("poster", "")  # Hypera API kadang ada poster field
        url = ch.get("stream_url")   # Pastikan API mengembalikan link m3u8
        if not url:
            continue
        extinf = f'#EXTINF:-1 tvg-logo="{logo}" tvg-name="{name}",{name}'
        lines.append(extinf)
        lines.append(url)
    return "\n".join(lines)

def main():
    channels = fetch_channels()
    if not channels:
        print("Tidak ada channel, playlist tidak diperbarui.")
        return

    m3u_content = generate_m3u(channels)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print(f"🎉 Playlist berhasil diperbarui: {OUTPUT_FILE} ({len(channels)} channel)")

if __name__ == "__main__":
    main()
