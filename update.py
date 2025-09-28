# update.py
import asyncio
from playwright.async_api import async_playwright

M3U_FILE = "tipikroya.m3u"
HYPERA_URL = "https://hypera.live/"  # halaman login/home
API_URL = "https://hypera.live/api/stats"  # endpoint JSON

# Ganti dengan cookie dari browser kamu (lihat DevTools > Application > Cookies)
COOKIES = {
    "_ga": "GA1.1.372946411.1759065554",
    "_ga_XC3J1X1K5E": "GS2.1.s1759080572$o4$g1$t1759083444$j60$l0$h0",
    "cf_clearance": "vS58nSRrazu76unKcH5WtoTO4lXRHEpRQQYYSL0go84-1759080602-1.2.1.1-Xya0Q18K3Vpf61WUopEeFJ6.cHZqyfVUoP3z3X_tzTlkzDMbABTb9BvDjn_nXHoX3KuTkbYOzCv4H6VF2nqARlNCPse1c8J7HKFBcru8WHxBS8lxRIdXttAT5hO8dw2NpSxXCCeETPmM9fkwZkmK7sjN5L_sp409gSqjiWK0aT3vHmk3di7rpi4ucki8sW13UduC2R3utzULJs0KcyHLOTE0ns2.Whyc40jSh5h1Oi8",
    "huid": "okrz1d5b4u",
    "huid_jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "passport": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4R0NNIn0..NRikteDN2vm_py_B.Y-v_jc3dvpMdDHH1CZVs2f8HnJnQb94oGFEQV9bcTvKqM4zfO7SHYbIan5nBqm4K335S8LRWnNnGjIrFlw6V16gL68SUWjVRHatN8z0CyJ38eGJ03wvFOoIEET8Tqme93P4gFJdSgCXzLNz5Z2WGSmke8zRMZFd_qn2fdT98vsYf4j1EaTwyLgh_5aK0qvbNpMQHSCt-YGQp9aMOXI03OCUmsd_Jk7VlyY8w8J34cNNFIFJeO8fxr01f0VFQmrTSkyOzopryxiz8TchRLGJx6dPAbFrcpaLj3ZCQUOCpuDvRg6MaKX9PdNM2cGxrbBiVWD4Hhumi21cPs7l8A_CubnO8NRP3y1E7Bc0Y8ffxx4sBWuWU45zZIHfMyLCwQBtSUeqkNCZH.MeIKmWwZ0UDcOfcy8BXsag",
    "viewTimeToken": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4R0NNIn0..WQTF1zZ5Gn-BuuZC.jfWNe4T9LnXudH6nZW5GLloeTzPfRU_59cG9rpGRoZjgwqYL2C-fNHQ9Wk3MiVZDnVB3Bz6rr9MQXk1Nb2PK1jPIywRM7LlG61PxcbzGy88jnBhDmV-eTc6zAuvVbhQFKHA4HgOqZ2qQVrL5CKmlXYhfmD02yiN1VjNDarIlYJgYmDk85dF_5LjUuWl9iv7v5_xdKRfKqm2NA4haiaAqHv8-LLuTJIM-HQeMR370fgjGAgFvHaj4tDIrPfmVlKDxVJGP85XgopenqB1ztx4As-LOfXyIIq2_Dcg.2k1P0Xwq2IQ6OIb8SCPaKA"
}

async def fetch_channels():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Set cookies agar bisa akses API
        cookies_list = [{"name": k, "value": v, "domain": ".hypera.live", "path": "/"} for k, v in COOKIES.items()]
        await context.add_cookies(cookies_list)
        
        page = await context.new_page()
        await page.goto(API_URL)
        
        try:
            # Ambil JSON dari page
            content = await page.content()
            # Kadang Hypera tetap merender HTML, gunakan evaluate untuk ambil JSON
            data = await page.evaluate("() => JSON.parse(document.body.innerText)")
        except Exception as e:
            print("Gagal decode JSON:", e)
            print("Isi page:", content[:500])
            await browser.close()
            return []
        
        await browser.close()
        return data.get("channels", [])

def generate_m3u(channels):
    with open(M3U_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for ch in channels:
            name = ch.get("name", "Unknown")
            poster = ch.get("poster", "")
            link = ch.get("link", "")
            f.write(f'#EXTINF:-1 tvg-logo="{poster}",{name}\n{link}\n')
    print(f"M3U berhasil dibuat: {M3U_FILE}")

async def main():
    channels = await fetch_channels()
    if channels:
        generate_m3u(channels)
    else:
        print("Tidak ada channel yang diambil.")

if __name__ == "__main__":
    asyncio.run(main())
