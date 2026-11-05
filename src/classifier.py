def classify_post(content: str) -> str:
    content_lower = content.lower()

    # ===== 1. BỘ LỌC QUẢNG CÁO / DỊCH VỤ (Ưu tiên loại bỏ trước) =====
    exclude_keywords = [
        'seeding', 'sensei', 'ss này', 'giới thiệu', 'reply', 
        'share', 'follow', 'inbox', 'bên mình', 'bên em', 
        'nhận hồ sơ', 'uy tín', 'chất lượng', 'cam kết',
        'hỗ trợ chuyển việc', 'chuyển việc', 'dịch vụ', 'tư vấn miễn phí'
    ]
    for kw in exclude_keywords:
        if kw in content_lower:
            return "TIN RÁC"

    # ===== 2. TỪ KHÓA ỨNG VIÊN (Bổ sung thêm viết tắt) =====
    job_keywords = [
        'tìm đơn', 'xin đơn', 'tìm gấp đơn', 'tìm job', 'tìm việc',
        'ai có đơn', 'cần tìm', 'có đơn nào', 'kiếm đơn', 'muốn tìm đơn',
        'muốn đi', 'cần đi', 'ứng tuyển', 'em cần', 'mình cần', 
        'đang tìm', 'cần xin', 'tìm việc làm', 'muốn xin việc', 
        'đang cần việc', 'tìm vc', 'xin vc', 'cần vc', 'cần job', 
        'ai có việc', 'tìm đơn tkt', 'tìm đơn tokutei', 'cần tìm đơn',
        'quay lại', 'về nước', 'đầu việt', 'đầu nhật'
    ]

    for kw in job_keywords:
        if kw in content_lower:
            # Nếu có từ khóa ứng viên, kiểm tra xem có phải là bài tuyển dụng không
            if 'tuyển' in content_lower or 'công ty' in content_lower:
                continue # Nếu vừa có từ tuyển dụng thì bỏ qua, không tính là ứng viên
            return "ỨNG VIÊN"

    # ===== 3. TỪ KHÓA VIỆC LÀM (Nhà tuyển dụng) =====
    recruitment_keywords = [
        'tuyển', 'cần tuyển', 'tuyển gấp', 'tuyển dụng',
        'visa', 'tokutei', 'thực tập sinh', 'kỹ sư',
        'lương', 'về tay', 'đơn hàng', 'hợp đồng',
        'công ty', 'phỏng vấn', 'xuất cảnh', 'lg', 'tts', 'cty', 'pv', 'xkld'
    ]

    for kw in recruitment_keywords:
        if kw in content_lower:
            return "VIỆC LÀM NHẬT"

    return "TIN RÁC"