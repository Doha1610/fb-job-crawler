from src.google_sheets import push_posts_to_sheet

test_posts = [
    {
        "ten_nhom": "Test Group",
        "raw_content": "Tuyển kỹ sư cơ khí",
        "nguoi_gui": "Nguyễn Văn A",
        "url_bai_viet": "https://facebook.com/posts/123",
        "label": "VIỆC LÀM NHẬT",
        "analyzed": {
            "visa_type": "kỹ sư",
            "industry": "cơ khí",
            "japanese_level": "N3",
            "gender": "nam",
            "location": "Osaka",
            "salary": "25-30 triệu",
            "requirements": "Có kinh nghiệm",
            "benefits": "Hỗ trợ vé",
            "summary": "Tuyển kỹ sư cơ khí"
        }
    }
]

print("🧪 TEST GHI SHEET")
result = push_posts_to_sheet(test_posts)

if result:
    print("✅ THÀNH CÔNG! Kiểm tra Sheet ngay.")
else:
    print("❌ THẤT BẠI! Xem lỗi ở trên.")