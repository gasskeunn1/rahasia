#!/usr/bin/env python3
# update.py — generate tipikroya.m3u from hypera.live using cookies (from env HYPERA_COOKIES)
import os
import requests
import re
import time
from datetime import datetime

API_STATS = "https://hypera.live/api/stats"
OUT_M3U = "tipikroya.m3u"
LAST_RESP = "last_response.html"
ERROR_LOG = "errors.log"

# --- Helpers ---
def parse_cookie_string(cookie_str):
    cookies = {}
    if not cookie_str:
        return cookies
    for part in cookie_str.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            k,v = part.split("=",1)
            cookies[k.strip()] = v.strip()
    return cookies

# load cookie string from env (set in GitHub Actions as secret HYPERA_COOKIES)
COOKIE_STR = os.environ.get("HYPERA_COOKIES", "")
COOKIES = parse_cookie_string(COOKIE_STR)

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/140.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*"
}

# --- Fetch API stats robustly ---
def fetch_stats(retries=3, wait=2):
    last_exc = None
    session = requests.Session()
    session.headers.update(HEADERS)
    try:
        session.cookies.update(COOKIES)
    except Exception:
        pass

    for attempt in range(1, retries+1):
        try:
            resp = session.get(API_STATS, timeout=10, allow_redirects=True)
            # save raw for debug
            with open(LAST_RESP, "w", encoding="utf-8") as f:
                f.write(resp.text)
            if resp.status_code != 200:
                last_msg = f"HTTP {resp.status_code}"
                # 401/403 often unauthorized
                print(f"[attempt {attempt}] {last_msg}")
                last_exc = RuntimeError(last_msg)
                time.sleep(wait)
                continue
            # try parse json
            try:
                data = resp.json()
                return data
            except ValueError as ve:
                # not json — probably Unauthorized HTML
                print(f"[attempt {attempt}] JSON decode error: {ve}")
                last_exc = ve
                time.sleep(wait)
                continue
        except requests.exceptions.TooManyRedirects as e:
            print(f"[attempt {attempt}] Too many redirects: {e}")
            last_exc = e
            break
        except requests.RequestException as e:
            print(f"[attempt {attempt}] RequestException: {e}")
            last_exc = e
            time.sleep(wait)
    # after retries
    raise last_exc or RuntimeError("Failed to fetch stats")

# --- If API contains no direct m3u8, try fetch channel page and extract .m3u8 url ---
def fetch_stream_from_channel_page(session, channel_id):
    # try https://hypera.live/{channel_id}
    url = f"https://hypera.live/{channel_id}"
    try:
        resp = session.get(url, timeout=8)
        text = resp.text
        # search for .m3u8 tokenized links
        m = re.search(r'(https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*)', text)
        if m:
            return m.group(1)
        # sometimes manifest link is in JS with /manifest...
        m2 = re.search(r'(https?://[^\s"\'<>]+/index\.m3u8[^\s"\'<>]*)', text)
        if m2:
            return m2.group(1)
    except Exception:
        return None
    return None

# --- Build playlist ---
def build_m3u_from_stats(data):
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(COOKIES)

    channels = data.get("channels", [])
    lines = ["#EXTM3U"]
    added = 0

    for ch in channels:
        # prefer english schedule name, fallback to schedule or id
        name = ch.get("name") or ch.get("schedule_en") or ch.get("schedule") or ch.get("id")
        poster = ch.get("poster") or ch.get("logo") or ""
        # try common keys for direct stream url in API
        m3u8 = ch.get("url") or ch.get("stream") or ch.get("m3u8") or ch.get("stream_url") or ch.get("hls")
        if not m3u8:
            # attempt to parse channel page for m3u8
            cid = ch.get("id") or ch.get("channel") or None
            if cid:
                found = fetch_stream_from_channel_page(session, cid)
                if found:
                    m3u8 = found
        # skip if none
        if not m3u8:
            continue
        # ensure it's an absolute https url
        if m3u8.startswith("//"):
            m3u8 = "https:" + m3u8
        lines.append(f'#EXTINF:-1 tvg-logo="{poster}",{name}')
        lines.append(m3u8)
        added += 1

    return "\n".join(lines), added

# --- Logging utility ---
def append_error(msg):
    ts = datetime.utcnow().isoformat()
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

# --- Main ---
def main():
    if not COOKIES:
        print("ERROR: HYPERA_COOKIES environment variable not set or empty.")
        append_error("Missing HYPERA_COOKIES")
        return 1

    try:
        data = fetch_stats(retries=4, wait=2)
    except Exception as e:
        print("Gagal mengambil data:", e)
        append_error(f"fetch_stats error: {e}")
        # last_response.html already saved by fetch_stats for debug
        return 1

    m3u_text, count = build_m3u_from_stats(data)
    if count == 0:
        print("Tidak ada channel yang ditemukan untuk ditulis ke M3U.")
        append_error("No channels found or no m3u8 links.")
        return 1

    with open(OUT_M3U, "w", encoding="utf-8") as f:
        f.write(m3u_text)

    print(f"Playlist berhasil diperbarui: {OUT_M3U} ({count} channel)")
    return 0

if __name__ == "__main__":
    exit(main())
