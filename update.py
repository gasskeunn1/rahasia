import os
import requests
import json

M3U_FILE = "tipikroya.m3u"
API_URL = "https://hypera.live/api/stats"

def fetch_channels():
    cookies = {}
    cookie_str = os.getenv("HYPERA_COOKIES")
    if not cookie_str:
        print("ERROR: HYPERA_COOKIES environment variable not set or empty.")
        return []

    # parsing cookie string ke dict
    for part in cookie_str.split(";"):
        if "=" in part:
            key, value = part.strip().split("=", 1)
            cookies[key] = value

    try:
        resp = requests.get(API_URL, cookies=cookies, timeout=10)
        data = resp.json()
    except json.JSONDecodeError:
        print("Gagal decode JSON, response:", resp.text[:200])
        return []
    except Exception as e:
        print("Gagal mengambil data:", e)
        return []

    channels = []
    for ch in data.get("channels", []):
        name = ch.get("name")
        poster = ch.get("poster", "")
        url = ch.get("url")  # pastikan di API keynya 'url' adalah m3u8
        if name and url:
            channels.append({"name": name, "poster": poster, "url": url})
    return channels

def save_m3u(channels):
    if not channels:
        print("Tidak ada channel yang diambil.")
        return

    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in channels:
            f.write(f'#EXTINF:-1 tvg-logo="{ch["poster"]}",{ch["name"]}\n')
            f.write(f'{ch["url"]}\n')
    print(f"{M3U_FILE} berhasil diperbarui.")

def main():
    channels = fetch_channels()
    save_m3u(channels)

if __name__ == "__main__":
    main()
