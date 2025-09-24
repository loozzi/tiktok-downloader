import random
import string
from datetime import datetime, timedelta

from key_management import KeyManager


def admin_key_management():
    """Chương trình quản lý key cho admin"""
    print("🔧 TikTok Downloader - Key Management System")
    print("=" * 50)

    # Kết nối MongoDB
    key_manager = KeyManager(
        "mongodb+srv://loozzi_myapp:pI5NCGIey19ga1nK@cluster0.hqs96.mongodb.net/?retryWrites=true&w=majority"
    )

    while True:
        print("\n📋 MENU QUẢN LÝ KEY:")
        print("1. Tạo key mới")
        print("2. Xem danh sách key")
        print("3. Xóa key")
        print("4. Cập nhật thời hạn key")
        print("5. Thống kê key")
        print("6. Tạo nhiều key")
        print("7. Xóa toàn bộ key")
        print("0. Thoát")

        choice = input("\nChọn chức năng (0-6): ").strip()

        if choice == "1":
            create_new_key(key_manager)
        elif choice == "2":
            list_all_keys(key_manager)
        elif choice == "3":
            delete_key(key_manager)
        elif choice == "4":
            update_key_expiry(key_manager)
        elif choice == "5":
            show_key_statistics(key_manager)
        elif choice == "6":
            create_multiple_keys(key_manager)
        elif choice == "7":
            delete_all_keys(key_manager)
        elif choice == "0":
            print("👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ!")


# Xóa toàn bộ key
def delete_all_keys(key_manager):
    print("\n⚠️ XÓA TOÀN BỘ KEY")
    print("-" * 30)
    confirm = input(
        "Bạn có chắc chắn muốn xóa toàn bộ key? (gõ YES để xác nhận): "
    ).strip()
    if confirm == "YES":
        result = key_manager.keys_collection.delete_many({})
        print(f"✅ Đã xóa {result.deleted_count} key khỏi hệ thống!")
    else:
        print("⏹️ Hủy thao tác xóa toàn bộ key.")


# Tạo nhiều key số lượng lớn
def create_multiple_keys(key_manager):
    print("\n🆕 TẠO NHIỀU KEY SỐ LƯỢNG LỚN")
    print("-" * 30)

    try:
        count = input("Nhập số lượng key muốn tạo: ").strip()
        if not count.isdigit() or int(count) <= 0:
            print("❌ Số lượng không hợp lệ!")
            return
        count = int(count)

        description = input("Mô tả key (tùy chọn, áp dụng cho tất cả): ").strip()

        print("\nChọn thời hạn key:")
        print("1. 7 ngày")
        print("2. 30 ngày")
        print("3. 90 ngày")
        print("4. 1 năm")
        print("5. Không giới hạn")
        expiry_choice = input("Chọn (1-5): ").strip()

        valid_days = None
        if expiry_choice == "1":
            valid_days = 7
        elif expiry_choice == "2":
            valid_days = 30
        elif expiry_choice == "3":
            valid_days = 90
        elif expiry_choice == "4":
            valid_days = 365
        # expiry_choice == "5" thì valid_days = None

        key_length = 20
        characters = string.ascii_letters + string.digits
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"keys_{now_str}.txt"

        key_docs = []
        key_lines = []
        for _ in range(count):
            new_key = "".join(random.choice(characters) for _ in range(key_length))
            key_doc = {
                "key": new_key,
                "description": description,
                "created_date": datetime.now(),
                "valid_days": valid_days,
                "expired_date": None,  # Sẽ set khi kích hoạt
                "device_id": None,
                "activated_date": None,
            }
            key_docs.append(key_doc)
            key_lines.append(f"Key: {new_key}")

        # Lưu vào database
        key_manager.keys_collection.insert_many(key_docs)

        # Lưu vào file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Mô tả: {description}\n")
            f.write(f"Ngày tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            if valid_days:
                f.write(f"Thời hạn: {valid_days} ngày kể từ khi kích hoạt\n")
            else:
                f.write("Hết hạn: Không giới hạn\n")
            f.write(f"Số lượng: {count}\n")
            f.write("-" * 40 + "\n")
            for line in key_lines:
                f.write(line + "\n")

        print(f"\n✅ Đã tạo {count} key thành công!")
        print(f"💾 Danh sách key đã được lưu vào file {filename}")

    except Exception as e:
        print(f"❌ Lỗi khi tạo nhiều key: {str(e)}")


def create_new_key(key_manager):
    """Tạo key mới"""
    print("\n🆕 TẠO KEY MỚI")
    print("-" * 30)

    # Tạo key ngẫu nhiên
    key_length = 20
    characters = string.ascii_letters + string.digits
    new_key = "".join(random.choice(characters) for _ in range(key_length))

    # Nhập thông tin key
    description = input("Mô tả key (tùy chọn): ").strip()

    # Nhập thời hạn
    print("\nChọn thời hạn key:")
    print("1. 7 ngày")
    print("2. 30 ngày")
    print("3. 90 ngày")
    print("4. 1 năm")
    print("5. Không giới hạn")

    expiry_choice = input("Chọn (1-5): ").strip()

    valid_days = None
    if expiry_choice == "1":
        valid_days = 7
    elif expiry_choice == "2":
        valid_days = 30
    elif expiry_choice == "3":
        valid_days = 90
    elif expiry_choice == "4":
        valid_days = 365
    # expiry_choice == "5" thì valid_days = None (không giới hạn)

    # Lưu key vào database
    key_doc = {
        "key": new_key,
        "description": description,
        "created_date": datetime.now(),
        "valid_days": valid_days,
        "expired_date": None,  # Sẽ set khi kích hoạt
        "device_id": None,
        "activated_date": None,
    }

    try:
        key_manager.keys_collection.insert_one(key_doc)
        print(f"\n✅ Tạo key thành công!")
        print(f"🔑 Key: {new_key}")
        if valid_days:
            print(f"⏰ Thời hạn: {valid_days} ngày kể từ khi kích hoạt")
        else:
            print("⏰ Hết hạn: Không giới hạn")

        # Lưu key vào file với encoding utf-8 để hỗ trợ tiếng Việt
        with open(
            f"key_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w", encoding="utf-8"
        ) as f:
            f.write(f"Key: {new_key}\n")
            f.write(f"Mô tả: {description}\n")
            f.write(f"Ngày tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            if valid_days:
                f.write(f"Thời hạn: {valid_days} ngày kể từ khi kích hoạt\n")
            else:
                f.write("Hết hạn: Không giới hạn\n")

        print(f"💾 Key đã được lưu vào file")

    except Exception as e:
        print(f"❌ Lỗi khi tạo key: {str(e)}")


def list_all_keys(key_manager):
    """Hiển thị danh sách tất cả key"""
    print("\n📝 DANH SÁCH KEY")
    print("-" * 100)

    try:
        keys = list(key_manager.keys_collection.find().sort("created_date", -1))

        if not keys:
            print("Không có key nào trong hệ thống")
            return

        print(
            f"{'STT':<3} {'Key':<22} {'Trạng thái':<12} {'Hết hạn':<20} {'Valid days':<12} {'Mô tả':<20}"
        )
        print("-" * 100)

        for i, key_doc in enumerate(keys, 1):
            key = key_doc.get("key", "")
            status = "Đã kích hoạt" if key_doc.get("device_id") else "Chưa kích hoạt"

            expired_date = key_doc.get("expired_date")
            if expired_date:
                if datetime.now() > expired_date:
                    status = "Hết hạn"
                expiry_str = expired_date.strftime("%d/%m/%Y")
            else:
                expiry_str = "Không giới hạn"

            valid_days = key_doc.get("valid_days")
            valid_days_str = str(valid_days) if valid_days else "Không giới hạn"

            description = key_doc.get("description", "")[:18]

            print(
                f"{i:<3} {key:<22} {status:<12} {expiry_str:<20} {valid_days_str:<12} {description:<20}"
            )

    except Exception as e:
        print(f"❌ Lỗi khi lấy danh sách key: {str(e)}")


def delete_key(key_manager):
    """Xóa key"""
    print("\n🗑️ XÓA KEY")
    print("-" * 30)

    key_to_delete = input("Nhập key cần xóa: ").strip()

    if not key_to_delete:
        print("❌ Vui lòng nhập key")
        return

    try:
        # Tìm key
        key_doc = key_manager.keys_collection.find_one({"key": key_to_delete})

        if not key_doc:
            print("❌ Key không tồn tại")
            return

        # Hiển thị thông tin key
        print(f"\nThông tin key sẽ xóa:")
        print(f"Key: {key_doc.get('key')}")
        print(f"Mô tả: {key_doc.get('description', 'Không có')}")
        print(
            f"Trạng thái: {'Đã kích hoạt' if key_doc.get('device_id') else 'Chưa kích hoạt'}"
        )

        confirm = input("\nBạn có chắc muốn xóa key này? (y/N): ").strip().lower()

        if confirm == "y":
            result = key_manager.keys_collection.delete_one({"key": key_to_delete})
            if result.deleted_count > 0:
                print("✅ Xóa key thành công!")
            else:
                print("❌ Không thể xóa key")
        else:
            print("⏹️ Hủy bỏ xóa key")

    except Exception as e:
        print(f"❌ Lỗi khi xóa key: {str(e)}")


def update_key_expiry(key_manager):
    """Cập nhật thời hạn key"""
    print("\n⏰ CẬP NHẬT THỜI HẠN KEY")
    print("-" * 30)

    key_to_update = input("Nhập key cần cập nhật: ").strip()

    if not key_to_update:
        print("❌ Vui lòng nhập key")
        return

    try:
        # Tìm key
        key_doc = key_manager.keys_collection.find_one({"key": key_to_update})

        if not key_doc:
            print("❌ Key không tồn tại")
            return

        print(f"\nThông tin key hiện tại:")
        print(f"Key: {key_doc.get('key')}")
        current_expiry = key_doc.get("expired_date")
        if current_expiry:
            print(f"Hết hạn hiện tại: {current_expiry.strftime('%d/%m/%Y %H:%M:%S')}")
        else:
            print("Hết hạn hiện tại: Không giới hạn")

        print("\nChọn thời hạn mới:")
        print("1. 7 ngày")
        print("2. 30 ngày")
        print("3. 90 ngày")
        print("4. 1 năm")
        print("5. Không giới hạn")

        expiry_choice = input("Chọn (1-5): ").strip()

        new_expiry_date = None
        if expiry_choice == "1":
            new_expiry_date = datetime.now() + timedelta(days=7)
        elif expiry_choice == "2":
            new_expiry_date = datetime.now() + timedelta(days=30)
        elif expiry_choice == "3":
            new_expiry_date = datetime.now() + timedelta(days=90)
        elif expiry_choice == "4":
            new_expiry_date = datetime.now() + timedelta(days=365)

        # Cập nhật
        result = key_manager.keys_collection.update_one(
            {"key": key_to_update}, {"$set": {"expired_date": new_expiry_date}}
        )

        if result.modified_count > 0:
            print("✅ Cập nhật thời hạn key thành công!")
            if new_expiry_date:
                print(
                    f"⏰ Thời hạn mới: {new_expiry_date.strftime('%d/%m/%Y %H:%M:%S')}"
                )
            else:
                print("⏰ Thời hạn mới: Không giới hạn")
        else:
            print("❌ Không thể cập nhật key")

    except Exception as e:
        print(f"❌ Lỗi khi cập nhật key: {str(e)}")


def show_key_statistics(key_manager):
    """Hiển thị thống kê key"""
    print("\n📊 THỐNG KÊ KEY")
    print("-" * 30)

    try:
        total_keys = key_manager.keys_collection.count_documents({})
        activated_keys = key_manager.keys_collection.count_documents(
            {"device_id": {"$ne": None}}
        )
        expired_keys = key_manager.keys_collection.count_documents(
            {"expired_date": {"$lt": datetime.now()}}
        )
        unlimited_keys = key_manager.keys_collection.count_documents(
            {"expired_date": None}
        )

        print(f"📈 Tổng số key: {total_keys}")
        print(f"✅ Key đã kích hoạt: {activated_keys}")
        print(f"⏳ Key chưa kích hoạt: {total_keys - activated_keys}")
        print(f"❌ Key hết hạn: {expired_keys}")
        print(f"♾️ Key không giới hạn: {unlimited_keys}")

        # Key được tạo trong 7 ngày qua
        week_ago = datetime.now() - timedelta(days=7)
        recent_keys = key_manager.keys_collection.count_documents(
            {"created_date": {"$gte": week_ago}}
        )
        print(f"🆕 Key tạo trong 7 ngày qua: {recent_keys}")

    except Exception as e:
        print(f"❌ Lỗi khi lấy thống kê: {str(e)}")


# Thêm import cần thiết


# Chương trình chính cho admin
def run_admin_panel():
    """Chạy panel admin"""
    admin_password = "admin123"  # Đổi password này trong thực tế

    print("🔐 ĐĂNG NHẬP ADMIN")
    password = input("Nhập mật khẩu admin: ")

    if password != admin_password:
        print("❌ Mật khẩu không đúng!")
        return

    admin_key_management()


# Uncomment dòng dưới để chạy admin panel
run_admin_panel()
