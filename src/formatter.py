def format_job(data: dict) -> list:
    """
    Chuẩn hóa dữ liệu AI thành mảng theo thứ tự cố định.
    Dùng để ghi vào Google Sheets theo cột.
    """
    fields = [
        "visa_type",
        "industry",
        "japanese_level",
        "gender",
        "location",
        "salary",
        "requirements",
        "benefits",
        "summary",
    ]

    result = []
    for field in fields:
        value = data.get(field, "")

        # Lọc giá trị rỗng
        if value in [None, "", "Không cung cấp", "không có", "N/A"]:
            value = ""

        # Nếu là list → chuyển thành string
        if isinstance(value, list):
            value = "; ".join(str(v) for v in value if v)

        result.append(str(value))

    return result


def format_post_full(post: dict) -> list:
    """
    Format toàn bộ bài viết để ghi vào Sheet.
    Bao gồm metadata + dữ liệu phân tích.
    """
    analyzed = post.get("analyzed", {})

    # Thứ tự cột trong Sheet:
    # A: Ngày | B: Nhóm | C: Nội dung | D: Người gửi
    # E: URL bài | F: Nhãn | G: Visa | H: Ngành
    # I: Tiếng Nhật | J: Giới tính | K: Địa điểm
    # L: Lương | M: Yêu cầu | N: Đãi ngộ | O: Tóm tắt
    row = [
        "",  # A: Ngày (để trống, Sheet tự điền)
        post.get("ten_nhom", ""),           # B
        post.get("raw_content", ""),         # C
        post.get("nguoi_gui", ""),           # D
        post.get("url_bai_viet", ""),        # E
        post.get("label", ""),               # F
        analyzed.get("visa_type", ""),       # G
        analyzed.get("industry", ""),        # H
        analyzed.get("japanese_level", ""),  # I
        analyzed.get("gender", ""),          # J
        analyzed.get("location", ""),        # K
        analyzed.get("salary", ""),          # L
        analyzed.get("requirements", ""),    # M
        analyzed.get("benefits", ""),        # N
        analyzed.get("summary", ""),         # O
    ]

    return row