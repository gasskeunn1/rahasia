import requests
import time

# URL API Hypera
API_URL = "https://hypera.live/api/stats"
M3U_FILE = "tipikroya.m3u"

def fetch_data(retries=3, delay=2):
    """Fetch JSON data from API with retries."""
    headers = {"User-Agent": "Mozilla/5.0"}  # tambahkan header kalau perlu
    for _ in range(retries):
        try:
            resp = requests.get(API_URL, headers=headers, timeout=10)
            if resp.status_code != 200:
                print(f"HTTP {resp.status_code}, retrying...")
                time.sleep(delay)
                continue
            return resp.json()
        except (requests.RequestException, ValueError) as e:
            print(f"Error: {e}, retrying...")
            time.sleep(delay)
    raise RuntimeError("Gagal ambil data dari API.")

def generate_m3u(data):
    """Generate M3U playlist from API JSON."""
    lines = ["#EXTM3U"]
    for ch in data.get("channels", []):
        name = ch.get("name") or ch.get("schedule") or "Unknown"
        poster = ch.get("poster") or ""
        url = ch.get("stream") or ch.get("m3u8") or ""
        if not url:
            continue  # skip channel tanpa link
        extinf = f'#EXTINF:-1 tvg-logo="{poster}",{name}'
        lines.append(extinf)
        lines.append(url)
    return "\n".join(lines)

def main():
    data = fetch_data()
    m3u_content = generate_m3u(data)
    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)
    print(f"Playlist berhasil diperbarui: {M3U_FILE}")

if __name__ == "__main__":
    main()
