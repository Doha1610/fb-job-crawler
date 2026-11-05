
import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.xah.io/v1"
)

MODEL_NAME = "gpt-5.5"

VALID_LABELS = [
    "ỨNG VIÊN",
    "NHÀ TUYỂN DỤNG",
    "CHƯA XÁC ĐỊNH"
]

# Các bài đăng mẫu để kiểm tra AI
# Cấu trúc: (nhãn mong đợi, nội dung bài đăng)

TEST_CASES = [
    # A. Ứng viên viết tắt, sai chính tả
    ("ỨNG VIÊN", "E cần tìm đơn tokutei senmon ngành lái máy ạ"),
    ("ỨNG VIÊN", "E cần tìm đơn nntt quay lại tokute ah"),
    ("ỨNG VIÊN", "Mình mún tìm đơn đi nhật lại ạ"),
    ("ỨNG VIÊN", "E muốn quay lại nhạt diện tokutei"),
    ("ỨNG VIÊN", "Cần tìm đơn cho nam còn 2 năm gino"),
    ("ỨNG VIÊN", "E nữ 22t tìm đơn thực phẩm quay lại nhật"),
    ("ỨNG VIÊN", "Mình cần tìm cv bên nhật, có N4"),
    ("ỨNG VIÊN", "E tìm đơn đầu nhật ngành ks, có N3"),
    ("ỨNG VIÊN", "Mn có đơn nào phù hợp giới thiệu e với ạ"),
    ("ỨNG VIÊN", "E muốn chuyển việc tokutei ngành xây dựng"),
    ("ỨNG VIÊN", "Mình đang ở Nhật muốn đổi cty"),
    ("ỨNG VIÊN", "E cần đơn quay lại Nhật, đã có 3 năm TTS"),
    ("ỨNG VIÊN", "Tìm đơn nông nghiệp đầu Việt cho nữ ạ"),
    ("ỨNG VIÊN", "E muốn đi Nhật lần 2, ai có đơn ib e"),
    ("ỨNG VIÊN", "Cần tìm việc tại Nhật, ngành nào cũng đc"),

    # B. Nhà tuyển dụng viết tắt
    ("NHÀ TUYỂN DỤNG", "Bên mình có đơn tokutei thực phẩm đầu Nhật"),
    ("NHÀ TUYỂN DỤNG", "Tuyển 5 nữ chế biến thực phẩm tại Osaka"),
    ("NHÀ TUYỂN DỤNG", "Nhận hs đi Nhật ngành xây dựng, ib mình"),
    ("NHÀ TUYỂN DỤNG", "Có đơn kỹ sư cơ khí lương 25man"),
    ("NHÀ TUYỂN DỤNG", "Cty cần tuyển nam làm hàn xì tại Nhật"),
    ("NHÀ TUYỂN DỤNG", "Đầu Nhật cần 3 bạn tokutei kaigo"),
    ("NHÀ TUYỂN DỤNG", "Mình nhận hồ sơ chuyển việc tokutei"),
    ("NHÀ TUYỂN DỤNG", "Tuyển gấp 2 nam đi đơn nông nghiệp"),
    ("NHÀ TUYỂN DỤNG", "Có form pv đơn thực phẩm, cần ứng viên nữ"),
    ("NHÀ TUYỂN DỤNG", "Nhận 2 đầu Nhật Việt, có đơn liên tục"),

    # C. Câu ngắn, thiếu chủ ngữ
    ("ỨNG VIÊN", "Tokutei thực phẩm, muốn quay lại"),
    ("ỨNG VIÊN", "Có N4, muốn tìm việc tại Nhật"),
    ("NHÀ TUYỂN DỤNG", "Đơn tokutei ngành lái máy, ai cần ib"),
    ("ỨNG VIÊN", "Tìm đơn đầu Nhật, ngành khách sạn"),
    ("NHÀ TUYỂN DỤNG", "Tuyển đơn đầu Việt, phỏng vấn online"),
    ("CHƯA XÁC ĐỊNH", "Nữ 23 tuổi, có kinh nghiệm thực phẩm"),
    ("CHƯA XÁC ĐỊNH", "Nhật Bản, tokutei, N4, Osaka"),
    ("ỨNG VIÊN", "Ai có đơn quay lại Nhật không ạ?"),
    ("NHÀ TUYỂN DỤNG", "Cần người đi đơn xây dựng tháng này"),
    ("CHƯA XÁC ĐỊNH", "Có đơn nào tốt không mọi người?"),

    # D. Không dấu, tiếng Nhật
    ("ỨNG VIÊN", "E can tim don tokutei thuc pham a"),
    ("ỨNG VIÊN", "Minh muon quay lai Nhat lam viec"),
    ("NHÀ TUYỂN DỤNG", "Tuyen nam lam han xi tai Kanagawa"),
    ("NHÀ TUYỂN DỤNG", "Nhan ho so tokutei dau Nhat"),
    ("ỨNG VIÊN", "E muon doi cty dang lam o Nhat"),
    ("ỨNG VIÊN", "仕事を探しています。食品関係希望です。"),
    ("NHÀ TUYỂN DỤNG", "特定技能の人材を募集しています"),
    ("ỨNG VIÊN", "日本で働きたいです。仕事を探しています。"),
    ("NHÀ TUYỂN DỤNG", "Tuyển 3 bạn làm thực phẩm, pv tháng 12"),
    ("ỨNG VIÊN", "E tìm đơn tokutei, bên nào nhận hồ sơ ib e"),

    # E. Mâu thuẫn, dễ nhầm
    ("ỨNG VIÊN", "Mình cần tìm đơn tokutei, ai có đơn giới thiệu mình"),
    ("NHÀ TUYỂN DỤNG", "Bên mình có đơn thực phẩm, ai cần tìm việc liên hệ"),
    ("CHƯA XÁC ĐỊNH", "Mình vừa tìm việc vừa muốn giới thiệu đơn cho bạn bè"),
    ("CHƯA XÁC ĐỊNH", "Có bạn nào cần đơn tokutei không, mình cũng đang tìm đơn"),
    ("CHƯA XÁC ĐỊNH", "Mình có N4, 3 năm kinh nghiệm, đang tìm hiểu các đơn Nhật"),
]


def classify_post(content):
    """Gửi bài đăng đến AI để phân loại."""

    prompt = f"""
Bạn là hệ thống phân loại bài đăng Facebook phục vụ CRM
ứng viên tìm việc Nhật Bản.

Chỉ phân loại dựa trên ý định của người viết.

CÓ 3 NHÃN:

1. ỨNG VIÊN:
Người viết đang tìm việc, tìm đơn, muốn quay lại Nhật,
muốn chuyển việc hoặc tìm cơ hội việc làm cho chính mình.

2. NHÀ TUYỂN DỤNG:
Người viết đang tuyển người, giới thiệu đơn tuyển dụng,
nhận hồ sơ hoặc tìm ứng viên cho doanh nghiệp.

3. CHƯA XÁC ĐỊNH:
Không đủ thông tin hoặc ý định không rõ ràng.

QUY TẮC:
- "Em cần tìm đơn", "muốn tìm việc", "muốn quay lại Nhật"
  là dấu hiệu ứng viên.
- "Tuyển", "nhận hồ sơ", "bên mình có đơn",
  "cần tìm ứng viên" là dấu hiệu nhà tuyển dụng.
- Không phân loại chỉ dựa vào Tokutei, N4, Nhật Bản,
  nam, nữ, ngành nghề hoặc mức lương.
- Nếu có cả ý định tìm việc và tuyển người cho chính mình,
  chọn CHƯA XÁC ĐỊNH.
- Không tự suy diễn thông tin không có trong bài đăng.
- Chấp nhận lỗi chính tả, viết tắt, không dấu và tiếng Nhật.
- Phân biệt người đang tìm đơn với người đang giới thiệu đơn.

BÀI ĐĂNG:
{content}

Chỉ trả về JSON:
{{
    "label": "ỨNG VIÊN hoặc NHÀ TUYỂN DỤNG hoặc CHƯA XÁC ĐỊNH",
    "reason": "Giải thích ngắn gọn"
}}
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "Chỉ trả về JSON hợp lệ, không thêm Markdown."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    result = response.choices[0].message.content

    if not result:
        raise ValueError("AI không trả về nội dung")

    result = result.strip()

    # Bỏ Markdown code fence nếu có
    result = re.sub(r"^```(?:json)?\s*", "", result)
    result = re.sub(r"\s*```$", "", result)

    # Parse JSON
    data = json.loads(result)

    label = data.get("label", "").strip().upper()

    if label not in VALID_LABELS:
        raise ValueError(f"Nhãn không hợp lệ: {label}")

    return {
        "label": label,
        "reason": data.get("reason", "")
    }


def main():
    correct = 0
    total = len(TEST_CASES)
    errors = 0

    print("=" * 75)
    print("BẮT ĐẦU KIỂM TRA AI CLASSIFIER")
    print("Model:", MODEL_NAME)
    print("Tổng số bài test:", total)
    print("=" * 75)

    for index, (expected, content) in enumerate(TEST_CASES, start=1):

        print(f"\n[{index}/{total}]")
        print("Bài đăng:", content)

        try:
            result = classify_post(content)

            actual = result["label"]
            is_correct = actual == expected

            if is_correct:
                correct += 1

            print("Nhãn mong đợi:", expected)
            print("Nhãn AI:", actual)
            print("Lý do:", result["reason"])
            print("Kết quả:", "ĐÚNG" if is_correct else "SAI")

        except Exception as e:
            errors += 1
            print("Lỗi:", str(e))

    # Tổng kết
    print("\n" + "=" * 75)
    print("TỔNG KẾT KIỂM TRA")
    print("=" * 75)

    print(f"Tổng số bài test: {total}")
    print(f"Phân loại đúng: {correct}")
    print(f"Phân loại sai: {total - correct - errors}")
    print(f"Lỗi API/JSON: {errors}")

    accuracy = correct / total * 100 if total else 0

    print(f"TỶ LỆ ĐÚNG: {accuracy:.2f}%")
    print("=" * 75)


if __name__ == "__main__":
    main()
