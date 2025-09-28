import requests

API_URL = "https://hypera.live/api/stats"
OUTPUT_FILE = "tipikroya.m3u"

# Gunakan cookie dari Anda
COOKIES = {
    "huid_jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodWlkIjoib2tyejFkNWI0dSIsImlzc3VlZF9hdCI6MTc1OTA2NTU1MzE5NiwiaWF0IjoxNzU5MDY1NTUzLCJleHAiOjE5MTY4NTM1NTN9.INijOj-ebg2a9cXlgXDhe5hclGeZqUWObU80EK8tooc",
    "huid": "okrz1d5b4u",
    "_ga": "GA1.1.372946411.1759065554",
    "cf_clearance": "vS58nSRrazu76unKcH5WtoTO4lXRHEpRQQYYSL0go84-1759080602-1.2.1.1-Xya0Q18K3Vpf61WUopEeFJ6.cHZqyfVUoP3z3X_tzTlkzDMbABTb9BvDjn_nXHoX3KuTkbYOzCv4H6VF2nqARlNCPse1c8J7HKFBcru8WHxBS8lxRIdXttAT5hO8dw2NpSxXCCeETPmM9fkwZkmK7sjN5L_sp409gSqjiWK0aT3vHmk3di7rpi4ucki8sW13UduC2R3utzULJs0KcyHLOTE0ns2.Whyc40jSh5h1Oi8",
    "_ga_XC3J1X1K5E": "GS2.1.s1759080572$o4$g1$t1759080661$j57$l0$h0"
}

def fetch_channels():
    try:
        resp = requests.get(API_URL, cookies=COOKIES)
        data = resp.json()
        return data.get("channels", [])
    except Exception as e:
        print("Gagal decode JSON, response:", resp.text[:300])
        return []

def build_m3u(channels):
    lines = ["#EXTM3U\n"]
    for ch in channels:
        name = ch.get("name") or ch.get("id")
        logo = ch.get("poster") or ""
        url = ch.get("url")  # pastikan ini m3u8
        if url:
            lines.append(f'#EXTINF:-1 tvg-logo="{logo}",{name}')
            lines.append(url)
    return "\n".join(lines)

def main():
    channels = fetch_channels()
    if not channels:
        print("Tidak ada channel yang diambil.")
        return
    m3u_content = build_m3u(channels)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(m3u_content)
    print(f"Playlist berhasil diperbarui: {OUTPUT_FILE} ({len(channels)} channel)")

if __name__ == "__main__":
    main()
