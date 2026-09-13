from src.ai_analyzer import analyze_post_full
import json

# Bài viết có NHIỀU job
sample = """
TUYỂN GẤP 2 VỊ TRÍ:

1. Kỹ sư cơ khí đi Osaka
- Visa kỹ sư
- Tiếng Nhật N3
- Lương 25-30 triệu

2. Thực tập sinh điện tử đi Tokyo
- Visa thực tập sinh
- Tiếng Nhật N4
- Lương 20 triệu
"""

print("="*60)
print("🧪 TEST AI 2 TẦNG")
print("="*60)

results = analyze_post_full(sample)

print(f"\n📊 Kết quả: Tách được {len(results)} job\n")

for i, r in enumerate(results, 1):
    print(f"--- Job {i} ---")
    print(f"Nội dung: {r['job_content'][:100]}...")
    print(f"\nPhân tích:")
    for k, v in r['analyzed'].items():
        if v:
            print(f"   {k}: {v}")
    print("-" * 60)