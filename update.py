import requests

# =========================
# KONFIGURASI
# =========================
API_URL = "https://hypera.live/api/stats"

# Cookies dari browser
COOKIES = {
    "huid_jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJodWlkIjoib2tyejFkNWI0dSIsImlzc3VlZF9hdCI6MTc1OTA2NTU1MzE5NiwiaWF0IjoxNzU5MDY1NTUzLCJleHAiOjE5MTY4NTM1NTN9.INijOj-ebg2a9cXlgXDhe5hclGeZqUWObU80EK8tooc",
    "huid": "okrz1d5b4u",
    "_ga": "GA1.1.372946411.1759065554",
    "cf_clearance": "vS58nSRrazu76unKcH5WtoTO4lXRHEpRQQYYSL0go84-1759080602-1.2.1.1-Xya0Q18K3Vpf61WUopEeFJ6.cHZqyfVUoP3z3X_tzTlkzDMbABTb9BvDjn_nXHoX3KuTkbYOzCv4H6VF2nqARlNCPse1c8J7HKFBcru8WHxBS8lxRIdXttAT5hO8dw2NpSxXCCeETPmM9fkwZkmK7sjN5L_sp409gSqjiWK0aT3vHmk3di7rpi4ucki8sW13UduC2R3utzULJs0KcyHLOTE0ns2.Whyc40jSh5h1Oi8",
    "_ga_XC3J1X1K5E": "GS2.1.s1759080572$o4$g1$t1759080661$j57$l0$h0"
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

OUTPUT_FILE = "tipikroya.m3u"

# =========================
# FUNGSI AMBIL CHANNEL
# =========================
def fetch_channels():
    try:
        resp = requests.get(API_URL, cookies=COOKIES, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        channels = data.get("channels", [])
        result = []
        for ch in channels:
            # Pastikan ada link m3u8
            link = ch.get("url") or ch.get("m3u8")  # tergantung key di API
            if not link:
                continue
            result.append({
                "name": ch.get("name") or ch.get("schedule_en") or ch.get("schedule"),
                "poster": ch.get("poster") or "",
                "url": link
            })
        return result
    except Exception as e:
        print("Gagal mengambil data:", e)
        if resp is not None:
            print("Isi response (untuk debug):", resp.text[:500])
        return []

# =========================
# FUNGSI BUAT M3U
# =========================
def generate_m3u(channels):
    lines = ["#EXTM3U"]
    for ch in channels:
        tvg_logo = ch["poster"]
        lines.append(f'#EXTINF:-1 tvg-logo="{tvg_logo}",{ch["name"]}')
        lines.append(ch["url"])
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Playlist berhasil diperbarui: {OUTPUT_FILE} ({len(channels)} channel)")

# =========================
# MAIN
# =========================
def main():
    channels = fetch_channels()
    if not channels:
        print("Tidak ada channel yang diambil.")
        return
    generate_m3u(channels)

if __name__ == "__main__":
    main()
