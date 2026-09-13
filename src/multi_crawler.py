import os
import time
import json
from datetime import datetime
from src.crawl import crawl_and_analyze


GROUPS_FILE = "groups.txt"


def load_groups() -> list:
    """Đọc danh sách URL group từ file"""
    if not os.path.exists(GROUPS_FILE):
        print(f"⚠️ Không tìm thấy file: {GROUPS_FILE}")
        print(f"💡 Tạo file với mỗi dòng 1 URL group")
        return []

    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"📋 Đã load {len(urls)} group từ {GROUPS_FILE}")
    return urls


def crawl_multiple_groups(max_posts_per_group=5, delay=15):
    """
    Crawl nhiều group.
    
    Args:
        max_posts_per_group: Số bài tối đa mỗi group
        delay: Thời gian nghỉ giữa các group (giây)
    
    Returns:
        list tất cả bài từ tất cả group
    """
    groups = load_groups()

    if not groups:
        print("❌ Không có group nào để crawl!")
        return []

    all_posts = []
    start_time = datetime.now()

    print("\n" + "=" * 60)
    print(f"🚀 BẮT ĐẦU CRAWL {len(groups)} GROUP")
    print("=" * 60)

    for i, url in enumerate(groups, 1):
        print(f"\n{'─' * 60}")
        print(f"🌐 GROUP {i}/{len(groups)}: {url[:60]}...")
        print(f"{'─' * 60}")

        try:
            posts = crawl_and_analyze(url, max_posts=max_posts_per_group)
            all_posts.extend(posts)

            print(f"✅ Group {i}: {len(posts)} bài | Tổng: {len(all_posts)} bài")

            # Nghỉ giữa các group (trừ group cuối)
            if i < len(groups):
                print(f"⏸️ Nghỉ {delay}s trước group tiếp theo...")
                time.sleep(delay)

        except Exception as e:
            print(f"❌ Lỗi group {i}: {e}")
            continue

    # Tổng kết
    elapsed = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 60)
    print(f"🎉 HOÀN THÀNH!")
    print(f"   Tổng group: {len(groups)}")
    print(f"   Tổng bài: {len(all_posts)}")
    print(f"   Thời gian: {elapsed:.0f} giây")
    print("=" * 60)

    return all_posts


def crawl_multiple_and_save(
    max_posts_per_group=5,
    delay=15,
    output_file="ket_qua_nhieu_group.json"
):
    """
    Crawl nhiều group + lưu JSON + SQLite.
    """
    from src.database import init_db, save_job

    posts = crawl_multiple_groups(max_posts_per_group, delay)

    if not posts:
        print("⚠️ Không có bài nào để lưu")
        return []

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

    return posts