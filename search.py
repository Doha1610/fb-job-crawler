from src.database import search_jobs, init_db

# Khởi tạo database
init_db()

# Tìm kiếm
results = search_jobs(visa="kỹ sư", location="Osaka")

print(f"\n🔍 Tìm thấy {len(results)} bài viết:\n")
for row in results:
    print(f"ID: {row[0]}")
    print(f"Visa: {row[2]}")
    print(f"Ngành: {row[3]}")
    print(f"Địa điểm: {row[5]}")
    print("-" * 40)