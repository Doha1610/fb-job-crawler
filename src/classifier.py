
import re


def normalize_text(content: str) -> str:
    """Chuẩn hóa khoảng trắng và chữ thường, không làm mất dấu tiếng Việt."""
    if not content:
        return ""
    return re.sub(r"\s+", " ", content.lower()).strip()


def contains_any(text: str, keywords: list) -> bool:
    return any(keyword in text for keyword in keywords)


def classify_post(content: str) -> str:
    """
    Chỉ phân loại ý định của NGƯỜI ĐĂNG BÀI.

    Kết quả:
    - ỨNG VIÊN: Có dấu hiệu rõ ràng người đăng đang tìm việc.
    - NHÀ TUYỂN DỤNG: Có dấu hiệu rõ ràng người đăng đang tuyển người.
    - CHƯA XÁC ĐỊNH: Chưa đủ bằng chứng.
    """

    text = normalize_text(content)

    if not text:
        return "CHƯA XÁC ĐỊNH"

    # Dấu hiệu rõ ràng người đăng đang tìm việc.
    candidate_keywords = [
        "em cần tìm đơn",
        "mình cần tìm đơn",
        "tôi cần tìm đơn",
        "em muốn tìm đơn",
        "mình muốn tìm đơn",
        "tôi muốn tìm đơn",
        "em cần tìm việc",
        "mình cần tìm việc",
        "tôi cần tìm việc",
        "em muốn tìm việc",
        "mình muốn tìm việc",
        "tôi muốn tìm việc",
        "em đang tìm việc",
        "mình đang tìm việc",
        "tôi đang tìm việc",
        "em tìm đơn",
        "mình tìm đơn",
        "tôi tìm đơn",
        "em xin đơn",
        "mình xin đơn",
        "tôi xin đơn",
        "ai có đơn",
        "ai có việc",
        "muốn tìm đơn",
        "cần tìm đơn",
        "đang tìm đơn",
        "tìm đơn tokutei",
        "tìm đơn tkt",
        "tìm đơn quay lại",
        "muốn quay lại nhật",
        "em muốn quay lại nhật",
        "mình muốn quay lại nhật",
        "cần quay lại nhật",
        "muốn chuyển việc",
        "em muốn chuyển việc",
        "mình muốn chuyển việc",
        "cần chuyển việc",
        "mong muốn tìm việc",
        "muốn tìm việc làm",
        "cần tìm việc làm",
        "em cần việc",
        "mình cần việc",
        "tôi cần việc",
        "tìm vc",
        "xin vc",
        "cần vc",
        "cần job",
    ]

    # Dấu hiệu rõ ràng người đăng đang tuyển người hoặc môi giới.
    recruiter_keywords = [
        "cần tuyển",
        "tuyển gấp",
        "đang tuyển",
        "tuyển dụng",
        "bên mình tuyển",
        "bên em tuyển",
        "công ty tuyển",
        "nhận hồ sơ",
        "nhận cv",
        "nhận đăng ký",
        "có form phỏng vấn",
        "form phỏng vấn",
        "đơn hàng cần tuyển",
        "tuyển lao động",
        "tuyển nam",
        "tuyển nữ",
        "tuyển cả nam và nữ",
        "cần nam nữ",
        "cần nam",
        "cần nữ",
        "bên mình có đơn",
        "bên em có đơn",
        "mình có đơn tuyển",
        "em có đơn tuyển",
        "hiện có đơn tuyển",
        "đang có đơn tuyển",
    ]

    is_candidate = contains_any(text, candidate_keywords)
    is_recruiter = contains_any(text, recruiter_keywords)

    # Có cả hai loại tín hiệu thì không tự phán đoán.
    if is_candidate and is_recruiter:
        return "CHƯA XÁC ĐỊNH"

    if is_candidate:
        return "ỨNG VIÊN"

    if is_recruiter:
        return "NHÀ TUYỂN DỤNG"

    # Các từ khóa này chỉ nói về chủ đề Nhật Bản,
    # không chứng minh người đăng đang tìm việc.
    general_keywords = [
        "tokutei",
        "thực tập sinh",
        "tts",
        "kỹ sư",
        "visa",
        "đầu việt",
        "đầu nhật",
        "quay lại",
        "lương",
        "đơn hàng",
        "phỏng vấn",
        "xuất cảnh",
        "nông nghiệp",
        "thực phẩm",
        "xây dựng",
    ]

    if contains_any(text, general_keywords):
        return "CHƯA XÁC ĐỊNH"

    return "CHƯA XÁC ĐỊNH"
