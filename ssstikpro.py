import asyncio
import logging
import os
import re
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ssstikpro")

API = "https://ssstikpro.net/api/ajaxSearch"


async def get_page(
    session: aiohttp.ClientSession,
    url: str,
    cursor: str = "0",
    page: int = 0,
    proxy: Optional[str] = None,
) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://ssstikpro.net",
        "Referer": "https://ssstikpro.net/",
    }
    data = {"q": url, "cursor": cursor, "page": str(page), "lang": "en"}
    logger.info(f"Requesting page {page} with cursor {cursor}")

    try:
        async with session.post(
            API, headers=headers, data=data, proxy=proxy
        ) as response:
            logger.info(f"Response status code: {response.status}")
            if response.status == 200:
                return await response.json()
    except Exception as e:
        logger.error(f"Error in get_page: {e}")
    return None


def parse_videos(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    videos = soup.select(".video-item")

    results = []
    for video in videos:
        title_element = video.select_one(".text-title")
        link_element = video.select_one("a")
        if title_element and link_element:
            title = title_element.text.strip()
            link = link_element["href"]
            results.append({"title": title, "link": link})

    return results


async def video_generator(
    session: aiohttp.ClientSession,
    channel: str,
    max_videos: int = 100,
    proxy: Optional[str] = None,
):
    """Async generator that yields videos one by one as they are fetched."""
    videos_yielded = 0
    cursor = "0"
    page = 0

    while videos_yielded < max_videos:
        response = await get_page(session, channel, cursor, page, proxy)
        if response and response.get("status") == "ok":
            logger.info(f"Successfully retrieved page {page}")
            html = response.get("data", "")
            videos = parse_videos(html)

            if not videos:
                logger.info("No more videos found on this page.")
                break

            for video in videos:
                if videos_yielded < max_videos:
                    yield video
                    videos_yielded += 1
                else:
                    break

            cursor = response.get("next_cursor", "0")
            if cursor == "0":
                break
            page += 1
            logger.info(f"Total videos yielded: {videos_yielded}")
        else:
            logger.warning(f"Failed to retrieve page {page} or no more data.")
            break


async def download_video(
    session: aiohttp.ClientSession, video_url: str, file_name: str, output_dir: str
) -> bool:
    try:
        async with session.get(video_url) as response:
            if response.status == 200:
                os.makedirs(output_dir, exist_ok=True)
                file_path = os.path.join(output_dir, file_name)

                with open(file_path, "wb") as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)

                logger.info(f"Video downloaded successfully: {file_name}")
                return True
            else:
                logger.error(
                    f"Failed to download video. Status code: {response.status}"
                )
                return False
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        return False


async def download_task(
    session: aiohttp.ClientSession,
    video_info: dict,
    output_dir: str,
    semaphore: asyncio.Semaphore,
):
    """Task for downloading a single video with semaphore for concurrency control."""
    async with semaphore:
        # Sanitize filename
        title = re.sub(r'[<>:"/\\|?*]', "_", video_info["title"])
        file_name = title[: min(len(title), 100)] + ".mp4"

        await download_video(session, video_info["link"], file_name, output_dir)


async def download_manager(
    session: aiohttp.ClientSession,
    video_queue: asyncio.Queue,
    output_dir: str,
    semaphore: asyncio.Semaphore,
):
    """Manager that processes videos from queue and downloads them."""
    tasks = []

    while True:
        try:
            # Wait for video with timeout to check if we should stop
            video = await asyncio.wait_for(video_queue.get(), timeout=5.0)

            if video is None:  # Sentinel value to stop
                break

            logger.info(f"Starting download for: {video['title']}")
            task = asyncio.create_task(
                download_task(session, video, output_dir, semaphore)
            )
            tasks.append(task)

            # Clean up completed tasks
            tasks = [t for t in tasks if not t.done()]

        except asyncio.TimeoutError:
            # Check if there are any pending tasks, if not, we might be done
            if not tasks:
                continue

        except Exception as e:
            logger.error(f"Error in download manager: {e}")

    # Wait for remaining tasks to complete
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


async def main():
    username = input("Enter TikTok username: ")
    output_dir = input("Enter output directory (default: output): ") or "output"
    video_limit_str = input(
        "Enter maximum number of videos to download (or press Enter for all): "
    )
    video_limit = int(video_limit_str) if video_limit_str.isdigit() else float("inf")

    concurrent_downloads_str = input(
        "Enter number of concurrent downloads (default 10): "
    )
    concurrent_downloads = (
        int(concurrent_downloads_str) if concurrent_downloads_str.isdigit() else 10
    )

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, username), exist_ok=True)
    output_dir = os.path.join(output_dir, username)

    channel_url = f"https://www.tiktok.com/@{username}"

    print(f"Starting download for user '{username}' into '{output_dir}' folder.")
    print(
        f"Using {concurrent_downloads} concurrent downloads. Max videos: {'All' if video_limit == float('inf') else video_limit}"
    )

    # Create semaphore to limit concurrent downloads
    semaphore = asyncio.Semaphore(concurrent_downloads)

    # Create queue for videos
    video_queue = asyncio.Queue(maxsize=50)  # Buffer size

    # Configure aiohttp session with connection limits
    connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
    timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes timeout

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        logger.info("Starting video fetching and downloading...")

        # Start download manager
        download_manager_task = asyncio.create_task(
            download_manager(session, video_queue, output_dir, semaphore)
        )

        # Start video producer
        video_count = 0
        async for video in video_generator(
            session, channel_url, max_videos=video_limit
        ):
            await video_queue.put(video)
            video_count += 1
            logger.info(f"Queued video {video_count}: {video['title']}")

        # Send sentinel to stop download manager
        await video_queue.put(None)

        # Wait for download manager to finish
        await download_manager_task

    print(f"All downloads completed! Total videos processed: {video_count}")


if __name__ == "__main__":
    asyncio.run(main())
