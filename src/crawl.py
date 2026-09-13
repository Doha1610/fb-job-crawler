from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from src.cookie_manager import load_cookies, save_cookies
from src.database import init_db, save_job  # ← THÊM DÒNG NÀY

load_dotenv()

# ===== SỬA: Khởi tạo client với base_url của ckey.vn =====
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.xah.io/v1"  # Endpoint của ckey.vn
)
# ========================================================


def init_driver():
    """Mở trình duyệt Chrome"""
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")

    # Tùy chọn: thêm user-agent để tránh bị phát hiện
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    # Chạy script để ẩn webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver


def analyze_job_post(content: str) -> dict:
    """Phân tích bài đăng tuyển dụng bằng AI (dùng model của ckey.vn)"""
    prompt = f"""
Bạn là chuyên gia phân tích tin tuyển dụng đi Nhật.
Đọc bài đăng sau và trích xuất thông tin dưới dạng JSON:

Bài đăng:
{content}

Hãy trả về JSON với các trường:
{{
  "visa_type": "loại visa (kỹ sư, thực tập sinh, tokutei, v.v)",
  "industry": "ngành nghề (cơ khí, điện tử, xây dựng, nhà hàng, v.v)",
  "japanese_level": "trình độ tiếng Nhật (N1, N2, N3, N4, N5, hoặc không yêu cầu)",
  "gender": "giới tính (nam, nữ, không yêu cầu)",
  "location": "địa điểm làm việc (tỉnh/thành phố ở Nhật)",
  "salary": "mức lương (nếu có)",
  "requirements": "các yêu cầu khác",
  "benefits": "chế độ đãi ngộ",
  "summary": "tóm tắt ngắn gọn bài đăng"
}}

Nếu không có thông tin thì để chuỗi rỗng.
Chỉ trả về JSON, không kèm giải thích.
"""
    try:
        # ===== SỬA: Dùng model của ckey.vn =====
        response = client.chat.completions.create(
            model="gpt-5.6-sol",  # Model của ckey.vn
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        # ======================================

        result_text = response.choices[0].message.content.strip()

        # Xóa code block nếu có
        if result_text.startswith("```json"):
            result_text = result_text[7:-3]
        elif result_text.startswith("```"):
            result_text = result_text[3:-3]

        return json.loads(result_text)

    except Exception as e:
        print(f"❌ Lỗi phân tích: {e}")
        return {
            "visa_type": "",
            "industry": "",
            "japanese_level": "",
            "gender": "",
            "location": "",
            "salary": "",
            "requirements": "",
            "benefits": "",
            "summary": "",
        }


def crawl_and_analyze(url, max_posts=15):
    """Crawl và phân tích bài viết bằng AI, có lưu cookies"""
    driver = init_driver()
    print("🌐 Đang mở trình duyệt...")

    # ----- XỬ LÝ COOKIES -----
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

        # Lưu cookies
        save_cookies(driver)
        print("🔄 Refresh trang sau khi lưu cookies...")
        driver.refresh()
        time.sleep(3)

    # ----- BẮT ĐẦU CRAWL -----
    posts_data = []
    print("🚀 Bắt đầu crawl và phân tích...")

    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(posts_data) < max_posts:
        # Scroll xuống
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # Lấy bài viết
        articles = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")

        for article in articles:
            try:
                text = article.text.strip()

                if text and len(text) > 80:
                    if text not in [p["raw_content"] for p in posts_data]:
                        # Phân tích AI
                        print(f"\n🔍 Đang phân tích bài {len(posts_data) + 1}...")
                        analyzed = analyze_job_post(text)

                        posts_data.append({
                            "raw_content": text,
                            "analyzed": analyzed
                        })

                        # In preview
                        print(f"   ✅ Đã phân tích xong!")
                        print(f"   📌 Visa: {analyzed.get('visa_type')}")
                        print(f"   📌 Ngành: {analyzed.get('industry')}")
                        print(f"   📌 Tiếng Nhật: {analyzed.get('japanese_level')}")
                        print("-" * 50)

                        if len(posts_data) >= max_posts:
                            break
            except Exception as e:
                print(f"⚠️ Lỗi xử lý bài: {e}")
                continue

        # Kiểm tra còn bài mới không
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("📭 Không còn bài mới.")
            break
        last_height = new_height

    driver.quit()
    print(f"\n🎉 Hoàn thành! Đã crawl và phân tích {len(posts_data)} bài.")
    return posts_data


def crawl_and_analyze_save(url, max_posts=15, output_file="posts_analyzed.json"):
    """Crawl, phân tích và lưu vào JSON + SQLite"""
    
    # 1. Crawl và phân tích
    posts = crawl_and_analyze(url, max_posts)
    
    # 2. Lưu JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Đã lưu JSON vào file: {output_file}")
    
    # 3. Lưu SQLite
    if posts:
        init_db()
        for post in posts:
            save_job(post)
        print(f"💾 Đã lưu {len(posts)} bài vào database (jobs.db)")
    else:
        print("⚠️ Không có bài viết nào để lưu vào database")
    
    return posts


def delete_cookies():
    """Xóa cookies (khi muốn đăng nhập lại)"""
    from src.cookie_manager import delete_cookies as del_cookies
    del_cookies()