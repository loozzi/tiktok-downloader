import json
import random
import time
from urllib.parse import urlencode

import requests


def get_sec_uid(username):
    """
    Lấy secuid của người dùng TikTok thông qua username
    """
    try:
        username = username.replace("@", "")
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/17.6 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) "
            "Gecko/20100101 Firefox/132.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) "
            "Gecko/20100101 Firefox/132.0",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) "
            "Gecko/20100101 Firefox/132.0",
        ]
        user_agent = random.choice(user_agents)
        # Cookie for authentication
        cookie = (
            "tt_csrf_token=KUZnBOnM-0PUt387SHDt99Iwv8k74aO4x51g; "
            "tiktok_webapp_theme_source=light; tiktok_webapp_theme=light; "
            "passport_csrf_token=d6caabd10dbe83ca04ea0d134dbf3b3e; "
            "passport_csrf_token_default=d6caabd10dbe83ca04ea0d134dbf3b3e; "
            "ttwid=1%7C9bJbwDKpMGg_ode4uyQ4FgzV7dcCgVJ2QXIJ28EnKGY%7C1746775821%7C"
            "fde69a521a980f73aba2909923305460d580d99bca73052cebb56130164eaf0b; "
            "msToken=Vp62AVjNYXNefqIFq23Ut_9ydQTurlVxwl9qXLVMXzsGSfLPPnF48qr9_huCqYkY"
            "DYz4xL2g5qEhE_4ULYq1O0ap2NRTyc1j1WocOIF0r29CgLEjDuEMBL0bsyPP; "
            "s_v_web_id=verify_magh965c_14nkm7El_TufS_454a_BuUz_CNb0QCkUAiP5; "
            "odin_tt=962e2e0222842ca3653a47a7697085e8d771f98035b2e8ec40cbd52f2d035ca0"
            "cfed0bd2ade336ca222235801bf404aade4d7c3ecc915c10478ae623f0964f7c; "
            "multi_sids=7502344901842584597%3A9cd890c47df3165459cd1bb01009b8c5; "
            "cmpl_token=AgQQAPNkF-RO0rgjQFfg-J0s8nw38etV_4TvYN-ilw; "
            "sid_guard=9cd890c47df3165459cd1bb01009b8c5%7C1746775887%7C15552000%7C"
            "Wed%2C+05-Nov-2025+07%3A31%3A27+GMT; "
            "uid_tt=d4200d38b3ecbb23efbb00c8cf2854e802c169b2f4d12a1b79a95a231608f7f2; "
            "uid_tt_ss=d4200d38b3ecbb23efbb00c8cf2854e802c169b2f4d12a1b79a95a231608f7f2; "
            "sid_tt=9cd890c47df3165459cd1bb01009b8c5; "
            "sessionid=9cd890c47df3165459cd1bb01009b8c5; "
            "sessionid_ss=9cd890c47df3165459cd1bb01009b8c5; "
            "sid_ucp_v1=1.0.0-KDc5NmMyYmIxZTA3ZmVjNDY3ZDJkMGU5NzFkZWQwMmNjNWU4ZjIxNWY"
            "KGgiViKnGht7rjmgQz972wAYYsws4AUDrB0gEEAMaA215MiIgOWNkODkwYzQ3ZGYzMTY1NDU5Y2QxYmIw"
            "MTAwOWI4YzU; "
            "ssid_ucp_v1=1.0.0-KDc5NmMyYmIxZTA3ZmVjNDY3ZDJkMGU5NzFkZWQwMmNjNWU4ZjIxNWY"
            "KGgiViKnGht7rjmgQz972wAYYsws4AUDrB0gEEAMaA215MiIgOWNkODkwYzQ3ZGYzMTY1NDU5Y2QxYmIw"
            "MTAwOWI4YzU; "
            "tt_ticket_guard_has_set_public_key=1; store-idc=maliva; "
            "store-country-sign=MEIEDAIcKwuX6ZMZg8yINwQgUhYwG_hlRNacrdZ0Dq2iQk8osAH5cGPohx1g"
            "HmuBvpkEEPYOhye8yPZnMRmb6PMrhn0; "
            "store-country-code=br; store-country-code-src=uid; tt-target-idc=useast1a; "
            "tt-target-idc-sign=FcqzNXqDLYOMauQExA1vcGIU2XYPp87Ke5Q09qf-bfRUy1slMj_wgxEGVB2L"
            "TkYhmPE8KMeMRdyHKMPvHG1tSTGDrbyFjk_BZrWj2PY7HboSnt5zCgO8TqHNMGFTjiUAlCIcT4f5HHmD"
            "xXeVjgr3Xz_ihq0leN_Q4_SPLp2oDs7iBcdwKXfb2_cgEw_VAcLHJpGAKi5G-pxHYubAXdnuSFqre-LJ"
            "2WpBLaHqRQE6ceUZ_o0LkqXr5-ZUbzwtNDa-Mhss-E5xm5VtSlLdLQbrPXbAap1k997HAaJJ9e_KWK7K"
            "HEYpuibJdNNYbpPoKkQ1MujvCKu47O8TuwjkGNQPzo5oBUJ79eGzqxn80TVE4T_NHFozJ9ANgiR5yUrt"
            "uGdGNMcWTcKK09QWcyweN2bKnExvmNsJgK8jO0s3tiD0Ah3rYSV6zNXpC5AVeUJOMg--deV4X3ETe8cJ"
            "eHrPr8XQpfyYbVhiLzdhRAJRHGvQOJt6p4fQ6XJFN6z05vvJxe76; "
            "msToken=n1FyJyTEL-CoaS_DCo0ILCmJPibSqyzc5z60pABPDj0--fePgd3rMrhXiUmyMAn8"
            "blbx1QXR2-ELNdd2MkQWRXJqmFnP1QfKxOvvHa8eTdTP6IwwI5ZT83sBIC9jMOZx_3dfH1pcE8ZVPA==; "
            "last_login_method=email"
        )

        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
            "Cookie": cookie,
        }
        url = f"https://www.tiktok.com/@{username}"
        print(f"Đang lấy thông tin người dùng: {username}")
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            html_content = response.text
            secuid_patterns = ['"secUid":"', '"sec_uid":"', "secUid:", "sec_uid:"]
            secuid = None
            for pattern in secuid_patterns:
                start_idx = html_content.find(pattern)
                if start_idx != -1:
                    start_idx += len(pattern)
                    end_idx = html_content.find('"', start_idx)
                    if end_idx != -1:
                        secuid = html_content[start_idx:end_idx]
                        break
            if secuid:
                print(f"Thành công! SecUID: {secuid}")
                return secuid
            else:
                print("Không tìm thấy secuid trong response")
                return None
        else:
            print(f"Request thất bại với status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Lỗi khi lấy secuid: {str(e)}")
        return None


class TikTokVideoScraper:
    """
    TikTok Video Scraper - Lấy danh sách video của một user TikTok
    """

    def __init__(self):
        self.base_url = "https://www.tiktok.com/api/post/item_list/"
        # Random user agent từ danh sách
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
            "(KHTML, like Gecko) Version/17.6 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) "
            "Gecko/20100101 Firefox/132.0",
        ]
        selected_ua = random.choice(user_agents)

        # Cookie for authentication
        self.cookie = "tt_chain_token=NXY2vq+Bf7QgLKxRuxwQmQ==; d_ticket=9ed8ba9e7f560649c64a631822f0e99dce082; ttwid=1%7CJPqtq2oITwOsE_W7yxTSRAi-BPH-K_RjtfAs0zDi5Jc%7C1743418462%7Ccd9eae413518d7700da4ced17519cc2b7827b5ed10fdfd41b8abda4466125c7a; uid_tt=659d5c3f523ed5a506a175c0c3b8a21bb315984a75f1e095c2c7d5f5361605b2; uid_tt_ss=659d5c3f523ed5a506a175c0c3b8a21bb315984a75f1e095c2c7d5f5361605b2; sid_tt=0b2f2a023d2ae0e1a8cd8abdb8dd7ea5; sessionid=0b2f2a023d2ae0e1a8cd8abdb8dd7ea5; sessionid_ss=0b2f2a023d2ae0e1a8cd8abdb8dd7ea5; store-idc=alisg; store-country-code=vn; store-country-code-src=uid; tt-target-idc=alisg; tt-target-idc-sign=lcEjHl9TOWQL659Rg1vYNb82LkuSGPHnIa9kTVPUkWnE5sFqrfVlHhVy0ZEbzWc5DnqQ8Ai5NEez_PtDCnuqfd88lhKtoLIQRxqPhxUnMl2z50vhtszKSQVQ7QT_Pt4LHOeSlbGI17D3y_EPI6enVhZKqY0dlAYE5-1584soCEI_V2XCBFLk2PmOkWINJWqtIaQcvzm1IJ8D_ztnlBCoyvrvIgsvMYX0xrshdlc3ahnkgiccCvgyX2hDDBktwXzGG2aDxzeBRIVz-JIYTVJb9Bub5XwDwpjRghxKBKM8hoo1grHCf7Mc1g6ZisGfM25nEyZC1PY-l6ew2WIeMKAGKS4i1ytnztQtZplSx3Adx9MhJo_KVLE1QsHV7GPmOnLUX9D6-jgeK51w3lRKNHbQzxAjVGy2ysz6usZOLcZukc52C4oGdmW_x2gSuGkECaUzeVaZ1h_eFHtF0zTqGOBaisPA2w1p8ZGhyi7J1zdSY-tYCYgfBEXXe4nDw50HyMZE; tt_csrf_token=5QbQhlbI-qRCHHV_kYiPuRmfnsPJpHV6Z1go; csrfToken=Ki1lgx8k-zRQJYcL_7_y2wJ1HTUry2JL3EwQ; sid_guard=0b2f2a023d2ae0e1a8cd8abdb8dd7ea5%7C1758207659%7C15552000%7CTue%2C+17-Mar-2026+15%3A00%3A59+GMT; sid_ucp_v1=1.0.0-KDVlODk3YmRkYzVmNzU1YzUzYTJjN2MwNDE1YzNiZTEwZmVhYzFiYTAKGQiBiL7GxMKLoGIQq72wxgYYsws4CEAKSAQQAxoDc2cxIiAwYjJmMmEwMjNkMmFlMGUxYThjZDhhYmRiOGRkN2VhNQ; ssid_ucp_v1=1.0.0-KDVlODk3YmRkYzVmNzU1YzUzYTJjN2MwNDE1YzNiZTEwZmVhYzFiYTAKGQiBiL7GxMKLoGIQq72wxgYYsws4CEAKSAQQAxoDc2cxIiAwYjJmMmEwMjNkMmFlMGUxYThjZDhhYmRiOGRkN2VhNQ; s_v_web_id=verify_mfpjgz6x_mHxi86pU_1ODa_41DW_AkiP_l4omxjpEXkmL; passport_csrf_token=366a5673d7556593bc0ff55907c36cf9; passport_csrf_token_default=366a5673d7556593bc0ff55907c36cf9; odin_tt=84850f4f1cb6e148e01a3ef8d7f7694943da0106417f102c02508ae9e8f52093378c60815c1c44136e8ac4462fc1aa42d979e6f7c6d3cef94ca926969ad3d034d4f2d116caa959e45d7dda18d7ac1145; store-country-sign=MEIEDN4SsiY_vduIi4pIcwQgx2EbiWDj4_NyF0fn1EHJXqBf10mIvHRF9x4QiLqJX3oEEOZQ5PHyrWxp-Bx-vQG0pMs; msToken=O1mXMa20bM4Xrm0KZCOkHiqkbHi_uIJCuEFZYJmoP_Wvv_VJNOcOiBfOOGOa2pW6o3g33nhSjTuOHESLt7179ZKNjucMJm3WMySkPSog70giL4K6n_jrecX7CCbARVAmebIP8_hVXfWLFoAbzEAF6BDh9g=="

        self.headers = {
            "User-Agent": selected_ua,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.tiktok.com/",
            "Origin": "https://www.tiktok.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Cookie": self.cookie,
        }

    def get_videos_page(self, sec_uid, cursor=0, count=16):
        # Sinh các giá trị động
        import string

        device_id = str(random.randint(7000000000000000000, 7999999999999999999))
        odinId = str(random.randint(7000000000000000000, 7999999999999999999))
        msToken = "".join(
            random.choices(string.ascii_letters + string.digits + "-_", k=128)
        )

        # X-Bogus và X-Gnarly giả lập
        def gen_x_bogus(query_string, user_agent):
            timestamp = int(time.time() * 1000)
            hash_input = f"{query_string}{timestamp}{user_agent}"
            hash_md5 = __import__("hashlib").md5(hash_input.encode()).hexdigest()
            random_chars = "".join(
                random.choices(string.ascii_letters + string.digits, k=16)
            )
            return f"DFSzswVu{random_chars[:4]}AN{hash_md5[:8]}{random_chars[4:]}"

        def gen_x_gnarly(query_string, user_agent):
            timestamp = int(time.time() * 1000)
            hash_input = f"{query_string}{timestamp}{user_agent}"
            hash_value = __import__("hashlib").md5(hash_input.encode()).hexdigest()
            random_chars = "".join(
                random.choices(string.ascii_letters + string.digits, k=20)
            )
            return f"XG_{hash_value[:8]}_{timestamp}_{random_chars}"

        # Tạo browser_version phù hợp với user agent
        current_ua = self.headers["User-Agent"]
        if "Chrome/131" in current_ua:
            browser_version = (
                "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            )
        elif "Chrome/130" in current_ua:
            browser_version = (
                "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            )
        elif "Firefox" in current_ua:
            browser_version = (
                "5.0 (Windows NT 10.0; Win64; x64; rv:132.0) "
                "Gecko/20100101 Firefox/132.0"
            )
        else:
            browser_version = (
                "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            )

        params = {
            "WebIdLastTime": "0",
            "aid": "1988",
            "app_language": "vi-VN",
            "app_name": "tiktok_web",
            "browser_language": "vi",
            "browser_name": "Mozilla",
            "browser_online": "true",
            "browser_platform": "Win32",
            "browser_version": browser_version,
            "channel": "tiktok_web",
            "clientABVersions": "74014084,74141281",
            "cookie_enabled": "true",
            "count": str(count),
            "coverFormat": "2",
            "cursor": str(cursor),
            "data_collection_enabled": "true",
            "device_id": device_id,
            "device_platform": "web_pc",
            "focus_state": "true",
            "from_page": "user",
            "history_len": "4",
            "is_fullscreen": "false",
            "is_page_visible": "true",
            "language": "vi-VN",
            "locate_item_id": "",
            "needPinnedItemIds": "true",
            "odinId": odinId,
            "os": "windows",
            "post_item_list_request_type": "0",
            "priority_region": "VN",
            "referer": "https://www.tiktok.com/",
            "region": "VN",
            "root_referer": "https://www.tiktok.com/",
            "screen_height": "1080",
            "screen_width": "1920",
            "secUid": sec_uid,
            "tz_name": "Asia/Bangkok",
            "user_is_login": "true",
            "webcast_language": "vi-VN",
            "msToken": msToken,
        }
        query_string = urlencode(params, doseq=True)
        user_agent = self.headers["User-Agent"]
        params["X-Bogus"] = gen_x_bogus(query_string, user_agent)
        params["X-Gnarly"] = gen_x_gnarly(query_string, user_agent)
        headers = self.headers.copy()
        headers["Referer"] = f"https://www.tiktok.com/@user?secUid={sec_uid}"

        # Random delay để tránh rate limit
        time.sleep(random.uniform(0.5, 1.5))

        try:
            response = requests.get(
                self.base_url, params=params, headers=headers, timeout=15
            )
            print(f"🌐 Response Status: {response.status_code}")

            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    print("❌ Không thể parse JSON response")
                    print(f"Response text: {response.text[:200]}...")
                    return None
            elif response.status_code == 403:
                print("❌ API Error 403: Bị chặn truy cập (có thể cần đổi IP/proxy)")
                return None
            elif response.status_code == 429:
                print("❌ API Error 429: Quá nhiều request (cần chờ lâu hơn)")
                return None
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                return None
        except requests.exceptions.Timeout:
            print("❌ Request timeout")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ Connection error")
            return None
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None

    def get_all_videos(self, sec_uid, max_videos=None, delay=2):
        all_videos = []
        cursor = 0
        page = 1
        print(f"🚀 Bắt đầu lấy video cho secUid: {sec_uid}")
        while True:
            print(f"\n📄 Trang {page} - Cursor: {cursor}")
            data = self.get_videos_page(sec_uid, cursor)
            print(data)
            if not data:
                print("❌ Không thể lấy dữ liệu từ API")
                break
            videos = data.get("itemList", [])
            if not videos:
                print("✅ Không có video nào để lấy thêm")
                break
            all_videos.extend(videos)
            print(f"✅ Trang {page}: +{len(videos)} videos, Tổng: {len(all_videos)}")
            if not data.get("hasMore", False):
                print("✅ Đã lấy hết tất cả video")
                break
            cursor = data.get("cursor", cursor)
            if max_videos and len(all_videos) >= max_videos:
                print(f"✅ Đã đạt giới hạn {max_videos} video")
                break
            page += 1
            # Random delay để tránh bị phát hiện
            delay_time = random.uniform(delay, delay + 1)
            print(f"⏳ Đang chờ {delay_time:.1f} giây...")
            time.sleep(delay_time)
        return all_videos

    def save_to_json(self, videos, filename=None):
        import datetime

        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tiktok_videos_{timestamp}.json"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(videos, f, indent=2, ensure_ascii=False)
            print(f"💾 Đã lưu {len(videos)} video vào: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Lỗi khi lưu JSON: {e}")
            return None


if __name__ == "__main__":
    print("🎯 TikTok Video Scraper")
    print("=" * 60)
    username = input("Nhập username TikTok (không cần @): ").strip()
    sec_uid = get_sec_uid(username)
    if not sec_uid:
        print("❌ Không lấy được secUid, kiểm tra lại username!")
    else:
        try:
            max_videos = input(
                "Số lượng video tối đa (Enter = không giới hạn): "
            ).strip()
            max_videos = int(max_videos) if max_videos else None
        except ValueError:
            max_videos = None
        scraper = TikTokVideoScraper()
        print("\n🚀 Bắt đầu lấy video...")
        videos = scraper.get_all_videos(sec_uid, max_videos)
        if not videos:
            print("❌ Không lấy được video nào")
        else:
            print(f"\n✅ Hoàn thành! Đã lấy {len(videos)} video")
            scraper.save_to_json(videos)
