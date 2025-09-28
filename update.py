import asyncio
from playwright.async_api import async_playwright
import os
import json

API_URL = "https://hypera.live/api/stats"

# Ambil cookies dari env variable agar aman di GitHub
COOKIES_RAW = os.getenv("HYPERA_COOKIES", "")
if not COOKIES_RAW:
    raise ValueError("ERROR: HYPERA_COOKIES environment variable not set or empty.")

# Parsing cookies JSON dari env
COOKIES = json.loads(COOKIES_RAW)

async def fetch_channels():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies(COOKIES)
        page = await context.new_page()
        await page.goto(API_URL, wait_until="networkidle")
        
        try:
            data_json = await page.evaluate("() => JSON.parse(document.body.innerText)")
            print("Jumlah channel:", len(data_json))
            
            with open("tipikroya.m3u", "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for ch in data_json:
                    f.write(f"#EXTINF:-1,{ch['name']}\n{ch['url']}\n")
            print("File tipikroya.m3u berhasil dibuat.")
        except Exception as e:
            print("Gagal decode JSON:", e)

        await browser.close()

asyncio.run(fetch_channels())
