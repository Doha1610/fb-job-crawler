import pickle
import os
import time
COOKIE_FILE = "facebook_cookies.pkl"


def save_cookies(driver):
    """Lưu cookies sau khi đăng nhập"""
    try:
        with open(COOKIE_FILE, "wb") as f:
            pickle.dump(driver.get_cookies(), f)
        print("✅ Đã lưu cookies thành công!")
        return True
    except Exception as e:
        print(f"❌ Lỗi lưu cookies: {e}")
        return False


def load_cookies(driver, url):
    """Load cookies trước khi vào Facebook"""
    if os.path.exists(COOKIE_FILE):
        try:
            driver.get(url)
            time.sleep(2)

            with open(COOKIE_FILE, "rb") as f:
                cookies = pickle.load(f)

            for cookie in cookies:
                try:
                    if 'expiry' in cookie:
                        cookie['expiry'] = int(cookie['expiry'])
                    if 'sameSite' in cookie:
                        del cookie['sameSite']
                    driver.add_cookie(cookie)
                except Exception as e:
                    continue

            print(f"✅ Đã load {len(cookies)} cookies!")
            return True
        except Exception as e:
            print(f"❌ Lỗi load cookies: {e}")
            return False
    else:
        print("📝 Chưa có file cookies, cần đăng nhập lần đầu.")
        return False


# ===== THÊM HÀM NÀY =====
def delete_cookies():
    """Xóa file cookies (khi cần đăng nhập lại)"""
    if os.path.exists(COOKIE_FILE):
        os.remove(COOKIE_FILE)
        print("🗑️ Đã xóa file cookies!")
        return True
    print("ℹ️ Không tìm thấy file cookies để xóa.")
    return False
# ========================