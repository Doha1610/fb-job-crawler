from src.multi_crawler import crawl_multiple_and_save

# ===== CẤU HÌNH =====
MAX_POSTS_PER_GROUP = 5      # Số bài tối đa mỗi group
DELAY_BETWEEN_GROUPS = 15    # Nghỉ 15s giữa các group
OUTPUT_FILE = "ket_qua_nhieu_group.json"
# ====================

posts = crawl_multiple_and_save(
    max_posts_per_group=MAX_POSTS_PER_GROUP,
    delay=DELAY_BETWEEN_GROUPS,
    output_file=OUTPUT_FILE
)

# In kết quả
print("\n========== 📊 KẾT QUẢ ==========\n")
for i, post in enumerate(posts, 1):
    print(f"--- Bài {i} ---")
    print(f"Nhãn: {post.get('label', '')}")
    print(f"Nhóm: {post.get('ten_nhom', '')[:50]}...")
    print(f"Nội dung: {post.get('raw_content', '')[:100]}...")

    analyzed = post.get('analyzed', {})
    print(f"📋 Phân tích:")
    for key, value in analyzed.items():
        if value:
            print(f"   {key}: {value}")
    print()