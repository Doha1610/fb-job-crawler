import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from src.job_schema import META_JOB_SCHEMA, CAREER_NOTE

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.xah.io/v1"
)

MODEL = "gpt-5.5"


def split_jobs(content: str) -> list:
    """TẦNG 1: Tách bài viết thành nhiều ứng viên riêng biệt."""
    prompt = f"""
Bài viết sau có thể chứa thông tin của NHIỀU ứng viên khác nhau.
Hãy tách thành các hồ sơ ứng viên riêng biệt.

Bài viết:
{content}

YÊU CẦU:
- Nếu bài chỉ có 1 ứng viên → trả về array 1 phần tử
- Nếu có nhiều ứng viên → tách thành nhiều phần tử
- Giữ nguyên nội dung gốc của từng người

Ví dụ output:
["Em Nam 25 tuổi, cần tìm việc Osaka, tiếng Nhật N3", "Em nữ 22 tuổi, tìm việc Tokyo, tokutei thực phẩm"]

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
        print(f"❌ Lỗi tách ứng viên: {e}")
        return [content]


# =========================================================
# BƯỚC 1: CHUẨN HÓA VĂN BẢN (Xóa teencode, sửa lỗi chính tả)
# =========================================================
def analyze_and_split_job_content(group_name: str, raw_text: str) -> str:
    """Làm sạch văn bản trước khi đưa cho AI phân tích."""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Bối cảnh: " + group_name + ".\n" +
                        "- Tuyệt đối giữ nguyên nội dung tin nhắn gốc, chỉ chuẩn hóa lại cách viết để dễ đọc và phân tích chính xác hơn.\n" +
                        "- Không được thêm bất kỳ từ, cụm từ, hay nội dung AI nào không có trong tin nhắn gốc. Nếu có từ tiếng nhật thì dịch chuẩn\n" +
                        "- Chỉ thực hiện chuẩn hóa các từ viết tắt, lỗi chính tả, ký tự đặc biệt, hoặc cách ngắt chữ không tự nhiên.\n" +
                        "- lưu ý các từ viết tắt tham khảo ở: " + CAREER_NOTE + "\n" +
                        "- ví dụ '$CBTP kanto ợ n.h.a.n n.a.m/n.u @ kai.wa.n2 / s A n..h.ậ..n  đ.unn.g n.gà..nh' → 'chế biến thực phẩm kanto, nhận nam nữ kaiwa n2, nhận đúng ngành'.\n" +
                        "- Kết quả trả về dưới dạng chuỗi văn bản rõ ràng, không chứa ký tự đặc biệt, lỗi định dạng hoặc JSON.\n" +
                        "- Đầu ra phải là nội dung thuần văn bản, dễ đọc, không chứa từ khóa 'json', dấu ngoặc kép, dấu ngoặc nhọn, hoặc bất kỳ ký tự đặc biệt nào khác.\n" +
                        "- Bắt buộc phải trả về giá trị, không để trống."
                    )
                },
                {
                    "role": "user",
                    "content": raw_text,
                }
            ],
            model=MODEL, # Đã đổi thành MODEL của bạn
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Lỗi chuẩn hóa văn bản: {e}")
        return raw_text # Nếu lỗi thì trả về nguyên bản để không bị mất dữ liệu


# =========================================================
# BƯỚC 2: TRÍCH XUẤT THÔNG TIN (Dùng Schema)
# =========================================================
def analyze_job_information(group_name: str, raw_text: str) -> dict:
    """Trích xuất thông tin từ văn bản đã được chuẩn hóa."""
    try:
        chat_completion = client.chat.completions.create(
            response_format={
                "type": "json_schema",
                "json_schema": META_JOB_SCHEMA
            },
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Dựa vào {group_name} để trả về loại visa chính xác hơn. Ví dụ tên nhóm 'TOKUTEI THỰC PHẨM - 食品加工特定技能' thì visa sẽ là Tokutei\n"
                        "Bạn là chuyên gia phân tích dữ liệu có 20 năm kinh nghiệm"
                        "Nhiệm vụ của bạn là phân tích nội dung đầu vào và xác định đúng loại visa bằng cách kiểm tra đầy đủ các tiêu chí:"
                        "\n Trước khi phân loại, bạn phải kiểm tra **tất cả từ khóa liên quan** trong nội dung."
                        "\n Nếu một nội dung chứa từ khóa liên quan đến **nhiều loại visa khác nhau**, hãy ưu tiên loại visa có **nhiều từ khóa phù hợp hơn**."
                        "\n Nếu một nội dung có tỉnh thành của Nhật Bản, điều đó không có nghĩa là nó là 'đầu Nhật' trừ khi có từ khóa liên quan đến loại visa."
                        "\n không tự động gán loại visa nếu không có thông tin cụ thể."
                        "\nTrả về kết quả JSON theo định dạng yêu cầu. Trả về đúng kết quả schema và không thêm bất kỳ thông tin dư thừa nào"
                    )
                },
                {
                    "role": "user",
                    "content": 'Phân tích nội dung: "'+raw_text+'"',
                }
            ],
            model=MODEL, # Đã đổi thành MODEL của bạn
        )
        
        # Parse JSON trả về
        return json.loads(chat_completion.choices[0].message.content)
        
    except Exception as e:
        print(f"❌ Lỗi trích xuất JSON (Có thể model không hỗ trợ Schema): {e}")
        return {}


# =========================================================
# HÀM TỔNG (Chạy 2 tầng + 2 bước)
# =========================================================
def analyze_post_full(content: str, group_name: str = "") -> list:
    """Phân tích 2 tầng: tách ứng viên + chuẩn hóa + trích xuất."""
    print("   📦 Tầng 1: Đang tách thông tin ứng viên...")
    jobs = split_jobs(content)
    print(f"   ✅ Tách được {len(jobs)} ứng viên")

    results = []
    for i, job in enumerate(jobs, 1):
        print(f"   🔍 Tầng 2 - Ứng viên {i}/{len(jobs)}:")
        
        # Bước 1: Chuẩn hóa văn bản (Xóa teencode)
        print("      🧹 Đang chuẩn hóa văn bản...")
        clean_text = analyze_and_split_job_content(group_name, job)
        
        # Bước 2: Trích xuất JSON
        print("      🧠 Đang trích xuất thông tin...")
        analyzed = analyze_job_information(group_name, clean_text)
        
        results.append({
            "job_content": clean_text, # Lưu nội dung đã được làm sạch
            "analyzed": analyzed
        })

    return results