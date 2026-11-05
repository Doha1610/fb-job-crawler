def format_job(data: dict) -> list:
    """
    Chuẩn hóa dữ liệu AI thành mảng theo thứ tự cố định.
    Dùng để ghi vào Google Sheets theo cột.
    """
    fields = [
        "visa_mong_muon",
        "nganh_nghe",
        "trinh_do_tieng_nhat",
        "gioi_tinh",
        "dia_diem",
        "luong_mong_muon",
        "yeu_cau_khac",
        "dai_ngo",
        "so_dien_thoai",
        "zalo",
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
    Khớp chính xác với 17 cột.
    """
    analyzed = post.get("analyzed", {})

    # Thứ tự cột trong Sheet:
    # A: Ngày | B: Nhóm | C: Nội dung | D: Người gửi | E: URL bài
    # F: Nhãn | G: Visa | H: Ngành | I: Tiếng Nhật | J: Giới tính
    # K: Địa điểm | L: Lương | M: Yêu cầu | N: Đãi ngộ | O: SĐT | P: Zalo | Q: Tóm tắt
    row = [
        "",  # A: Ngày (để trống, Sheet tự điền)
        post.get("ten_nhom", ""),                 # B: Nhóm
        post.get("raw_content", ""),               # C: Nội dung
        post.get("nguoi_gui", ""),                 # D: Người gửi
        post.get("url_bai_viet", ""),              # E: URL bài
        post.get("label", ""),                     # F: Nhãn
        analyzed.get("visa_mong_muon", ""),        # G: Visa
        analyzed.get("nganh_nghe", ""),            # H: Ngành
        analyzed.get("trinh_do_tieng_nhat", ""),   # I: Tiếng Nhật
        analyzed.get("gioi_tinh", ""),             # J: Giới tính
        analyzed.get("dia_diem", ""),              # K: Địa điểm
        analyzed.get("luong_mong_muon", ""),       # L: Lương
        analyzed.get("yeu_cau_khac", ""),          # M: Yêu cầu
        analyzed.get("dai_ngo", ""),               # N: Đãi ngộ
        analyzed.get("so_dien_thoai", ""),         # O: SĐT (MỚI)
        analyzed.get("zalo", ""),                  # P: Zalo (MỚI)
        analyzed.get("summary", ""),               # Q: Tóm tắt
    ]

    return row