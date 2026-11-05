
META_JOB_SCHEMA = {
    "name": "candidate_profile",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "postType": {
                "type": "string",
                "enum": ["ỨNG VIÊN"]
            },
            "visa": {
                "type": "string",
                "description": """
Chỉ xác định loại visa khi nội dung bài đăng có bằng chứng cụ thể.
Không mặc định đầu Nhật.
Không dùng tên nhóm làm bằng chứng duy nhất.
Nếu không đủ thông tin, trả về Không cung cấp.
""",
                "enum": [
                    "Thực tập sinh 3 năm",
                    "Thực tập sinh 1 năm",
                    "Thực tập sinh 3 go",
                    "Tokutei đầu Việt",
                    "Tokutei đầu Nhật",
                    "Kỹ sư đầu Nhật",
                    "Kỹ sư đầu Việt",
                    "Không cung cấp"
                ]
            },
            "job": {
                "type": "string",
                "description": """
Ngành nghề mà chính người đăng đang muốn tìm việc.
Chỉ lấy ngành nghề có trong nội dung.
Không suy luận ngành nghề từ tên nhóm.
Nếu không có thông tin, trả về Không cung cấp.
"""
            },
            "workLocation": {
                "type": "string",
                "description": """
Khu vực người đăng mong muốn làm việc.
Chỉ lấy địa điểm được người đăng đề cập là mong muốn.
Không lấy địa điểm của đơn tuyển dụng khác.
Nếu không có, trả về Không cung cấp.
"""
            },
            "languageLevel": {
                "type": "string",
                "description": """
Trình độ tiếng Nhật của chính người đăng.
Phân biệt JLPT và Kaiwa.
Không tự suy luận từ công việc hoặc tên nhóm.
Nếu không có thông tin, trả về Không cung cấp.
""",
                "enum": [
                    "Không yêu cầu tiếng",
                    "JLPT N5",
                    "JLPT N4",
                    "JLPT N3",
                    "JLPT N2",
                    "JLPT N1",
                    "Kaiwa N5",
                    "Kaiwa N4",
                    "Kaiwa N3",
                    "Kaiwa N2",
                    "Kaiwa N1",
                    "Không cung cấp"
                ]
            },
            "gender": {
                "type": "string",
                "description": """
Giới tính của chính người đăng đang tìm việc.
Chỉ xác định khi người đăng tự nói rõ giới tính.
Không lấy giới tính yêu cầu trong tin tuyển dụng.
Nếu không rõ, trả về Không cung cấp.
""",
                "enum": [
                    "Nam",
                    "Nữ",
                    "Không cung cấp"
                ]
            },
            "specialConditions": {
                "type": "array",
                "description": """
Các mong muốn hoặc điều kiện của chính người tìm việc.
Chỉ lấy thông tin được nói rõ trong bài.
Không lấy điều kiện tuyển dụng của công ty khác.
Không lặp giá trị.
""",
                "items": {
                    "type": "string",
                    "enum": [
                        "Bao đỗ",
                        "Tăng ca",
                        "Lương tốt",
                        "Vợ chồng",
                        "Hỗ trợ chỗ ở",
                        "Không yêu cầu kinh nghiệm",
                        "Thưởng"
                    ]
                }
            },
            "makeAI": {
                "type": "string",
                "description": """
Tóm tắt hồ sơ tìm việc của chính người đăng bằng tiếng Việt.
Chỉ sử dụng thông tin có trong bài viết gốc.
Không tự thêm tuổi, giới tính, visa, kinh nghiệm,
chứng chỉ, trình độ tiếng Nhật hoặc khu vực.
Không biến điều kiện tuyển dụng thành mong muốn của ứng viên.
Nếu bài ngắn, chỉ tóm tắt đúng thông tin ngắn đó.
"""
            }
        },
        "required": [
            "postType",
            "visa",
            "job",
            "workLocation",
            "languageLevel",
            "gender",
            "specialConditions",
            "makeAI"
        ],
        "additionalProperties": False
    }
}
