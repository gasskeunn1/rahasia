import os
import requests

URL = "https://hypera.live/api/stats"
COOKIES = os.getenv("HYPERA_COOKIES", "")

headers = {
    "User-Agent": "Mozilla/5.0",
    "Cookie": COOKIES,
}

try:
    resp = requests.get(URL, headers=headers, timeout=20)
    resp.raise_for_status()

    # simpan raw response selalu
    with open("last_response.html", "wb") as f:
        f.write(resp.content)

    # cek tipe konten
    if "application/json" in resp.headers.get("Content-Type", ""):
        data = resp.json()
        print("✅ Data JSON berhasil diambil:", list(data.keys())[:5])
    else:
        print("⚠️ Respon bukan JSON, cek last_response.html")

except Exception as e:
    with open("errors.log", "a") as log:
        log.write(f"Error: {e}\n")
    print(f"❌ Gagal request: {e}")
