from src.crawl import analyze_job_post
import json


sample_post = """
CÔNG TY TNHH XYZ TUYỂN KỸ SƯ CƠ KHÍ ĐI NHẬT

Vị trí: Kỹ sư cơ khí
Số lượng: 5 người
Địa điểm làm việc: Osaka, Nhật Bản

Yêu cầu:
- Tốt nghiệp đại học chuyên ngành Cơ khí/Cơ điện tử
- Tiếng Nhật N3 trở lên (có chứng chỉ)
- Nam, dưới 30 tuổi
- Có kinh nghiệm ít nhất 1 năm

Quyền lợi:
- Lương: 25-30 triệu/tháng (tùy kinh nghiệm)
- Hỗ trợ vé máy bay và chi phí làm thủ tục
- Có người hỗ trợ tại Nhật
- Visa kỹ sư (Engineer)

Liên hệ: 0988.xxx.xxx (Ms. Hoa)
"""


print("=" * 60)
print("🧪 TEST PHÂN TÍCH AI")
print("=" * 60)

print("\n📝 Nội dung bài đăng:")
print("-" * 60)
print(sample_post[:200] + "...")
print("-" * 60)

print("\n🤖 Đang gửi lên AI...")
print("⏳ Chờ trong giây lát...\n")


result = analyze_job_post(sample_post)


print("=" * 60)
print("📊 KẾT QUẢ PHÂN TÍCH")
print("=" * 60)


for key, value in result.items():

    if value is not None and value != "":
        print(f"{key:20}: {value}")
    else:
        print(f"{key:20}: (Không có thông tin)")


print("\n" + "=" * 60)
print("✅ Test hoàn tất!")


with open(
    "test_ai_result.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        result,
        f,
        ensure_ascii=False,
        indent=2
    )


print("💾 Đã lưu kết quả vào file: test_ai_result.json")