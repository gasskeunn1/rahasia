#!/usr/bin/env python3
# update.py — ambil playlist / stats dari hypera.live dan buat tipikroya.m3u
import os
import requests
import time
from datetime import datetime

API_URL = "https://hypera.live/api/stats"
OUT_M3U = "tipikroya.m3u"
LAST_RESPONSE = "last_response.html"
ERR_LOG = "errors.log"

# --- Ambil cookies dari env (raw string: "k=v; k2=v2; ...") ---
RAW_COOKIES = os.getenv("HYPERA_COOKIES", "").strip()
if not RAW_COOKIES:
    print("ERROR: set environment variable HYPERA_COOKIES (format: 'k=v; k2=v2; ...')")
    raise SystemExit(1)

def parse_cookies(raw):
    d = {}
    for part in raw.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        k, v = part.split("=", 1)
        d[k.strip()] = v.strip()
    return d

COOKIES = parse_cookies(RAW_COOKIES)

# --- Headers meniru browser (sesuaikan jika perlu) ---
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://hypera.live/premium",
    "Origin": "https://hypera.live",
    # optional: remove if causing issues
    # "Sec-Fetch-Site": "same-origin",
    # "Sec-Fetch-Mode": "cors",
}

def append_error(msg):
    with open(ERR_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.utcnow().isoformat()}] {msg}\n")

def try_fetch(url=API_URL, retries=3, wait=2):
    session = requests.Session()
    session.headers.update(HEADERS)
    # attach cookies to session
    for k, v in COOKIES.items():
        session.cookies.set(k, v, domain="hypera.live", path="/")

    last_exc = None
    for attempt in range(1, retries+1):
        try:
            resp = session.get(url, timeout=15, allow_redirects=True)
            # save raw response for debugging
            with open(LAST_RESPONSE, "w", encoding="utf-8") as f:
                f.write(resp.text)
            return resp
        except requests.RequestException as e:
            last_exc = e
            print(f"[attempt {attempt}] request error: {e}")
            time.sleep(wait)
    raise last_exc

def build_m3u_from_json(data):
    # API kemungkinan mengembalikan {"channels":[{...}, ...]}
    channels = data.get("channels") if isinstance(data, dict) else None
    # if top-level is array of channels:
    if channels is None and isinstance(data, list):
        channels = data
    if not channels:
        return None, 0

    lines = ["#EXTM3U"]
    added = 0
    for ch in channels:
        # prefer name fields
        name = ch.get("name") or ch.get("schedule_en") or ch.get("schedule") or ch.get("id")
        # poster keys may vary
        poster = ch.get("poster") or ch.get("logo") or ch.get("image") or ""
        # try common keys for stream url
        url = ch.get("url") or ch.get("stream") or ch.get("m3u8") or ch.get("stream_url") or ch.get("hls")
        if not url:
            # if channel dict contains nested manifest/links, try scan for any http...m3u8
            for v in ch.values():
                if isinstance(v, str) and ".m3u8" in v:
                    url = v
                    break
        if not url:
            continue
        # normalize protocol-relative
        if url.startswith("//"):
            url = "https:" + url
        lines.append(f'#EXTINF:-1 tvg-logo="{poster}",{name}')
        lines.append(url)
        added += 1
    return "\n".join(lines), added

def main():
    try:
        resp = try_fetch()
    except Exception as e:
        print("Gagal request:", e)
        append_error(f"request failed: {e}")
        return

    ctype = resp.headers.get("content-type", "").lower()
    text = resp.text.strip()

    # 1) jika API mengembalikan JSON
    if "application/json" in ctype or (text.startswith("{") or text.startswith("[")):
        try:
            data = resp.json()
        except Exception as e:
            print("Gagal decode JSON:", e)
            append_error(f"json decode error: {e}")
            # last_response.html sudah disimpan
            return

        m3u_text, count = build_m3u_from_json(data)
        if m3u_text and count > 0:
            with open(OUT_M3U, "w", encoding="utf-8") as f:
                f.write(m3u_text)
            print(f"Playlist berhasil dibuat: {OUT_M3U} ({count} channel)")
            return
        else:
            print("JSON OK tapi tidak menemukan link m3u8 di objek channels.")
            append_error("JSON OK but no m3u8 found")
            return

    # 2) jika server langsung mengembalikan playlist text (.m3u)
    if text.startswith("#EXTM3U") or "application/vnd.apple.mpegurl" in ctype or "mpegurl" in ctype:
        with open(OUT_M3U, "w", encoding="utf-8") as f:
            f.write(resp.text)
        print(f"Playlist (raw) disimpan ke {OUT_M3U}")
        return

    # 3) lainnya: simpan response untuk debugging
    print("Respon tidak dikenali, simpan last_response.html untuk debug.")
    append_error("Unexpected response; saved last_response.html")
    # last_response.html sudah ditulis in try_fetch

if __name__ == "__main__":
    main()
