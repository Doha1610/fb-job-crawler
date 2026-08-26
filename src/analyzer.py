import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_job_post(content: str) -> dict:
    """
    Phân tích bài đăng tuyển dụng bằng OpenAI.
    Trả về dict với các trường đã chuẩn hóa.
    """
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
        response = client.chat.completions.create(
            model="gpt-5.6-sol",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        result_text = response.choices[0].message.content.strip()

        # Xóa code block nếu có
        if result_text.startswith("```json"):
            result_text = result_text[7:-3]
        elif result_text.startswith("```"):
            result_text = result_text[3:-3]

        return json.loads(result_text)

    except Exception as e:
        print(f"Lỗi phân tích: {e}")
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