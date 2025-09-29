import asyncio
from playwright.async_api import async_playwright
import os

# URL langsung ke playlist M3U
PLAYLIST_URL = "https://hypera.live/path/to/playlist.m3u"

COOKIES_RAW = os.getenv("HYPERA_COOKIES", "")
if not COOKIES_RAW:
    raise ValueError("ERROR: HYPERA_COOKIES environment variable not set or empty.")

def parse_cookies(raw):
    cookies = []
    for part in raw.split(";"):
        if "=" not in part:
            continue
        name, value = part.strip().split("=", 1)
        cookies.append({
            "name": name,
            "value": value,
            "domain": "hypera.live",
            "path": "/"
        })
    return cookies

COOKIES = parse_cookies(COOKIES_RAW)

async def fetch_playlist():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies(COOKIES)
        page = await context.new_page()

        # buka playlist URL
        resp = await page.goto(PLAYLIST_URL)
        text = await resp.text()

        await browser.close()
        return text

async def main():
    try:
        playlist = await fetch_playlist()
        if not playlist.strip():
            print("Playlist kosong!")
            return

        # simpan ke file .m3u
        with open("tipikroya.m3u", "w", encoding="utf-8") as f:
            f.write(playlist)
        print("✅ Playlist berhasil diambil dan disimpan ke tipikroya.m3u")
    except Exception as e:
        print("❌ Gagal:", e)

if __name__ == "__main__":
    asyncio.run(main())
