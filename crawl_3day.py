import time
import json
import os
import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
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

# ===== CẤU HÌNH =====
GROUPS_FILE = "groups.txt"
MAX_SCROLLS_PER_GROUP = 20  # Số lần cuộn tối đa mỗi group (3 ngày cần cuộn sâu hơn)
DELAY_BETWEEN_GROUPS = 20    # Nghỉ 20s giữa các group
OUTPUT_FILE = "ket_qua_3day.json"
# ====================


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
# 2. ĐỌC DANH SÁCH GROUP
# =========================================================
def load_groups():
    """Đọc danh sách URL group từ file."""
    if not os.path.exists(GROUPS_FILE):
        print(f"⚠️ Không tìm thấy file: {GROUPS_FILE}")
        return []

    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        urls = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

    print(f"📋 Đã load {len(urls)} group từ {GROUPS_FILE}")
    return urls


# =========================================================
# 3. KIỂM TRA THỜI GIAN BÀI VIẾT (3 NGÀY)
# =========================================================
def check_thoi_gian_cu(thoi_gian_text):
    """
    Trả về True nếu bài viết đã cũ từ 3 ngày trở lên.
    Trả về False nếu bài mới hoặc không đủ thông tin.
    """
    if not thoi_gian_text:
        return False

    text = thoi_gian_text.lower().strip()

    # Bài mới (giây, phút, giờ)
    if any(kw in text for kw in ["giây", "phút", "giờ", "vừa xong", "mới đây"]):
        return False

    # Bài trong vài ngày
    match_ngay = re.search(r"(\d+)\s*ngày", text)
    if match_ngay:
        amount = int(match_ngay.group(1))
        if amount >= 3:
            return True
        return False

    # Tuần, tháng, năm -> Chắc chắn cũ
    if any(unit in text for unit in ["tuần", "tháng", "năm"]):
        return True

    # Hôm qua (1 ngày), hôm kia (2 ngày) -> Vẫn trong khoảng 3 ngày
    if "hôm qua" in text or "hôm kia" in text:
        return False

    return False


# =========================================================
# 4. LẤY NỘI DUNG BÀI ĐĂNG GỐC
# =========================================================
def get_author_post_content(article):
    """Chỉ lấy nội dung bài đăng gốc, bỏ qua comment."""
    try:
        aria_label = article.get_attribute("aria-label")
        if aria_label and "Comment" in aria_label:
            return "", None
    except:
        pass

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
                if text in ["Author", "Reply", "Follow", "See more", "Xem thêm", "Share", "Chia sẻ"]:
                    continue
                if text and len(text) > 10:
                    return text, element
                if empty_element is None:
                    empty_element = element
        except StaleElementReferenceException:
            continue

    if empty_element is not None:
        return "", empty_element
    return "", None


# =========================================================
# 5. LẤY TÊN NGƯỜI ĐĂNG
# =========================================================
def get_author_name(article):
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
# 6. LẤY LINK BÀI VIẾT
# =========================================================
def get_post_url(article):
    selectors = ['a[href*="/posts/"]', 'a[href*="/permalink/"]']
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
# 7. LẤY THỜI GIAN ĐĂNG
# =========================================================
def get_post_time(article):
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
# 8. OCR ẢNH
# =========================================================
def get_post_image_text(message_element):
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
            except Exception:
                pass
    except StaleElementReferenceException:
        pass
    return ""


# =========================================================
# 9. CRAWL 1 GROUP (3 NGÀY)
# =========================================================
def crawl_single_group(driver, url, rules, max_scrolls=20):
    """Crawl 1 group cụ thể, quét bài trong 3 ngày."""
    print(f"\n{'='*60}")
    print(f"🌐 ĐANG QUÉT: {url[:60]}...")
    print(f"{'='*60}")

    posts_data = []
    skipped_data = []
    seen_urls = set()
    seen_contents = set()

    driver.get(url)
    time.sleep(10)

    driver.execute_script("window.scrollBy(0, 500);")
    time.sleep(2)

    last_height = driver.execute_script("return document.body.scrollHeight")
    flag_stop = False
    so_lan_cuon = 0

    while not flag_stop and so_lan_cuon < max_scrolls:
        so_lan_cuon += 1
        print(f"\n🖱️ Cuộn lần {so_lan_cuon}/{max_scrolls}...")

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        articles = driver.find_elements(By.CSS_SELECTOR, 'div[aria-posinset]')
        if not articles:
            articles = driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]')

        print(f"🔎 Tìm thấy {len(articles)} bài viết trên màn hình...")

        for article in articles:
            try:
                nguoi_gui = get_author_name(article)
                url_bai_viet = get_post_url(article)

                if url_bai_viet and url_bai_viet in seen_urls:
                    continue
                if url_bai_viet:
                    seen_urls.add(url_bai_viet)

                text, message_element = get_author_post_content(article)
                if not text.strip():
                    text = get_post_image_text(message_element)

                if not text or not text.strip():
                    skipped_data.append({
                        "ly_do": "KHÔNG LẤY ĐƯỢC NỘI DUNG",
                        "noi_dung": "",
                        "nguoi_gui": nguoi_gui,
                        "url_bai_viet": url_bai_viet
                    })
                    continue

                if text in seen_contents:
                    continue
                seen_contents.add(text)

                thoi_gian = get_post_time(article)
                if check_thoi_gian_cu(thoi_gian):
                    print(f"⏹️ Gặp bài cũ hơn 3 ngày: {thoi_gian}")
                    flag_stop = True
                    break

                if is_post_exists(text, url_bai_viet):
                    print("⏭️ Bài đã có trong DB.")
                    continue

                label = classify_post(text)
                print(f"📌 {label} | {nguoi_gui} | {text[:60]}...")

                if label != "ỨNG VIÊN":
                    skipped_data.append({
                        "ly_do": label,
                        "noi_dung": text,
                        "nguoi_gui": nguoi_gui,
                        "url_bai_viet": url_bai_viet
                    })
                    continue

                print("🔍 Đang phân tích ứng viên...")
                try:
                    jobs_analyzed = analyze_post_full(text, group_name=url)
                except Exception as e:
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

                try:
                    saved = save_job(post)
                except Exception:
                    saved = False

                if not saved:
                    skipped_data.append({
                        "ly_do": "KHÔNG LƯU ĐƯỢC VÀO DATABASE",
                        "noi_dung": text,
                        "nguoi_gui": nguoi_gui,
                        "url_bai_viet": url_bai_viet
                    })
                    continue

                posts_data.append(post)
                print(f"✅ Đã thu thập ứng viên thứ {len(posts_data)}")
                print(f"   Tóm tắt: {analyzed.get('makeAI', '')[:100]}")

            except StaleElementReferenceException:
                continue
            except Exception as e:
                print(f"⚠️ Lỗi xử lý bài: {e}")
                continue

        if flag_stop:
            break

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("📭 Không còn nội dung mới.")
            break
        last_height = new_height

    print(f"\n✅ Group này: {len(posts_data)} ứng viên | {len(skipped_data)} bài bỏ qua")
    return posts_data, skipped_data


# =========================================================
# 10. HÀM CHÍNH: CRAWL NHIỀU GROUP (3 NGÀY)
# =========================================================
def crawl_3day_multiple_groups():
    """Crawl tất cả các group trong groups.txt, quét bài trong 3 ngày."""
    init_db()

    groups = load_groups()
    if not groups:
        print("❌ Không có group nào để crawl.")
        return [], []

    driver = init_driver()
    print("\n🌐 Đang mở trình duyệt...")

    try:
        # Đăng nhập ở group đầu tiên
        first_url = groups[0]
        cookies_loaded = load_cookies(driver, first_url)
        if cookies_loaded:
            print("🔄 Đã load cookies, refresh trang...")
            driver.refresh()
            time.sleep(10)
        else:
            print("🔐 Lần đầu chạy, vui lòng đăng nhập Facebook...")
            driver.get(first_url)
            time.sleep(10)
            input("✅ Đăng nhập xong nhấn Enter để tiếp tục...")
            save_cookies(driver)
            driver.refresh()
            time.sleep(10)

        rules = load_rules()

        all_posts = []
        all_skipped = []

        for i, url in enumerate(groups, 1):
            print(f"\n{'#'*60}")
            print(f"# GROUP {i}/{len(groups)}")
            print(f"{'#'*60}")

            try:
                posts, skipped = crawl_single_group(
                    driver,
                    url,
                    rules,
                    max_scrolls=MAX_SCROLLS_PER_GROUP
                )
                all_posts.extend(posts)
                all_skipped.extend(skipped)

            except Exception as e:
                print(f"❌ Lỗi group {url}: {e}")
                continue

            if i < len(groups):
                print(f"\n⏸️ Nghỉ {DELAY_BETWEEN_GROUPS}s trước group tiếp theo...")
                time.sleep(DELAY_BETWEEN_GROUPS)

        return all_posts, all_skipped

    finally:
        driver.quit()


# =========================================================
# 11. CHẠY CHÍNH
# =========================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 BẮT ĐẦU QUÉT NHIỀU GROUP (3 NGÀY GẦN NHẤT)")
    print("=" * 60)

    posts, skipped = crawl_3day_multiple_groups()

    # Lưu file bỏ qua
    with open("danh_sach_bo_qua_3day.json", "w", encoding="utf-8") as f:
        json.dump(skipped, f, ensure_ascii=False, indent=2)

    # Lưu JSON kết quả
    if posts:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Đã lưu {len(posts)} ứng viên vào: {OUTPUT_FILE}")

        print("\n📤 Đang đẩy lên Google Sheets...")
        try:
            push_posts_to_sheet(posts)
            print("✅ Đẩy Google Sheets thành công!")
        except Exception as e:
            print(f"❌ Lỗi Google Sheets: {e}")
    else:
        print("\n⚠️ Không tìm thấy ứng viên nào.")

    print("\n" + "=" * 60)
    print(f"🎉 HOÀN THÀNH!")
    print(f"   ✅ Tổng ứng viên: {len(posts)}")
    print(f"   ⏭️ Tổng bài bỏ qua: {len(skipped)}")
    print("=" * 60)