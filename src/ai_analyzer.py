import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.xah.io/v1"
)

MODEL = "gpt-5.6-sol"


def split_jobs(content: str) -> list:
    """TẦNG 1: Tách bài viết thành nhiều job riêng biệt."""
    prompt = f"""
Bài viết sau có thể chứa NHIỀU tin tuyển dụng khác nhau.
Hãy tách thành các job riêng biệt.

Bài viết:
{content}

YÊU CẦU:
- Nếu bài chỉ có 1 job → trả về array 1 phần tử
- Nếu có nhiều job → tách thành nhiều phần tử
- Giữ nguyên nội dung gốc

Ví dụ output:
["Tuyển kỹ sư cơ khí đi Osaka", "Tuyển thực tập sinh điện tử đi Tokyo"]

CHỈ TRẢ VỀ JSON ARRAY, KHÔNG GIẢI THÍCH.
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        result = response.choices[0].message.content.strip()

        if result.startswith("```json"):
            result = result[7:-3]
        elif result.startswith("```"):
            result = result[3:-3]

        jobs = json.loads(result)
        return jobs if isinstance(jobs, list) else [content]

    except Exception as e:
        print(f"❌ Lỗi tách job: {e}")
        return [content]


def analyze_single_job(job: str) -> dict:
    """TẦNG 2: Phân tích chi tiết 1 job."""
    prompt = f"""
Phân tích tin tuyển dụng sau và trích xuất thông tin:

{job}

Trả về JSON với schema:
{{
  "visa_type": "loại visa",
  "industry": "ngành nghề",
  "japanese_level": "trình độ tiếng Nhật",
  "gender": "giới tính",
  "location": "địa điểm làm việc",
  "salary": "mức lương",
  "requirements": "yêu cầu khác",
  "benefits": "chế độ đãi ngộ",
  "summary": "tóm tắt ngắn gọn"
}}

Nếu không có thông tin thì để chuỗi rỗng.
Chỉ trả về JSON.
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        result = response.choices[0].message.content.strip()

        if result.startswith("```json"):
            result = result[7:-3]
        elif result.startswith("```"):
            result = result[3:-3]

        return json.loads(result)

    except Exception as e:
        print(f"❌ Lỗi phân tích job: {e}")
        return {
            "visa_type": "", "industry": "", "japanese_level": "",
            "gender": "", "location": "", "salary": "",
            "requirements": "", "benefits": "", "summary": ""
        }


def analyze_post_full(content: str) -> list:
    """Phân tích 2 tầng: tách job + phân tích từng job."""
    print("   📦 Tầng 1: Đang tách job...")
    jobs = split_jobs(content)
    print(f"   ✅ Tách được {len(jobs)} job")

    results = []
    for i, job in enumerate(jobs, 1):
        print(f"   🔍 Tầng 2: Phân tích job {i}/{len(jobs)}...")
        analyzed = analyze_single_job(job)
        results.append({
            "job_content": job,
            "analyzed": analyzed
        })

    return results