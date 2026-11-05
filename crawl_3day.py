import time
import json
import os
import re
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
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

def init_driver():
    """Mở trình duyệt Chrome với Profile cố định"""
    options = webdriver.ChromeOptions()
    profile_path = os.path.join(os.getcwd(), "chrome_profile")
    options.add_argument(f"--user-data-dir={profile_path}")
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

def check_thoi_gian_cu(thoi_gian_text):
    """
    Kiểm tra xem bài viết đã cũ hơn 3 ngày chưa.
    Trả về True nếu cũ hơn 3 ngày, False nếu trong vòng 3 ngày.
    """
    if not thoi_gian_text:
        return False # Không rõ thời gian thì cứ coi là mới để cào tiếp

    text = thoi_gian_text.lower().strip()

    # Xử lý các mốc thời gian ngắn (giờ, phút, giây, vừa xong) -> Chắc chắn là mới
    if any(x in text for x in ["giây", "phút", "giờ", "vừa xong", "mới đây"]):
        return False

    # Xử lý các mốc thời gian dài (ngày, tuần, tháng, năm)
    match = re.search(r"(\d+)\s*(ngày|tuần|tháng|năm)", text)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        
        if unit == "ngày" and amount >= 3:
            return True
        if unit == "tuần" or unit == "tháng" or unit == "năm":
            return True

    # Xử lý trường hợp "hôm qua", "hôm kia", "thứ 2", "tháng 10"
    if "hôm qua" in text or "hôm kia" in text:
        return False # Hôm qua (1 ngày), hôm kia (2 ngày) vẫn nằm trong mốc 3 ngày
        
    return False # Các trường hợp còn lại (ví dụ ghi "Thứ 2", "Tháng 10") thì bỏ qua, không dừng

def crawl_3_days(url, max_scrolls=100):
    """Quét TOÀN BỘ bài viết trong vòng 3 NGÀY."""
    init_db()
    
    driver = init_driver()
    print("🌐 [CHẾ ĐỘ 3 NGÀY] Đang mở trình duyệt...")

    cookies_loaded = load_cookies(driver, url)
    if cookies_loaded:
        print("🔄 Đã load cookies, refresh trang...")
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

    posts_data = []
    skipped_data = [] 
    print("🚀 Bắt đầu quét dữ liệu 3 ngày...")

    rules = load_rules()
    last_height = driver.execute_script("return document.body.scrollHeight")
    flag_stop = False
    so_lan_cuon = 0

    while not flag_stop and so_lan_cuon < max_scrolls:
        so_lan_cuon += 1
        print(f"🖱️ Đang cuộn trang lần {so_lan_cuon}/{max_scrolls}...")
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5) 

        articles = driver.find_elements(By.CSS_SELECTOR, 'div[role="article"], div[aria-posinset]')
        print(f"🔎 Đang thấy {len(articles)} bài viết trên màn hình...")
            
        for article in articles:
            try:
                text = article.text.strip()

                # Bộ lọc comment (Bỏ qua bài quá ngắn)
                if len(text) < 80: 
                    continue
                if "Reply" in text and len(text) < 150 and ("ib" in text.lower() or "nhắn" in text.lower()):
                    continue

                if not text:
                    img_elems = article.find_elements(By.CSS_SELECTOR, "img[src*='scontent']")
                    if img_elems:
                        img_url = img_elems[0].get_attribute("src")
                        text = extract_text_from_image(img_url)

                if not text: continue
                if text in [p.get("full_content", "") for p in posts_data]: continue
                if is_post_exists(text): continue

                # Kiểm tra thời gian
                try:
                    time_elem = article.find_element(
                        By.XPATH,
                        ".//*[contains(text(),'giờ') or contains(text(),'phút') or contains(text(),'ngày') or contains(text(),'vừa xong') or contains(text(),'tuần') or contains(text(),'tháng') or contains(text(),'hôm')]",
                    )
                    if check_thoi_gian_cu(time_elem.text):
                        print("⏹️ Đã chạm mốc bài cũ hơn 3 ngày, dừng quét!")
                        flag_stop = True
                        break
                except: pass

                nguoi_gui = ""
                try:
                    name_elem = article.find_element(By.CSS_SELECTOR, '[data-ad-rendering-role="profile_name"]')
                    nguoi_gui = name_elem.text
                except: pass

                url_bai_viet = ""
                try:
                    link_elem = article.find_element(By.CSS_SELECTOR, "a[href*='/posts/'], a[href*='/permalink/']")
                    url_bai_viet = link_elem.get_attribute("href")
                except: pass

                label = classify_post(text)
                
                if label != "ỨNG VIÊN":
                    skipped_data.append({
                        "ly_do": label,
                        "noi_dung": text,
                        "nguoi_gui": nguoi_gui,
                        "url_bai_viet": url_bai_viet
                    })
                    print(f"⏭️ Bỏ qua bài {label}")
                    continue

                print(f"🔍 Đang phân tích ứng viên...")
                jobs_analyzed = analyze_post_full(text, group_name=url)

                for job_data in jobs_analyzed:
                    analyzed = apply_rules(job_data["job_content"], job_data["analyzed"], rules)
                    posts_data.append({
                        "ten_nhom": url,
                        "raw_content": job_data["job_content"],
                        "full_content": text,
                        "nguoi_gui": nguoi_gui,
                        "url_bai_viet": url_bai_viet,
                        "url_nhom": url,
                        "label": label,
                        "analyzed": analyzed
                    })
                    print(f"   ✅ Ứng viên {len(posts_data)}: {analyzed.get('makeAI', '')[:50]}...")

            except Exception as e:
                if "stale element reference" not in str(e).lower():
                    print(f"⚠️ Lỗi: {e}")
                continue

        if flag_stop: break

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("📭 Đã cuộn đến cuối trang.")
            break
        last_height = new_height

    driver.quit()
    
    # Lưu file danh sách bỏ qua
    with open("danh_sach_bo_qua.json", "w", encoding="utf-8") as f:
        json.dump(skipped_data, f, ensure_ascii=False, indent=2)
    print(f"💾 Đã lưu {len(skipped_data)} bài bị bỏ qua vào: danh_sach_bo_qua.json")

    print(f"\n🎉 Hoàn thành quét 3 ngày! Thu thập được {len(posts_data)} ứng viên.")
    return posts_data


# =========================================================
# KHỐI CHẠY CHÍNH
# =========================================================
if __name__ == "__main__":
    URL = "https://www.facebook.com/groups/tokuteiginothucpham.japan" 
    MAX_SCROLLS = 100 
    OUTPUT_FILE = "ket_qua_3day.json"

    print("=" * 60)
    print("🚀 BẮT ĐẦU QUÉT TOÀN BỘ DỮ LIỆU 3 NGÀY")
    print("=" * 60)

    posts = crawl_3_days(URL, max_scrolls=MAX_SCROLLS)

    if posts:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Đã lưu JSON: {OUTPUT_FILE}")
        print("📤 Đang đẩy lên Google Sheets...")
        push_posts_to_sheet(posts)
    else:
        print("⚠️ Không tìm thấy ứng viên nào trong 3 ngày qua.")