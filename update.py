import requests

# ===== CONFIG =====
API_URL = "https://hypera.live/api/stats"
OUTPUT_FILE = "tipikroya.m3u"
COOKIES = {
    "huid_jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodWlkIjoib2tyejFkNWI0dSIsImlzc3VlZF9hdCI6MTc1OTA2NTU1MzE5NiwiaWF0IjoxNzU5MDY1NTUzLCJleHAiOjE5MTY4NTM1NTN9.INijOj-ebg2a9cXlgXDhe5hclGeZqUWObU80EK8tooc",
    "huid": "okrz1d5b4u",
    "_ga": "GA1.1.372946411.1759065554",
    "cf_clearance": "vS58nSRrazu76unKcH5WtoTO4lXRHEpRQQYYSL0go84-1759080602-1.2.1.1-Xya0Q18K3Vpf61WUopEeFJ6.cHZqyfVUoP3z3X_tzTlkzDMbABTb9BvDjn_nXHoX3KuTkbYOzCv4H6VF2nqARlNCPse1c8J7HKFBcru8WHxBS8lxRIdXttAT5hO8dw2NpSxXCCeETPmM9fkwZkmK7sjN5L_sp409gSqjiWK0aT3vHmk3di7rpi4ucki8sW13UduC2R3utzULJs0KcyHLOTE0ns2.Whyc40jSh5h1Oi8",
    "_ga_XC3J1X1K5E": "GS2.1.s1759080572$o4$g1$t1759080661$j57$l0$h0"
}

# ===== FUNCTION =====
def fetch_channels():
    resp = requests.get(API_URL, cookies=COOKIES)
    if resp.status_code != 200:
        print("Gagal mengambil data:", resp.status_code)
        return []

    try:
        data = resp.json()
    except Exception as e:
        print("Gagal decode JSON:", e)
        return []

    channels = []
    for ch in data.get("channels", []):
        name = ch.get("name") or ch.get("id")
        poster = ch.get("poster") or ""
        m3u8 = ch.get("m3u8")  # field m3u8 sesuai API Hypera
        if m3u8:
            channels.append({
                "name": name,
                "poster": poster,
                "m3u8": m3u8
            })
    return channels

def save_m3u(channels):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in channels:
            f.write(f'#EXTINF:-1 tvg-logo="{ch["poster"]}",{ch["name"]}\n')
            f.write(f'{ch["m3u8"]}\n')
    print(f"Playlist berhasil diperbarui: {OUTPUT_FILE} ({len(channels)} channel)")

# ===== MAIN =====
def main():
    channels = fetch_channels()
    if channels:
        save_m3u(channels)
    else:
        print("Tidak ada channel yang diambil.")

if __name__ == "__main__":
    main()
