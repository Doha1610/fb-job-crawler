import time
import json
import os
import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    StaleElementReferenceException,
    NoSuchElementException
)
from webdriver_manager.chrome import ChromeDriverManager

# ===== IMPORT TỪ THƯ MỤC SRC =====
from src.ai_analyzer import analyze_post_full
from src.classifier import classify_post
from src.cookie_manager import load_cookies, save_cookies
from src.database import init_db, save_job, is_post_exists
from src.ocr import extract_text_from_image
from src.rules_engine import load_rules, apply_rules
from src.google_sheets import push_posts_to_sheet
# ==================================


# =========================================================
# 1. KHỞI TẠO CHROME
# =========================================================

def init_driver():
    """Mở Chrome bằng profile cố định."""
    options = webdriver.ChromeOptions()
    profile_path = os.path.join(os.getcwd(), "chrome_profile")
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


# =========================================================
# 2. KIỂM TRA THỜI GIAN BÀI VIẾT
# =========================================================

def check_thoi_gian_cu(thoi_gian_text):
    """Trả về True nếu bài viết đã cũ từ 3 ngày trở lên."""
    if not thoi_gian_text:
        return False

    text = thoi_gian_text.lower().strip()

    tu_khoa_moi = ["giây", "phút", "giờ", "vừa xong", "mới đây"]
    if any(keyword in text for keyword in tu_khoa_moi):
        return False

    match = re.search(r"(\d+)\s*(ngày|tuần|tháng|năm)", text)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        if unit == "ngày" and amount >= 3:
            return True
        if unit in ["tuần", "tháng", "năm"]:
            return True

    if "hôm qua" in text or "hôm kia" in text:
        return False

    return False


# =========================================================
# 3. LẤY NỘI DUNG BÀI ĐĂNG GỐC (ĐÃ CẬP NHẬT)
# =========================================================

def get_author_post_content(article):
    """
    Chỉ lấy nội dung bài đăng gốc.
    Có cơ chế phát hiện và bỏ qua nếu thẻ hiện tại là COMMENT.
    """
    # 1. KIỂM TRA: Nếu là comment thì bỏ qua ngay lập tức
    try:
        aria_label = article.get_attribute("aria-label")
        if aria_label and "Comment" in aria_label:
            return "", None
    except:
        pass

    # 2. Lấy các selector chính xác cho bài đăng gốc
    selectors = [
        'div[data-ad-rendering-role="story_message"]',
        'div[data-ad-preview="message"]',
        'div[data-ad-comet-preview="message"]',
        'div.html-div'
    ]

    empty_element = None

    for selector in selectors:
        try:
            elements = article.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                text = element.text.strip()

                # Loại bỏ các text rác
                if text in ["Author", "Reply", "Follow", "See more", "Xem thêm", "Share", "Chia sẻ", "Thích", "Bình luận"]:
                    continue

                if text and len(text) > 10:  # Text phải đủ dài để tránh lấy tên
                    return text, element
                
                if empty_element is None:
                    empty_element = element

        except StaleElementReferenceException:
            continue

    if empty_element is not None:
        return "", empty_element

    return "", None


# =========================================================
# 4. LẤY TÊN NGƯỜI ĐĂNG
# =========================================================

def get_author_name(article):
    """Lấy tên người đăng bài."""
    selectors = [
        '[data-ad-rendering-role="profile_name"]',
        'h2 a[role="link"]',
        'h3 a[role="link"]'
    ]
    for selector in selectors:
        try:
            elements = article.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                name = element.text.strip()
                if name:
                    return name
        except StaleElementReferenceException:
            continue
    return ""


# =========================================================
# 5. LẤY LINK BÀI VIẾT
# =========================================================

def get_post_url(article):
    """Lấy URL của bài đăng."""
    selectors = [
        'a[href*="/posts/"]',
        'a[href*="/permalink/"]'
    ]
    for selector in selectors:
        try:
            elements = article.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                url = element.get_attribute("href")
                if url:
                    return url.split("?")[0]
        except StaleElementReferenceException:
            continue
    return ""


# =========================================================
# 6. LẤY THỜI GIAN ĐĂNG
# =========================================================

def get_post_time(article):
    """Chỉ kiểm tra phần tử thời gian của Facebook."""
    selectors = ["abbr", "time"]
    for selector in selectors:
        try:
            elements = article.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                time_text = (
                    element.get_attribute("aria-label")
                    or element.get_attribute("title")
                    or element.text
                )
                if time_text:
                    return time_text.strip()
        except StaleElementReferenceException:
            continue
    return ""


# =========================================================
# 7. OCR ẢNH TRONG VÙNG BÀI ĐĂNG
# =========================================================

def get_post_image_text(message_element):
    """Chỉ tìm ảnh nằm trong vùng nội dung bài đăng."""
    if message_element is None:
        return ""
    try:
        images = message_element.find_elements(By.CSS_SELECTOR, "img[src*='scontent']")
        for image in images:
            try:
                image_url = image.get_attribute("src")
                if image_url:
                    text = extract_text_from_image(image_url)
                    if text and text.strip():
                        return text.strip()
            except Exception as e:
                print(f"⚠️ OCR ảnh thất bại: {e}")
    except StaleElementReferenceException:
        pass
    return ""


# =========================================================
# 8. LƯU DANH SÁCH BÀI BỊ BỎ QUA
# =========================================================

def save_skipped_data(skipped_data):
    """Lưu các bài không được phân loại là ứng viên."""
    file_path = "danh_sach_bo_qua.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(skipped_data, f, ensure_ascii=False, indent=2)
    print(f"💾 Đã lưu {len(skipped_data)} bài bỏ qua vào {file_path}")


# =========================================================
# 9. HÀM CRAWL CHÍNH
# =========================================================

def crawl_3_days(url, max_scrolls=100):
    """
    Quét bài viết trong khoảng 3 ngày.
    """
    init_db()
    driver = init_driver()
    print("🌐 [CHẾ ĐỘ 3 NGÀY] Đang mở trình duyệt...")

    posts_data = []
    skipped_data = []
    seen_urls = set()
    seen_contents = set()

    try:
        # -------------------------------------------------
        # ĐĂNG NHẬP FACEBOOK
        # -------------------------------------------------
        cookies_loaded = load_cookies(driver, url)
        if cookies_loaded:
            print("🔄 Đã load cookies, đang refresh trang...")
            driver.refresh()
            time.sleep(10)
        else:
            print("🔐 Lần đầu chạy, vui lòng đăng nhập Facebook...")
            driver.get(url)
            time.sleep(10)
            input("✅ Đăng nhập xong thì nhấn Enter để tiếp tục...")
            save_cookies(driver)
            driver.refresh()
            time.sleep(10)

        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(2)

        rules = load_rules()
        last_height = driver.execute_script("return document.body.scrollHeight")
        flag_stop = False
        so_lan_cuon = 0

        print("\n🚀 Bắt đầu quét dữ liệu 3 ngày...\n")

        # =================================================
        # VÒNG LẶP CUỘN FACEBOOK
        # =================================================
        while not flag_stop and so_lan_cuon < max_scrolls:
            so_lan_cuon += 1
            print(f"\n🖱️ Đang cuộn lần {so_lan_cuon}/{max_scrolls}...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

            # SỬA: Ưu tiên tìm thẻ có aria-posinset (bài đăng gốc)
            articles = driver.find_elements(By.CSS_SELECTOR, 'div[aria-posinset]')
            if not articles:
                # Nếu không có, quay lại dùng role='article'
                articles = driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]')
            
            print(f"🔎 Đang thấy {len(articles)} bài viết trên màn hình...")

            # =============================================
            # XỬ LÝ TỪNG BÀI ĐĂNG
            # =============================================
            for article in articles:
                try:
                    nguoi_gui = get_author_name(article)
                    url_bai_viet = get_post_url(article)

                    # 1. CHỐNG TRÙNG THEO URL
                    if url_bai_viet and url_bai_viet in seen_urls:
                        continue
                    if url_bai_viet:
                        seen_urls.add(url_bai_viet)

                    # 2. LẤY NỘI DUNG BÀI GỐC
                    text, message_element = get_author_post_content(article)
                    if not text.strip():
                        text = get_post_image_text(message_element)

                    if not text or not text.strip():
                        skipped_data.append({
                            "ly_do": (
                                "KHÔNG TÌM THẤY VÙNG NỘI DUNG BÀI ĐĂNG"
                                if message_element is None
                                else "KHÔNG LẤY ĐƯỢC NỘI DUNG TỪ VĂN BẢN HOẶC ẢNH"
                            ),
                            "noi_dung": "",
                            "nguoi_gui": nguoi_gui,
                            "url_bai_viet": url_bai_viet
                        })
                        continue

                    if text in seen_contents:
                        continue
                    seen_contents.add(text)

                    # 3. KIỂM TRA THỜI GIAN
                    thoi_gian = get_post_time(article)
                    if check_thoi_gian_cu(thoi_gian):
                        print(f"⏹️ Gặp bài cũ hơn 3 ngày: {thoi_gian}")
                        flag_stop = True
                        break

                    # 4. KIỂM TRA DATABASE
                    if is_post_exists(text, url_bai_viet):
                        print("⏭️ Bài viết đã tồn tại trong database.")
                        continue

                    # 5. PHÂN LOẠI BÀI VIẾT
                    label = classify_post(text)
                    print(f"\n📌 Phân loại: {label}")
                    print(f"👤 Người đăng: {nguoi_gui}")
                    print(f"📝 Nội dung: {text[:100]}...")

                    if label != "ỨNG VIÊN":
                        skipped_data.append({
                            "ly_do": label,
                            "noi_dung": text,
                            "nguoi_gui": nguoi_gui,
                            "url_bai_viet": url_bai_viet
                        })
                        print(f"⏭️ Bỏ qua bài: {label}")
                        continue

                    # 6. PHÂN TÍCH ỨNG VIÊN BẰNG AI
                    print("🔍 Đang phân tích thông tin ứng viên...")
                    try:
                        jobs_analyzed = analyze_post_full(text, group_name=url)
                    except Exception as e:
                        print(f"❌ Lỗi AI Analyzer: {e}")
                        skipped_data.append({
                            "ly_do": "LỖI PHÂN TÍCH AI",
                            "noi_dung": text,
                            "nguoi_gui": nguoi_gui,
                            "url_bai_viet": url_bai_viet,
                            "error": str(e)
                        })
                        continue

                    if not jobs_analyzed:
                        skipped_data.append({
                            "ly_do": "AI KHÔNG TRẢ VỀ KẾT QUẢ",
                            "noi_dung": text,
                            "nguoi_gui": nguoi_gui,
                            "url_bai_viet": url_bai_viet
                        })
                        continue

                    # 7. CHỈ LẤY MỘT KẾT QUẢ CHO MỘT BÀI
                    job_data = jobs_analyzed[0]
                    analyzed = apply_rules(
                        job_data["job_content"],
                        job_data["analyzed"],
                        rules
                    )

                    post = {
                        "ten_nhom": url,
                        "raw_content": text,
                        "full_content": text,
                        "nguoi_gui": nguoi_gui,
                        "url_bai_viet": url_bai_viet,
                        "url_nhom": url,
                        "label": "ỨNG VIÊN",
                        "analyzed": analyzed
                    }

                    # 8. LƯU VÀO SQLITE
                    try:
                        saved = save_job(post)
                    except Exception as e:
                        print(f"⚠️ Lỗi lưu database: {e}")
                        saved = False

                    if not saved:
                        skipped_data.append({
                            "ly_do": "KHÔNG LƯU ĐƯỢC VÀO DATABASE",
                            "noi_dung": text,
                            "nguoi_gui": nguoi_gui,
                            "url_bai_viet": url_bai_viet
                        })
                        continue

                    # 9. THÊM VÀO DANH SÁCH KẾT QUẢ
                    posts_data.append(post)
                    print(f"✅ Đã thu thập ứng viên thứ {len(posts_data)}")
                    print(f"   Tóm tắt: {analyzed.get('makeAI', '')[:100]}")

                except StaleElementReferenceException:
                    continue
                except Exception as e:
                    print(f"⚠️ Lỗi xử lý bài viết: {e}")
                    continue

            # =============================================
            # KIỂM TRA ĐIỀU KIỆN DỪNG
            # =============================================
            if flag_stop:
                break

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("📭 Không còn nội dung mới để cuộn.")
                break
            last_height = new_height

    finally:
        driver.quit()

    # =====================================================
    # LƯU DANH SÁCH BỎ QUA
    # =====================================================
    save_skipped_data(skipped_data)

    print("\n" + "=" * 60)
    print("🎉 HOÀN THÀNH QUÉT DỮ LIỆU!")
    print(f"✅ Tổng ứng viên thu thập: {len(posts_data)}")
    print(f"⏭️ Tổng bài bỏ qua: {len(skipped_data)}")
    print("=" * 60)

    return posts_data


# =========================================================
# 10. KHỐI CHẠY CHÍNH
# =========================================================

if __name__ == "__main__":
    URL = "https://www.facebook.com/groups/tokuteiginothucpham.japan"
    
    # Ban đầu nên chạy ít lượt để kiểm tra
    MAX_SCROLLS = 10
    OUTPUT_FILE = "ket_qua_3day.json"

    print("=" * 60)
    print("🚀 BẮT ĐẦU QUÉT BÀI VIẾT FACEBOOK")
    print("=" * 60)

    posts = crawl_3_days(URL, max_scrolls=MAX_SCROLLS)

    # -----------------------------------------------------
    # LƯU JSON
    # -----------------------------------------------------
    if posts:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Đã lưu kết quả vào: {OUTPUT_FILE}")

        # -------------------------------------------------
        # ĐẨY GOOGLE SHEETS
        # -------------------------------------------------
        print("\n📤 Đang đẩy dữ liệu lên Google Sheets...")
        try:
            push_posts_to_sheet(posts)
            print("✅ Đẩy Google Sheets hoàn tất!")
        except Exception as e:
            print(f"❌ Lỗi Google Sheets: {e}")
    else:
        print("\n⚠️ Không tìm thấy ứng viên nào.")