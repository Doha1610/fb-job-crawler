from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI
from src.cookie_manager import load_cookies, save_cookies
from src.database import init_db, save_job, is_post_exists
from src.classifier import classify_post
from src.ocr import extract_text_from_image
from src.ai_analyzer import analyze_post_full
from src.rules_engine import load_rules, apply_rules

load_dotenv()

# ===== Khởi tạo client với base_url =====
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.xah.io/v1"
)
MODEL = "gpt-5.6-sol"
# =========================================


def tinh_thoi_gian(thoi_gian_text):
    """Chuyển chuỗi thời gian tiếng Việt thành datetime"""
    try:
        weekday_mapping = {
            "Thứ Hai": "Monday",
            "Thứ Ba": "Tuesday",
            "Thứ Tư": "Wednesday",
            "Thứ Năm": "Thursday",
            "Thứ Sáu": "Friday",
            "Thứ bảy": "Saturday",
            "Chủ Nhật": "Sunday",
        }
        for vietnamese, english in weekday_mapping.items():
            if vietnamese in thoi_gian_text:
                thoi_gian_text = thoi_gian_text.replace(vietnamese, english)
                break
        processed_string = thoi_gian_text.replace("Tháng ", "").replace("lúc ", "")
        return datetime.strptime(processed_string, "%A, %d %m, %Y %H:%M")
    except Exception as e:
        print(f"⚠️ Lỗi parse thời gian: {e}")
        return None


def init_driver():
    """Mở trình duyệt Chrome"""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def crawl_and_analyze(url, max_posts=15):
    """
    Crawl + phân tích 2 tầng + áp rules.
    Logic:
    - Có text → AI
    - Không text → OCR ảnh
    - Không gì → bỏ qua
    - Đã có trong DB → bỏ qua
    """
    driver = init_driver()
    print("🌐 Đang mở trình duyệt...")

    # Xử lý cookies
    cookies_loaded = load_cookies(driver, url)
    if cookies_loaded:
        print("🔄 Đã load cookies, refresh trang...")
        driver.refresh()
        time.sleep(3)
    else:
        print("🔐 Lần đầu chạy, vui lòng đăng nhập Facebook...")
        driver.get(url)
        time.sleep(3)
        input("✅ Đăng nhập xong thì nhấn Enter để tiếp tục...")
        save_cookies(driver)
        driver.refresh()
        time.sleep(3)

    posts_data = []
    print("🚀 Bắt đầu crawl và phân tích...")

    # ===== LOAD RULES 1 LẦN =====
    rules = load_rules()
    print(f"📋 Đã load rules: {len(rules)} nhóm từ khóa")
    # ============================

    # Mốc thời gian 3 giờ trước
    now = datetime.now()
    three_hours_ago = now - timedelta(hours=3)
    three_hours_ago_timestamp = int(three_hours_ago.timestamp())

    last_height = driver.execute_script("return document.body.scrollHeight")
    flag_stop = False

    while len(posts_data) < max_posts and not flag_stop:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        articles = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")

        for article in articles:
            try:
                # ===== 1. LẤY TEXT =====
                text = article.text.strip()

                # ===== 2. KHÔNG CÓ TEXT → OCR ẢNH =====
                if not text:
                    print("\n🖼️ Không có text, thử OCR ảnh...")
                    img_url = None
                    try:
                        img_elems = article.find_elements(By.CSS_SELECTOR, "img[src*='scontent']")
                        if img_elems:
                            img_url = img_elems[0].get_attribute("src")
                    except:
                        pass

                    if img_url:
                        text = extract_text_from_image(img_url)
                        if text:
                            print(f"✅ OCR đọc được text")
                        else:
                            print("⏭️ OCR không đọc được → bỏ qua")
                            continue
                    else:
                        print("⏭️ Không tìm thấy ảnh → bỏ qua")
                        continue

                # ===== 3. VẪN KHÔNG CÓ TEXT → BỎ QUA =====
                if not text:
                    continue

                # ===== 4. KIỂM TRA TRÙNG =====
                # 4.1: Trong session hiện tại
                if text in [p.get("full_content", "") for p in posts_data]:
                    print("⏭️ Bài đã có trong session → bỏ qua")
                    continue

                # 4.2: Trong database
                if is_post_exists(text):
                    print("⏭️ Bài đã có trong DB → bỏ qua")
                    continue

                # ===== 5. LẤY THỜI GIAN =====
                try:
                    time_elem = article.find_element(
                        By.XPATH, ".//*[contains(text(),'Thứ') or contains(text(),'giờ') or contains(text(),'phút')]"
                    )
                    thoi_gian = tinh_thoi_gian(time_elem.text)
                    if thoi_gian:
                        if int(thoi_gian.timestamp()) <= three_hours_ago_timestamp:
                            print("⏹️ Bài cũ hơn 3 giờ, dừng!")
                            flag_stop = True
                            break
                except:
                    pass

                # ===== 6. LẤY METADATA =====
                nguoi_gui = ""
                try:
                    name_elem = article.find_element(
                        By.CSS_SELECTOR, '[data-ad-rendering-role="profile_name"]'
                    )
                    nguoi_gui = name_elem.text
                except:
                    pass

                url_bai_viet = ""
                try:
                    link_elem = article.find_element(
                        By.CSS_SELECTOR, "a[href*='/posts/'], a[href*='/permalink/']"
                    )
                    url_bai_viet = link_elem.get_attribute("href")
                except:
                    pass

                # ===== 7. PHÂN LOẠI =====
                label = classify_post(text)
                print(f"🏷️ Nhãn: {label}")

                if label == "TIN RÁC":
                    print("⏭️ Bỏ qua tin rác")
                    continue

                # ===== 8. PHÂN TÍCH AI 2 TẦNG =====
                print(f"🔍 Đang phân tích bài {len(posts_data) + 1}...")
                jobs_analyzed = analyze_post_full(text)

                # Mỗi job tách được → 1 record
                for job_data in jobs_analyzed:
                    analyzed = job_data["analyzed"]
                    job_content = job_data["job_content"]

                    # ===== 8.1: ÁP RULES =====
                    analyzed = apply_rules(job_content, analyzed, rules)

                    posts_data.append({
                        "ten_nhom": url,
                        "raw_content": job_content,
                        "full_content": text,
                        "nguoi_gui": nguoi_gui,
                        "url_bai_viet": url_bai_viet,
                        "url_nhom": url,
                        "label": label,
                        "analyzed": analyzed
                    })

                    print(f"   ✅ Job {len(posts_data)}: {analyzed.get('summary', '')[:50]}...")

                print("-" * 50)

                if len(posts_data) >= max_posts:
                    break

            except Exception as e:
                print(f"⚠️ Lỗi: {e}")
                continue

        if flag_stop:
            break

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("📭 Không còn bài mới.")
            break
        last_height = new_height

    driver.quit()
    print(f"\n🎉 Hoàn thành! Đã crawl {len(posts_data)} bài MỚI.")
    return posts_data


def crawl_and_analyze_save(url, max_posts=15, output_file="posts_analyzed.json"):
    """Crawl, phân tích, lưu JSON + SQLite"""
    posts = crawl_and_analyze(url, max_posts)

    if posts:
        # Lưu JSON
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Đã lưu JSON: {output_file}")

        # Lưu SQLite
        init_db()
        saved_count = 0
        for post in posts:
            if save_job(post):
                saved_count += 1
        print(f"💾 Đã lưu {saved_count}/{len(posts)} bài vào database")
    else:
        print("⚠️ Không có bài mới để lưu")

    return posts


def delete_cookies():
    """Xóa cookies"""
    from src.cookie_manager import delete_cookies as del_cookies
    del_cookies()