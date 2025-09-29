#!/usr/bin/env python3
# update.py — ambil playlist/stat dari hypera.live menggunakan header Cookie string
import os
import requests
import time
from datetime import datetime

API_URL = "https://hypera.live/api/stats"
OUT_M3U = "tipikroya.m3u"
LAST_HTML = "last_response.html"
ERR_LOG = "errors.log"

COOKIE_STR = os.getenv("HYPERA_COOKIES", "").strip()
if not COOKIE_STR:
    print("ERROR: set HYPERA_COOKIES (raw cookie string like 'k=v; k2=v2; ...').")
    raise SystemExit(1)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://hypera.live/premium",
    "Origin": "https://hypera.live",
    "Cookie": COOKIE_STR,
}

def append_error(msg):
    ts = datetime.utcnow().isoformat()
    with open(ERR_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

def fetch_url(url, retries=3, wait=2):
    s = requests.Session()
    s.headers.update(HEADERS)
    last_exc = None
    for attempt in range(1, retries+1):
        try:
            r = s.get(url, timeout=15, allow_redirects=True)
            # simpan raw response untuk debug
            with open(LAST_HTML, "w", encoding="utf-8") as fh:
                fh.write(r.text)
            return r
        except requests.RequestException as e:
            last_exc = e
            print(f"[attempt {attempt}] request error: {e}")
            time.sleep(wait)
    raise last_exc

def build_m3u_from_json(obj):
    # obj bisa dict {'channels':[...]} atau list [...]
    channels = None
    if isinstance(obj, dict):
        channels = obj.get("channels")
    elif isinstance(obj, list):
        channels = obj
    if not channels:
        return None, 0

    lines = ["#EXTM3U"]
    added = 0
    for ch in channels:
        # cari nama
        name = ch.get("name") or ch.get("schedule_en") or ch.get("schedule") or ch.get("id") or "Unknown"
        # cari poster
        poster = ch.get("poster") or ch.get("logo") or ch.get("image") or ""
        # berbagai kemungkinan key untuk stream
        url = ch.get("url") or ch.get("stream") or ch.get("m3u8") or ch.get("stream_url") or ch.get("hls")
        if not url:
            # coba scan any str value containing .m3u8
            for v in ch.values():
                if isinstance(v, str) and ".m3u8" in v:
                    url = v
                    break
        if not url:
            continue
        if url.startswith("//"):
            url = "https:" + url
        lines.append(f'#EXTINF:-1 tvg-logo="{poster}",{name}')
        lines.append(url)
        added += 1
    return "\n".join(lines), added

def main():
    try:
        resp = fetch_url(API_URL)
    except Exception as e:
        print("Gagal request:", e)
        append_error(f"fetch_url error: {e}")
        return 1

    ctype = resp.headers.get("content-type", "").lower()
    text = resp.text.strip()

    # Jika JSON
    if "application/json" in ctype or text.startswith("{") or text.startswith("["):
        try:
            data = resp.json()
        except Exception as e:
            print("Gagal decode JSON:", e)
            append_error(f"json decode: {e}")
            return 1

        m3u_text, count = build_m3u_from_json(data)
        if m3u_text and count > 0:
            with open(OUT_M3U, "w", encoding="utf-8") as f:
                f.write(m3u_text)
            print(f"Playlist berhasil dibuat: {OUT_M3U} ({count} channel)")
            return 0
        else:
            print("JSON OK tapi tidak menemukan link m3u8 di data.")
            append_error("JSON OK but no m3u8 found")
            return 1

    # Jika server langsung mengembalikan playlist (.m3u)
    if text.startswith("#EXTM3U") or "mpegurl" in ctype or "application/vnd.apple.mpegurl" in ctype:
        with open(OUT_M3U, "w", encoding="utf-8") as f:
            f.write(resp.text)
        print(f"Playlist (raw) disimpan ke {OUT_M3U}")
        return 0

    # Lainnya -> simpan last_response.html (sudah dilakukan) dan log error
    print("Respon tidak dikenali (lihat last_response.html).")
    append_error("Unexpected response; saved last_response.html")
    return 1

if __name__ == "__main__":
    exit(main())
