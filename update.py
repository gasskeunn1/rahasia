import json
import requests
from datetime import datetime

# --- Konfigurasi ---
JSON_URL = "https://example.com/channels.json"  # ganti dengan URL sumber JSON
OUTPUT_FILE = "tipikroya.m3u"

# --- Ambil data JSON ---
try:
    resp = requests.get(JSON_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()
except Exception as e:
    print("Gagal ambil JSON:", e)
    exit(1)

# --- Mulai tulis file M3U ---
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    f.write(f"# Generated: {datetime.utcnow().isoformat()} UTC\n\n")

    for channel in data.get("channels", []):
        channel_id = channel.get("id")
        channel_name = channel.get("schedule_en") or channel.get("schedule")
        m3u8_url = channel.get("m3u8_url")  # pastikan JSON berisi URL m3u8 terbaru

        if not m3u8_url:
            continue  # skip jika tidak ada URL

        f.write(f"#EXTINF:-1,{channel_name}\n")
        f.write(f"{m3u8_url}\n\n")

print(f"Playlist berhasil diperbarui: {OUTPUT_FILE}")
