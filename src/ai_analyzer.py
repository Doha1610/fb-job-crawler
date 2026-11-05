
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from src.job_schema import META_JOB_SCHEMA

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.xah.io/v1"
)

MODEL = "gpt-5.5"


def analyze_job_information(group_name: str, raw_text: str) -> dict:
    """
    Phân tích thông tin tìm việc của chính người đăng.
    Không phân tích bình luận và không tạo hồ sơ cho người khác.
    """

    if not raw_text or not raw_text.strip():
        return {}

    system_prompt = """
Bạn là hệ thống trích xuất dữ liệu ứng viên tìm việc tại Nhật Bản.

NHIỆM VỤ:
Phân tích bài đăng của MỘT người đăng và trích xuất thông tin
phục vụ CRM quản lý người lao động đang tìm việc.

QUY TẮC BẮT BUỘC:

1. Chỉ phân tích thông tin của chính người đăng.
2. Không phân tích bình luận.
3. Không tạo hồ sơ cho người được nhắc đến trong bài.
4. Không coi tin tuyển dụng của công ty là thông tin ứng viên.
5. Không suy luận thông tin không được đề cập.
6. Không tự thêm tuổi, giới tính, visa, kinh nghiệm,
   chứng chỉ, trình độ tiếng Nhật hoặc địa điểm.
7. Phân biệt:
   - "Em cần tìm đơn": người tìm việc.
   - "Em có đơn tuyển": người tuyển dụng hoặc môi giới.
8. Phân biệt:
   - "Em muốn tìm đơn thực phẩm": ngành nghề mong muốn.
   - "Bên công ty tuyển thực phẩm": thông tin tuyển dụng,
     không phải ngành nghề mong muốn của người đăng.
9. Nếu không có dữ liệu, trả về "Không cung cấp".
10. makeAI chỉ được tóm tắt thông tin thực sự xuất hiện
    trong bài gốc.

Tên nhóm chỉ là thông tin tham khảo.
Không sử dụng tên nhóm để tự suy luận visa hoặc ngành nghề.
"""

    user_prompt = f"""
Tên nhóm tham khảo:
{group_name}

Nội dung bài đăng gốc của người đăng:
{raw_text}

Hãy trích xuất thông tin của chính người đăng.
Không thêm thông tin không có trong nội dung.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": META_JOB_SCHEMA
            },
            temperature=0
        )

        result_text = response.choices[0].message.content

        if not result_text:
            return {}

        result = json.loads(result_text)

        if not isinstance(result, dict):
            return {}

        return result

    except Exception as e:
        print(f"❌ Lỗi phân tích ứng viên: {e}")
        return {}


def analyze_post_full(content: str, group_name: str = "") -> list:
    """
    Giữ lại giao diện hàm cũ để crawl_3day.py không phải
    thay đổi cách gọi.

    Mỗi bài đăng chỉ tạo một hồ sơ của người đăng.
    Không tách thành nhiều người.
    """

    print("   🧠 Đang phân tích bài đăng của người đăng...")

    analyzed = analyze_job_information(group_name, content)

    if not analyzed:
        print("   ⚠️ AI không phân tích được nội dung.")
        return []

    return [
        {
            "job_content": content,
            "analyzed": analyzed
        }
    ]
