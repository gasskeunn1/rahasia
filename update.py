import requests
import time

url = "https://hypera.live/api/stats"

for i in range(3):  # coba 3 kali
    resp = requests.get(url)
    if resp.status_code == 200:
        try:
            data = resp.json()
            break
        except Exception as e:
            print("JSON decode error, retrying...", e)
    else:
        print(f"HTTP error {resp.status_code}, retrying...")
    time.sleep(2)
else:
    print("Gagal ambil data JSON, hentikan script.")
    exit(1)

# lanjut buat M3U
lines = ["#EXTM3U"]

for ch in data.get("channels", []):
    name = ch.get("name", "Unknown")
    poster = ch.get("poster", "")
    m3u8 = ch.get("stream", {}).get("url", "")
    if m3u8:
        lines.append(f'#EXTINF:-1 tvg-logo="{poster}",{name}')
        lines.append(m3u8)

with open("tipikroya.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Playlist berhasil diperbarui: tipikroya.m3u")


if __name__ == "__main__":
    main()
