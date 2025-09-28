import requests

# URL API Hypera
url_api = "https://hypera.live/api/stats"

# Cookie dari browser (ganti dengan cookie terbaru Anda)
cookies = {
    "huid_jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodWlkIjoib2tyejFkNWI0dSIsImlzc3VlZF9hdCI6MTc1OTA2NTU1MzE5NiwiaWF0IjoxNzU5MDY1NTUzLCJleHAiOjE5MTY4NTM1NTN9.INijOj-ebg2a9cXlgXDhe5hclGeZqUWObU80EK8tooc",
    "huid": "okrz1d5b4u",
    "_ga": "GA1.1.372946411.1759065554",
    "cf_clearance": "vS58nSRrazu76unKcH5WtoTO4lXRHEpRQQYYSL0go84-1759080602-1.2.1.1-Xya0Q18K3Vpf61WUopEeFJ6.cHZqyfVUoP3z3X_tzTlkzDMbABTb9BvDjn_nXHoX3KuTkbYOzCv4H6VF2nqARlNCPse1c8J7HKFBcru8WHxBS8lxRIdXttAT5hO8dw2NpSxXCCeETPmM9fkwZkmK7sjN5L_sp409gSqjiWK0aT3vHmk3di7rpi4ucki8sW13UduC2R3utzULJs0KcyHLOTE0ns2.Whyc40jSh5h1Oi8"
}

# File M3U output
m3u_file = "tipikroya.m3u"

# Fungsi ambil channel
def fetch_channels():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/140.0.0.0 Safari/537.36"
        }
        resp = requests.get(url_api, cookies=cookies, headers=headers, timeout=10, allow_redirects=False)
        resp.raise_for_status()
        data = resp.json()
        return data.get("channels", [])
    except requests.exceptions.TooManyRedirects:
        print("Gagal: terlalu banyak redirect")
        return []
    except requests.exceptions.RequestException as e:
        print("Gagal mengambil data:", e)
        return []
    except ValueError:
        print("Gagal decode JSON, response preview:", resp.text[:200] if 'resp' in locals() else "Tidak ada response")
        return []

# Fungsi generate M3U
def generate_m3u(channels):
    lines = ["#EXTM3U\n"]
    for ch in channels:
        name = ch.get("schedule_en") or ch.get("schedule") or "Unknown"
        poster = ch.get("poster") or ""
        m3u8_url = ch.get("stream") or ch.get("url") or ""
        if not m3u8_url:
            continue
        lines.append(f'#EXTINF:-1 tvg-logo="{poster}",{name}')
        lines.append(m3u8_url)
    with open(m3u_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Playlist berhasil diperbarui: {m3u_file} ({len(channels)} channel)")

def main():
    channels = fetch_channels()
    if not channels:
        print("Tidak ada channel yang diambil.")
        return
    generate_m3u(channels)

if __name__ == "__main__":
    main()
