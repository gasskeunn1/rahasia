import requests

# URL API Hypera
url_api = "https://hypera.live/api/stats"

# Cookies dari browser (harus update kalau expired)
cookies = {
    "_ga": "GA1.1.372946411.1759065554",
    "_ga_XC3J1X1K5E": "GS2.1.s1759080572$o4$g1$t1759081807$j59$l0$h0",
    "cf_clearance": "vS58nSRrazu76unKcH5WtoTO4lXRHEpRQQYYSL0go84-1759080602-1.2.1.1-Xya0Q18K3Vpf61WUopEeFJ6.cHZqyfVUoP3z3X_tzTlkzDMbABTb9BvDjn_nXHoX3KuTkbYOzCv4H6VF2nqARlNCPse1c8J7HKFBcru8WHxBS8lxRIdXttAT5hO8dw2NpSxXCCeETPmM9fkwZkmK7sjN5L_sp409gSqjiWK0aT3vHmk3di7rpi4ucki8sW13UduC2R3utzULJs0KcyHLOTE0ns2.Whyc40jSh5h1Oi8",
    "huid": "okrz1d5b4u",
    "huid_jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodWlkIjoib2tyejFkNWI0dSIsImlzc3VlZF9hdCI6MTc1OTA2NTU1MzE5NiwiaWF0IjoxNzU5MDY1NTUzLCJleHAiOjE5MTY4NTM1NTN9.INijOj-ebg2a9cXlgXDhe5hclGeZqUWObU80EK8tooc"
}

def fetch_channels():
    try:
        resp = requests.get(url_api, cookies=cookies, timeout=10)
        data = resp.json()
        return data.get("channels", [])
    except Exception as e:
        print("Gagal mengambil data:", e)
        print("Isi response (untuk debug):", getattr(resp, "text", "")[:200])
        return []

def generate_m3u(channels):
    with open("tipikroya.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in channels:
            name = ch.get("name") or ch.get("id")
            poster = ch.get("poster") or ""
            link = ch.get("m3u8_link")
            if link:
                f.write(f'#EXTINF:-1 tvg-logo="{poster}",{name}\n')
                f.write(f'{link}\n')
    print(f"Playlist berhasil diperbarui: tipikroya.m3u ({len(channels)} channel)")

def main():
    channels = fetch_channels()
    if channels:
        generate_m3u(channels)
    else:
        print("Tidak ada channel yang diambil.")

if __name__ == "__main__":
    main()
