import re

import requests

PROXY_API = (
    "https://7proxy.net/api/client/proxy/available?proxy_key="
    + open("./proxy-key.txt").read().strip()
)


def get_proxy_once():
    try:
        response = requests.get(PROXY_API, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(data)
            ip = data.get("ip")
            port = data.get("port")
            if ip and port:
                proxy_url = f"{ip}:{port}"
                print(f"✅ Proxy nhận được: {proxy_url}")
                return {"http": proxy_url, "https": proxy_url}
            else:
                print("⚠️ Proxy không hợp lệ hoặc thiếu thông tin.")
                return None

        elif response.status_code == 400:
            msg = response.json().get("message", "")

            if "không tồn tại" in msg.lower():
                print(f"❌ Key proxy không tồn tại: {msg}")
            elif "chờ thêm" in msg.lower():
                wait_seconds = extract_wait_time(msg)
                print(f"⛔ Bị giới hạn! Phải đợi {wait_seconds}s để lấy proxy mới.")
            else:
                print(f"⚠️ Lỗi 400 khác: {msg}")
            return None

        else:
            print(f"❌ Lỗi HTTP không xác định: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Lỗi kết nối hoặc không thể truy cập: {e}")
        return None


def extract_wait_time(message):
    """Tìm số giây cần chờ từ chuỗi thông báo"""
    match = re.search(r"chờ thêm (\d+)s", message)
    return int(match.group(1)) if match else 10


if __name__ == "__main__":
    print(get_proxy_once())
