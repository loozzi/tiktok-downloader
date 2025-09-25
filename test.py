import asyncio

from pyppeteer import launch


async def get_content(url, user_agent, cookie) -> str:
    browser = await launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-infobars",
            "--window-position=0,0",
            "--ignore-certifcate-errors",
            "--ignore-certifcate-errors-spki-list",
            "--user-agent=" + user_agent,
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--no-first-run",
            "--no-zygote",
            # "--single-process",  # <- this one doesn't work in Windows
            "--disable-gpu",
        ],
    )
    page = await browser.newPage()
    await page.setUserAgent(user_agent)
    await page.setCookie(*cookie)
    await page.setViewport({"width": 1280, "height": 800})

    # Go to the page
    await page.goto(url, {"waitUntil": "networkidle2"})
    content = await page.content()
    await browser.close()
    return content


async def main():
    url = "https://www.tiktok.com/api/post/item_list/?WebIdLastTime=0&aid=1988&app_language=vi-VN&app_name=tiktok_web&browser_language=vi&browser_name=Mozilla&browser_online=true&browser_platform=Win32&browser_version=5.0+%28Windows+NT+10.0%3B+Win64%3B+x64%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F130.0.0.0+Safari%2F537.36&channel=tiktok_web&clientABVersions=74014084%2C74141281&cookie_enabled=true&count=16&coverFormat=2&cursor=0&data_collection_enabled=true&device_id=7561726488962321386&device_platform=web_pc&focus_state=true&from_page=user&history_len=4&is_fullscreen=false&is_page_visible=true&language=vi-VN&locate_item_id=&needPinnedItemIds=true&odinId=7800243493670184662&os=windows&post_item_list_request_type=0&priority_region=VN&referer=https%3A%2F%2Fwww.tiktok.com%2F&region=VN&root_referer=https%3A%2F%2Fwww.tiktok.com%2F&screen_height=1080&screen_width=1920&secUid=MS4wLjABAAAA9JY6ghQRp48pi2aBwoXEqn3j9EmOVW4EjATtqeI29qnsOpal0Rx63-XWjZyWuljC&tz_name=Asia%2FBangkok&user_is_login=true&webcast_language=vi-VN&msToken=somiRWt_4A3kkLp46CfGqKKoEModl57buG6pRPnAwH-5uSfwqRdAZzkiGQFszQ1_kFVHa37D-WRz25B-GF3yezh4zXzPDjTjSmX84MhTNVYLW5Df9MTzJpSNVH87Jhwg&X-Bogus=DFSzswVu9q58AN8756e683JSETTqnQjAdk&X-Gnarly=XG_8756e683_1758814269681_UNcopffUWrR9aoQ7SQZc"
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    cookie = []

    content = await get_content(url, user_agent, cookie)
    print(content)


if __name__ == "__main__":
    asyncio.run(main())
