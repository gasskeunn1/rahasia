import requests

# --- CONFIG ---
url_api = "https://hypera.live/api/stats"
output_file = "tipikroya.m3u"

# Ganti dengan cookie/token milikmu
cookies = {
    "huid_jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "huid": "okrz1d5b4u",
    "_ga": "GA1.1.372946411.1759065554",
    "cf_clearance": "vS58nSRrazu76unKcH5WtoTO4lXRHEpRQQYYSL0go84..."
}

def fetch_channels():
    try:
        resp = requests.get(url_api, cookies=cookies, timeout=10)
        data = resp.json()
        return data.get("channels", [])
    except Exception as e:
        print("Gagal mengambil data:", e)
        print("Isi response (untuk debug):", resp.text[:200])
        return []

def build_m3u(channels):
    m3u_lines = ['#EXTM3U']
    for ch in channels:
        name = ch.get("name") or ch.get("schedule") or ch.get("id")
        poster = ch.get("poster") or ""
        link = ch.get("stream") or ch.get("m3u8") or ""
        if link:
            m3u_lines.append(f'#EXTINF:-1 tvg-logo="{poster}",{name}')
            m3u_lines.append(link)
    return "\n".join(m3u_lines)

def main():
    channels = fetch_channels()
    if not channels:
        print("Tidak ada channel yang diambil.")
        return
    m3u_content = build_m3u(channels)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(m3u_content)
    print(f"Playlist berhasil diperbarui: {output_file} ({len(channels)} channel)")

if __name__ == "__main__":
    main()
