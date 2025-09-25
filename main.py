import json
import os
from abc import ABC, abstractmethod

import requests

from key_management import check_license


class BaseService(ABC):
    def __init__(self, save_path: str = "output", proxy: str = None):
        """
        Initialize the BaseService class.
        :param save_path: Path to save downloaded videos. Default is "output".
        :param proxy: Proxy server to use. Default is None.
        """
        self.platform = None
        self.proxy = proxy
        self.save_path = save_path
        if os.path.exists(save_path) and not os.path.isdir(save_path):
            raise ValueError(f"Path {save_path} is not a directory.")
        if save_path and not os.path.exists(save_path):
            os.makedirs(save_path)

    def extract_video_id_from_url(self, video_url: str):
        """
        Extract the video ID from a TikTok video URL.
        :param video_url: The TikTok video URL.
        :param proxy: Optional proxy settings.
        :return: The extracted video ID.
        """
        url = requests.head(url=video_url, allow_redirects=True).url
        if "douyin" in url:
            video_url = requests.head(url=video_url, allow_redirects=True).url
            return video_url.split("=")[-1]
        else:
            if "@" in url and "/video/" in url:
                return url.split("/video/")[1].split("?")[0]
            else:
                raise TypeError(
                    "URL format not supported. Below is an example of a supported url.\n"
                    "https://www.tiktok.com/@therock/video/6829267836783971589"
                )

    def fetch_file_url(self, video_url: str) -> tuple:
        """
        Fetch the file URL from a TikTok video URL.
        :param video_url: The TikTok video URL.
        :return: Tuple containing the file URL and description.
        """
        api = "https://ssstikpro.net/api/ajaxSearch"
        data = {"q": video_url, "cursor": 0, "page": 0, "lang": "en"}
        r = requests.post(api, data=data, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            raise Exception(r.text)

        res = r.json()
        if res["status"] != "ok" or "statusCode" in res:
            raise Exception(res["msg"])

        source = res["data"]
        desc = source.split("<h3>")[1].split("</h3>")[0]
        _id = source.split('value="')[1].split('"')[0]
        hrefs = source.split('href="')[1:4]
        hrefs = [href.split('"')[0] for href in hrefs]
        if len(hrefs) == 0:
            raise Exception(res["msg"])
        return hrefs[0], desc, _id

    @abstractmethod
    def crawl_all_video(self, username: str, limit: int = 100) -> list:
        """
        Crawl all videos from a user's profile.
        :param username: TikTok, Douyin, or Kuaishou username...
        :param limit: Maximum number of videos to crawl.
        :return: List of video URLs.
        """
        pass

    @abstractmethod
    def download_video(self, video_url: str) -> bool:
        """
        Download a video from a given URL.
        :param video_url: URL of the video to download.
        :return: True if download is successful, False otherwise.
        """
        pass


class TiktokService(BaseService):
    def __init__(self, save_path: str = "output", proxy: str = None):
        """
        Initialize the TiktokService class.
        :param save_path: Path to save downloaded videos. Default is "output".
        :param proxy: Proxy server to use. Default is None.
        """
        super().__init__(save_path=save_path, proxy=proxy)
        self.platform = "tiktok"

    def crawl_all_video(self, username, limit=100, skip=0) -> list:
        from get_all_videos import TikTokVideoScraper, get_sec_uid

        sec_uid = get_sec_uid(username)
        if not sec_uid:
            print(f"Không lấy được secUid cho user: {username}")
            return []
        scraper = TikTokVideoScraper()
        videos = scraper.get_all_videos(sec_uid, max_videos=limit + skip)
        if skip > 0:
            videos = videos[skip:]
        video_urls = []
        for v in videos:
            video_id = v.get("id") or v.get("aweme_id") or v.get("video", {}).get("id")
            unique_id = v.get("author", {}).get("uniqueId") or username
            video_urls.append(f"https://www.tiktok.com/@{unique_id}/video/{video_id}")
        return video_urls

    def download_all(self, username, limit=100, skip=0, num_threads=4):
        import os
        import queue
        import threading

        from tqdm import tqdm

        # Tạo queue để chứa video URLs
        video_queue = queue.Queue()

        # Tạo thư mục output và user
        output_dir = os.path.join("output", username)
        os.makedirs(output_dir, exist_ok=True)

        # Biến để theo dõi trạng thái
        loading_complete = threading.Event()
        download_stats = {"completed": 0, "total": 0}
        stats_lock = threading.Lock()

        def sanitize_filename(s):
            import re

            s = re.sub(r'[\\/:*?"<>|]', "", s)
            return s[:80]

        def format_filename(s):
            import re

            s = re.sub(r'[\\/:*?"<>|]', "", s)
            return s[:80]

        def video_loader():
            """Thread function để load video URLs vào queue"""
            try:
                from get_all_videos import TikTokVideoScraper, get_sec_uid

                sec_uid = get_sec_uid(username)
                if not sec_uid:
                    print(f"Không lấy được secUid cho user: {username}")
                    loading_complete.set()
                    return

                scraper = TikTokVideoScraper()
                cursor = 0
                page = 1
                loaded_count = 0
                skipped_count = 0

                print(f"🚀 Bắt đầu load video cho user: {username}")

                while loaded_count < limit:
                    print(f"\n📄 Đang load trang {page}...")
                    data = scraper.get_videos_page(sec_uid, cursor)

                    if not data:
                        print("Data:", data)
                        print("❌ Không thể lấy dữ liệu từ API")
                        break

                    videos = data.get("itemList", [])
                    if not videos:
                        print("✅ Không có video nào để load thêm")
                        break

                    # Xử lý từng video
                    for v in videos:
                        if skipped_count < skip:
                            skipped_count += 1
                            continue

                        if loaded_count >= limit:
                            break

                        video_id = (
                            v.get("id")
                            or v.get("aweme_id")
                            or v.get("video", {}).get("id")
                        )
                        unique_id = v.get("author", {}).get("uniqueId") or username
                        video_url = (
                            f"https://www.tiktok.com/@{unique_id}/video/{video_id}"
                        )

                        # Đẩy video URL vào queue
                        video_queue.put(video_url)
                        loaded_count += 1

                        with stats_lock:
                            download_stats["total"] += 1

                        print(f"✅ Đã load video {loaded_count}/{limit}: {video_id}")

                    if not data.get("hasMore", False):
                        print("✅ Đã load hết tất cả video")
                        break

                    cursor = data.get("cursor", cursor)
                    page += 1

                    # Thêm delay nhỏ để tránh rate limit
                    import time

                    time.sleep(1)

                print(f"\n✅ Hoàn thành load! Đã load {loaded_count} video vào queue")

            except Exception as e:
                print(f"❌ Lỗi khi load video: {e}")
            finally:
                loading_complete.set()

        def download_worker():
            """Thread function để download video từ queue"""
            while True:
                try:
                    # Lấy video URL từ queue với timeout
                    try:
                        video_url = video_queue.get(timeout=5)
                    except queue.Empty:
                        # Nếu queue rỗng và việc load đã hoàn thành thì thoát
                        if loading_complete.is_set():
                            break
                        continue

                    # Download video
                    success = download_one(video_url)

                    # Cập nhật stats
                    with stats_lock:
                        download_stats["completed"] += 1
                        completed = download_stats["completed"]
                        total = download_stats["total"]

                    status = "✅" if success else "❌"
                    print(
                        f"{status} [{completed}/{total}] Hoàn thành: {video_url.split('/')[-1]}"
                    )

                    # Đánh dấu task hoàn thành
                    video_queue.task_done()

                except Exception as e:
                    print(f"❌ Lỗi trong download worker: {e}")
                    video_queue.task_done()

        def download_one(video_url):
            try:
                info = self.get_video_info(video_url)
                desc = info.get("desc", "")
                hashtags = " ".join(
                    [
                        f"#{tag['title']}"
                        for tag in info.get("textExtra", [])
                        if tag.get("title")
                    ]
                )
                video_id = info.get("id", "video")
                filename_base = format_filename(
                    f"{desc[:min(50, len(desc))]} {hashtags[:min(20, len(hashtags))]} {video_id}"
                ).strip()
                if not filename_base:
                    filename_base = video_id
                # Ưu tiên tải ảnh nếu có imagePost và images
                image_post = info.get("imagePost", {})
                image_urls = []
                # Chỉ lấy ảnh từ images
                images = image_post.get("images", [])
                for img in images:
                    image_url_obj = img.get("imageURL", {})
                    url_list = image_url_obj.get("urlList", [])
                    if isinstance(url_list, list) and url_list:
                        image_urls.append(url_list[-1])
                if image_urls:
                    folder_path = os.path.join(output_dir, filename_base)
                    os.makedirs(folder_path, exist_ok=True)
                    for idx, img_url in enumerate(image_urls):
                        img_path = os.path.join(folder_path, f"img_{idx+1}.jpg")
                        headers = {
                            "User-Agent": (
                                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
                            ),
                            "Referer": "https://www.tiktok.com/",
                        }
                        print(f"Downloading image {img_path} ...")
                        with open(img_path, "wb") as f:
                            response = requests.get(
                                img_url, stream=True, headers=headers
                            )
                            if response.headers.get("Content-Type", "").startswith(
                                "image"
                            ):
                                for chunk in tqdm(
                                    response.iter_content(chunk_size=1024)
                                ):
                                    if chunk:
                                        f.write(chunk)
                                print(f"Image {img_path} downloaded successfully.")
                            else:
                                print(f"Link ảnh không hợp lệ: {img_url}")
                    print(f"Đã tải xong ảnh cho bài đăng {filename_base}")
                    return True
                # Nếu không phải bài đăng hình ảnh thì tải video
                if "video" in info:
                    video_data = info["video"]
                    file_url = None
                    if "bitrateInfo" in video_data:
                        file_url = video_data["bitrateInfo"][0]["PlayAddr"]["UrlList"][
                            -1
                        ]
                    if not file_url:
                        # fallback
                        try:
                            file_url, _, _ = self.fetch_file_url(video_url)
                        except Exception:
                            print(f"Không lấy được link tải cho {filename_base}")
                            return False
                    # Tạo thư mục nếu chưa có
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    username_dir = os.path.join(output_dir)
                    if not os.path.exists(username_dir):
                        os.makedirs(username_dir)
                    save_path = os.path.join(username_dir, f"{filename_base}.mp4")
                    # Nếu file đã tồn tại, thêm id vào tên file
                    if os.path.exists(save_path):
                        save_path = os.path.join(
                            username_dir, f"{filename_base}_{video_id}.mp4"
                        )
                    headers = {
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
                        ),
                        "Referer": "https://www.tiktok.com/",
                    }
                    print(f"Downloading video {os.path.basename(save_path)} ...")
                    with open(save_path, "wb") as file:
                        response = requests.get(file_url, stream=True, headers=headers)
                        # Chỉ lưu nếu là video/mp4
                        if response.headers.get("Content-Type", "").startswith("video"):
                            for chunk in tqdm(response.iter_content(chunk_size=1024)):
                                if chunk:
                                    file.write(chunk)
                            print(
                                f"Video {os.path.basename(save_path)} downloaded successfully."
                            )
                            return True
                        else:
                            print(f"Link tải không hợp lệ cho {filename_base}")
                            return False
                return False
            except Exception as e:
                print(f"Lỗi tải {video_url}: {e}")
                return False

        # Bắt đầu thread loader
        loader_thread = threading.Thread(target=video_loader, daemon=True)
        loader_thread.start()

        # Bắt đầu các worker threads để download
        download_threads = []
        for i in range(num_threads):
            worker = threading.Thread(target=download_worker, daemon=True)
            worker.start()
            download_threads.append(worker)

        print(f"🚀 Đã khởi động {num_threads} download threads")

        # Thread để hiển thị progress
        def progress_monitor():
            """Thread để hiển thị tiến trình"""
            while not loading_complete.is_set() or not video_queue.empty():
                with stats_lock:
                    completed = download_stats["completed"]
                    total = download_stats["total"]
                    queued = video_queue.qsize()

                if total > 0:
                    progress = (completed / total) * 100
                    print(
                        f"\r📊 Tiến trình: {completed}/{total} ({progress:.1f}%) | Queue: {queued}",
                        end="",
                        flush=True,
                    )

                import time

                time.sleep(2)

        # Bắt đầu progress monitor
        progress_thread = threading.Thread(target=progress_monitor, daemon=True)
        progress_thread.start()

        # Đợi loader hoàn thành và tất cả download hoàn thành
        try:
            loader_thread.join()
            print("\n✅ Loader thread đã hoàn thành")

            # Đợi tất cả video trong queue được xử lý
            video_queue.join()
            print("\n✅ Tất cả video đã được xử lý")

        except KeyboardInterrupt:
            print("\n❌ Nhận được tín hiệu dừng từ người dùng")

        with stats_lock:
            completed = download_stats["completed"]
            total = download_stats["total"]

        print(
            f"\n🎉 Hoàn thành! Đã tải {completed}/{total} video/ảnh cho user {username}"
        )
        print(f"📁 Thư mục lưu: {output_dir}")

    def download_video(self, video_url: str) -> bool:
        video_info = self.get_video_info(video_url)
        description = video_info.get("desc", "")
        videos = video_info.get("video", {})
        file_url = None
        if "bitrateInfo" in videos:
            file_url = videos["bitrateInfo"][0]["PlayAddr"]["UrlList"][-1]

        else:
            file_url, desc, id_video = self.fetch_file_url(video_url)

        if file_url is None:
            raise Exception(
                "Failed to fetch file URL. Please check the video URL or try again later."
            )

        filename = f"{description.strip()}.mp4"
        return self.save(filename=filename, file_url=file_url)

    def get_video_info(self, video_url: str):
        id = self.extract_video_id_from_url(video_url)

        r = requests.get(video_url, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            raise Exception(f"TikTok returned status code {r.status_code}")

        start = r.text.find('<script id="SIGI_STATE" type="application/json">')
        if start != -1:
            start += len('<script id="SIGI_STATE" type="application/json">')
            end = r.text.find("</script>", start)

            if end == -1:
                raise Exception(
                    "TikTok returned an invalid response.",
                )

            data = json.loads(r.text[start:end])
            video_info = data["ItemModule"][id]
        else:
            # Try __UNIVERSAL_DATA_FOR_REHYDRATION__ next

            # extract tag <script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">{..}</script>
            # extract json in the middle

            start = r.text.find(
                '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">'
            )
            if start == -1:
                raise Exception(
                    "TikTok returned an invalid response.",
                )

            start += len(
                '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">'
            )
            end = r.text.find("</script>", start)

            if end == -1:
                raise Exception(
                    "TikTok returned an invalid response.",
                )

            data = json.loads(r.text[start:end])
            default_scope = data.get("__DEFAULT_SCOPE__", {})
            video_detail = default_scope.get("webapp.video-detail", {})
            if video_detail.get("statusCode", 0) != 0:  # assume 0 if not present
                raise Exception(
                    "TikTok returned an invalid response structure.",
                )
            video_info = video_detail.get("itemInfo", {}).get("itemStruct")
            if video_info is None:
                raise Exception(
                    "TikTok returned an invalid response structure.",
                )

        return video_info


# This is for testing purposes only
# and should be removed in production code.
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Download all TikTok videos/images for a user."
    )
    parser.add_argument("username", nargs="?", help="TikTok username")
    parser.add_argument(
        "--limit", type=int, default=None, help="Number of videos/images to download"
    )
    parser.add_argument(
        "--skip", type=int, default=None, help="Number of newest videos/images to skip"
    )
    parser.add_argument(
        "--threads", type=int, default=None, help="Number of download threads"
    )
    args = parser.parse_args()

    # Nếu không truyền qua args thì hỏi nhập từng field
    username = args.username or input("Nhập TikTok username: ").strip()
    try:
        limit = (
            args.limit
            if args.limit is not None
            else int(input("Số lượng video/images muốn tải (Enter = 20): ") or 20)
        )
    except ValueError:
        limit = 20
    try:
        skip = (
            args.skip
            if args.skip is not None
            else int(
                input("Số lượng video/images mới nhất sẽ bỏ qua (Enter = 0): ") or 0
            )
        )
    except ValueError:
        skip = 0
    try:
        threads = (
            args.threads
            if args.threads is not None
            else int(input("Số luồng tải xuống (Enter = 4): ") or 4)
        )
    except ValueError:
        threads = 4

    tiktok_service = TiktokService(save_path="output")
    tiktok_service.download_all(
        username=username, limit=limit, skip=skip, num_threads=threads
    )
    print(f"✅ Đã tải xong {username} với {limit} video/images.")
    print("Nhấn Enter để thoát...")
    input()


if __name__ == "__main__":
    if check_license():
        main()
    else:
        print("❌ Không thể khởi động chương trình. Vui lòng liên hệ để được hỗ trợ.")
        input("Nhấn Enter để thoát...")
