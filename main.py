from src.crawl import crawl_and_analyze_save
import sys

# URL Facebook cần crawl
url = "https://www.facebook.com/profile.php?id=100054527256592"

# Chạy crawl và phân tích, tự động lưu vào file
posts = crawl_and_analyze_save(
    url=url,
    max_posts=5,
    output_file="ket_qua_phan_tich.json"
)

# In kết quả
print("\n========== 📊 KẾT QUẢ PHÂN TÍCH ==========\n")
for i, post in enumerate(posts, 1):
    print(f"--- Bài {i} ---")
    print(f"Nội dung: {post['raw_content'][:150]}...")
    print(f"\n📋 Thông tin:")
    for key, value in post['analyzed'].items():
        if value:
            print(f"   {key}: {value}")
    print("\n" + "=" * 60 + "\n")