import getpass
import hashlib
import platform
import subprocess
import uuid
from datetime import datetime, timedelta

from pymongo import MongoClient


class KeyManager:
    def __init__(
        self, mongo_uri="mongodb://localhost:27017/", db_name="tiktok_download"
    ):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.keys_collection = self.db.keys
        self.device_id = self.get_device_id()

    def get_device_id(self):
        """Tạo device ID duy nhất cho thiết bị"""

        # Tạo device ID từ thông tin hệ thống chi tiết hơn
        try:
            # Lấy MAC address của network interface đầu tiên
            mac = ":".join(
                [
                    "{:02x}".format((uuid.getnode() >> elements) & 0xFF)
                    for elements in range(0, 2 * 6, 2)
                ][::-1]
            )

            # Lấy thêm thông tin CPU nếu có thể
            try:
                cpu_info = (
                    subprocess.check_output(
                        "cat /proc/cpuinfo | grep 'processor'", shell=True
                    )
                    .decode()
                    .strip()
                )
            except:
                cpu_info = "unknown"

            # Kết hợp nhiều thông tin để tạo device ID duy nhất
            system_info = f"{platform.node()}-{platform.system()}-{getpass.getuser()}-{mac}-{cpu_info}-{platform.machine()}"
            device_id = hashlib.sha256(system_info.encode()).hexdigest()[:32]

        except Exception:
            # Fallback nếu không lấy được thông tin chi tiết
            system_info = f"{platform.node()}-{platform.system()}-{getpass.getuser()}-{uuid.getnode()}"
            device_id = hashlib.md5(system_info.encode()).hexdigest()

        return device_id

    def validate_key(self, key):
        """Kiểm tra key có hợp lệ không"""
        if len(key) < 10:
            return False, "Key không hợp lệ"

        key_doc = self.keys_collection.find_one({"key": key})
        if not key_doc:
            return False, "Key không tồn tại"

        # Kiểm tra key đã được kích hoạt chưa
        if key_doc.get("device_id"):
            if key_doc["device_id"] != self.device_id:
                return False, "Key đã được sử dụng trên thiết bị khác"

        # Kiểm tra key có hết hạn không (chỉ nếu đã kích hoạt và có expired_date)
        expired_date = key_doc.get("expired_date")
        if expired_date:
            if datetime.now() > expired_date:
                return False, "Key đã hết hạn"

        return True, "Key hợp lệ"

    def activate_key(self, key):
        """Kích hoạt key cho thiết bị hiện tại, set thời hạn kể từ lúc kích hoạt"""
        key_doc = self.keys_collection.find_one({"key": key})
        if not key_doc:
            return False

        valid_days = key_doc.get("valid_days")
        activated_date = datetime.now()
        expired_date = None
        if valid_days:
            expired_date = activated_date + timedelta(days=valid_days)

        result = self.keys_collection.update_one(
            {"key": key},
            {
                "$set": {
                    "device_id": self.device_id,
                    "activated_date": activated_date,
                    "expired_date": expired_date,
                }
            },
        )
        return result.modified_count > 0

    def check_device_activated(self):
        """Kiểm tra thiết bị đã được kích hoạt chưa"""
        key_doc = self.keys_collection.find_one({"device_id": self.device_id})
        return key_doc is not None

    def save_key_to_file(self, key):
        """Lưu key vào file local để không phải nhập lại"""
        try:
            with open(".key", "w") as f:
                f.write(key)
        except:
            pass

    def load_key_from_file(self):
        """Đọc key từ file local"""
        try:
            with open(".key", "r") as f:
                return f.read().strip()
        except:
            return None


def check_license():
    """Kiểm tra license trước khi chạy chương trình"""
    key_manager = KeyManager(
        "mongodb+srv://loozzi_myapp:pI5NCGIey19ga1nK@cluster0.hqs96.mongodb.net/?retryWrites=true&w=majority"
    )

    # Kiểm tra thiết bị đã được kích hoạt chưa
    if key_manager.check_device_activated():
        print("✅ Thiết bị đã được kích hoạt")
        return True

    # Thử đọc key từ file local
    saved_key = key_manager.load_key_from_file()
    if saved_key:
        is_valid, message = key_manager.validate_key(saved_key)
        if is_valid:
            if key_manager.activate_key(saved_key):
                print("✅ Key được kích hoạt thành công")
                return True

    # Yêu cầu nhập key
    print("🔐 Yêu cầu kích hoạt license")
    print("Vui lòng nhập key để sử dụng chương trình:")

    max_attempts = 3
    for attempt in range(max_attempts):
        key = input(f"Nhập key (lần thử {attempt + 1}/{max_attempts}): ").strip()

        if not key:
            print("❌ Vui lòng nhập key")
            continue

        is_valid, message = key_manager.validate_key(key)

        if is_valid:
            if key_manager.activate_key(key):
                key_manager.save_key_to_file(key)
                print("✅ Key được kích hoạt thành công!")
                return True
            else:
                print("❌ Lỗi khi kích hoạt key")
        else:
            print(f"❌ {message}")

    print("❌ Đã hết số lần thử. Chương trình sẽ thoát.")
    return False
