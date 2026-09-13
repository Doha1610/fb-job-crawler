def classify_post(content: str) -> str:
    """
    Phân loại bài viết:
    - ỨNG VIÊN: Người tìm việc
    - VIỆC LÀM NHẬT: Người tuyển dụng
    - TIN RÁC: Không liên quan
    """
    content_lower = content.lower()

    # ===== TỪ KHÓA ỨNG VIÊN =====
    job_keywords = [
        'tìm đơn', 'xin đơn', 'tìm gấp đơn', 'tìm job',
        'ai có đơn', 'cần tìm', 'có đơn nào nhận', 'kiếm đơn',
        'muốn đi', 'cần đi', 'tìm việc', 'ứng tuyển'
    ]

    # ===== TỪ KHÓA VIỆC LÀM =====
    recruitment_keywords = [
        'tuyển', 'cần tuyển', 'tuyển gấp', 'tuyển dụng',
        'visa', 'tokutei', 'thực tập sinh', 'kỹ sư',
        'lương', 'về tay', 'đơn hàng', 'hợp đồng'
    ]

    job_count = sum(1 for kw in job_keywords if kw in content_lower)
    recruitment_count = sum(1 for kw in recruitment_keywords if kw in content_lower)

    if job_count > recruitment_count:
        return "ỨNG VIÊN"
    elif recruitment_count > 0:
        return "VIỆC LÀM NHẬT"
    else:
        return "TIN RÁC"


def is_spam(content: str) -> bool:
    """Kiểm tra nhanh có phải tin rác không"""
    return classify_post(content) == "TIN RÁC"