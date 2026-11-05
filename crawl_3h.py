from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
import re
from datetime import datetime, timedelta

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
MAX_POSTS_PER_GROUP = 5      
DELAY_BETWEEN_GROUPS = 15    
OUTPUT_FILE = "ket_qua_3h.json"
# ====================

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

def tinh_thoi_gian(thoi_gian_text):
    """Chuyển chuỗi thời gian tiếng Việt thành datetime"""
    try:
        thoi_gian_text_lower = thoi_gian_text.lower()
        if "vừa xong" in thoi_gian_text_lower:
            return datetime.now()
            
        match_gio = re.search(r'(\d+)\s*giờ', thoi_gian_text_lower)
        if match_gio:
            return datetime.now() - timedelta(hours=int(match_gio.group(1)))
            
        match_phut = re.search(r'(\d+)\s*phút', thoi_gian_text_lower)
        if match_phut:
            return datetime.now() - timedelta(minutes=int(match_phut.group(1)))

        weekday_mapping = {
            "Thứ Hai": "Monday", "Thứ Ba": "Tuesday", "Thứ Tư": "Wednesday",
            "Thứ Năm": "Thursday", "Thứ Sáu": "Friday", "Thứ bảy": "Saturday", "Chủ Nhật": "Sunday",
        }
        for vietnamese, english in weekday_mapping.items():
            if vietnamese in thoi_gian_text:
                thoi_gian_text = thoi_gian_text.replace(vietnamese, english)
                break
                
        processed_string = thoi_gian_text.replace("Tháng ", "").replace("lúc ", "")
        return datetime.strptime(processed_string, "%A, %d %m, %Y %H:%M")
        
    except Exception as e:
        return datetime.now() 

def crawl_3_hours(url, max_posts=5):
    """Crawl và phân tích bài viết trong vòng 3 giờ"""
    init_db()
    driver = init_driver()
    print("🌐 [CHẾ ĐỘ 3 GIỜ] Đang mở trình duyệt...")

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
    rules = load_rules()
    
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
                text = article.text.strip()
                if not text:
                    img_elems = article.find_elements(By.CSS_SELECTOR, "img[src*='scontent']")
                    if img_elems:
                        text = extract_text_from_image(img_elems[0].get_attribute("src"))
                
                if not text: continue
                if text in [p.get("full_content", "") for p in posts_data]: continue
                if is_post_exists(text): continue

                try:
                    time_elem = article.find_element(By.XPATH, ".//*[contains(text(),'Thứ') or contains(text(),'giờ') or contains(text(),'phút')]")
                    thoi_gian = tinh_thoi_gian(time_elem.text)
                    if thoi_gian and int(thoi_gian.timestamp()) <= three_hours_ago_timestamp:
                        print("⏹️ Bài cũ hơn 3 giờ, dừng!")
                        flag_stop = True
                        break
                except: pass

                nguoi_gui = ""
                try:
                    nguoi_gui = article.find_element(By.CSS_SELECTOR, '[data-ad-rendering-role="profile_name"]').text
                except: pass

                url_bai_viet = ""
                try:
                    url_bai_viet = article.find_element(By.CSS_SELECTOR, "a[href*='/posts/'], a[href*='/permalink/']").get_attribute("href")
                except: pass

                label = classify_post(text)
                if label != "ỨNG VIÊN": continue

                print(f"🔍 Đang phân tích ứng viên...")
                jobs_analyzed = analyze_post_full(text, group_name=url)

                for job_data in jobs_analyzed:
                    analyzed = apply_rules(job_data["job_content"], job_data["analyzed"], rules)
                    posts_data.append({
                        "ten_nhom": url, "raw_content": job_data["job_content"], "full_content": text,
                        "nguoi_gui": nguoi_gui, "url_bai_viet": url_bai_viet, "url_nhom": url,
                        "label": label, "analyzed": analyzed
                    })
                    print(f"   ✅ Ứng viên {len(posts_data)}: {analyzed.get('summary', '')[:50]}...")
                
                if len(posts_data) >= max_posts: break
            except Exception as e:
                if "stale element reference" not in str(e).lower(): print(f"⚠️ Lỗi: {e}")
                continue

        if flag_stop: break
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("📭 Không còn bài mới.")
            break
        last_height = new_height

    driver.quit()
    return posts_data

def load_groups():
    if not os.path.exists(GROUPS_FILE):
        print(f"⚠️ Không tìm thấy file: {GROUPS_FILE}")
        return []
    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

# =========================================================
# KHỐI CHẠY CHÍNH
# =========================================================
if __name__ == "__main__":
    groups = load_groups()
    all_posts = []
    
    print("=" * 60)
    print(f"🚀 BẮT ĐẦU CRAWL 3 GIỜ ({len(groups)} GROUPS)")
    print("=" * 60)

    for i, url in enumerate(groups, 1):
        print(f"\n🌐 GROUP {i}/{len(groups)}: {url[:50]}...")
        posts = crawl_3_hours(url, max_posts=MAX_POSTS_PER_GROUP)
        
        if posts:
            for post in posts:
                if save_job(post):
                    all_posts.append(post)
            print(f"✅ Group {i}: Lưu thành công {len(posts)} ứng viên.")
            
        if i < len(groups):
            print(f"⏸️ Nghỉ {DELAY_BETWEEN_GROUPS}s...")
            time.sleep(DELAY_BETWEEN_GROUPS)

    if all_posts:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_posts, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Đã lưu JSON: {OUTPUT_FILE}")
        print(f"📤 Đang đẩy {len(all_posts)} ứng viên lên Google Sheets...")
        push_posts_to_sheet(all_posts)
    else:
        print("\n⚠️ Không có ứng viên mới nào trong 3 giờ qua.")
        
    print("\n🎉 HOÀN THÀNH!")