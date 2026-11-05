VISA_JOB_KEYWORDS = {
    "Thực tập sinh 3 năm": [
        'tr/f', 'triệu/form', 'tr/form', 'xăm', 'nhận xăm kín', 'nhận xăm', 'NHẬN XĂM HỞ', 'vgb', 'viêm gan B',
    ],
    "Thực tập sinh 1 năm": [
        "1 năm", "1n"
    ],
    "Thực tập sinh 3 go": [
        "may 3go", "may 3 go", "3 go"
    ],
    "Tokutei đầu Việt": [
        "đầu Việt", "đ.Việt", "đầu v", "quay lại", "đi mới", 'sang lại nhật'
    ],
    "Tokutei đầu Nhật": [
        "đầu Nhật", "đ.nhật", 'chuyển việc', 'sắp hết hạn', 'thực tập sinh sắp hết hạn'
    ],
    "Kỹ sư đầu Nhật": ["kĩ sư đầu Nhật", 'nvct', 'nhân viên chính thức'],
    "Kỹ sư đầu Việt": ["kĩ sư đầu Việt", "bằng", 'quay lại', 'q.lại', 'có vé', 'nvct', 'nhân viên chính thức']
}
CAREER_NOTE = """Nông nghiệp'; 'Thực phẩm'; 'In ấn'; 'Sơn'; 'Đồ gia dụng'; 'Đóng sách'; 'Đúc'; 'Hàn xì'; 'Đóng gói'; 'Sản xuất hộp'; 'Gốm'; 'Bê tông'; 'Rác thải'; 'Đường sắt'; 'Cao su, nhựa'; 'Vật liệu composite'; 'Nghề Mộc'; 'Ngư nghiệp'; 'Dệt may'; 'Xây dựng'; 'Cơ khí, kim loại'; 'Sân bay'; 'Nồi hơi'; 'Logistic'; 'Vận chuyển'; 'Điều dưỡng'; 'Chế tạo vật liệu'; 'Đóng tàu'; 'Nhà hàng'; 'Vệ sinh toà nhà'; 'Buồng phòng khách sạn'; 'Chế tạo máy'; 'Ô tô'; 'Lưu trú', 'Khách sạn'; 'Vận tải', 'Lái xe'; 'Điện, điện tử'; 'Kiến trúc'; 'Tài chính', 'Bảo hiểm'; 'Thiết kế'; 'Công nghệ thông tin'; 'Bảo trì, sửa chữa máy móc'; 'Quản lý sản xuất'; 'Giải trí', 'Du lịch'; 'Kế toán'; 'Kinh doanh, Sale, Tiếp thị'; 'Y tế'; 'Năng lượng';'Phiên dịch viên';'Giặt là'.\n
                    * Note: 
                    - 'nntt'->'Nông nghiệp trồng trọt', 'lmxd' -> 'Lái máy xây dựng\n
                    - 'cbtp','cctp','tp'->'Thực phẩm' , 'dgcn' -> 'Đóng gói công nghiệp'\n
                    - 'ks may'->'Dệt may', 'dkl'->'dập kim loại'\n
                    - 'lmxd' -> 'Lái máy xây dựng', 'lk điện tử' -> 'linh kiện điện tử', 'lkđt' -> 'linh kiện điện tử'\n
                    - 'front'->'Khách sạn', 'nh' -> 'nhà hàng', 'nncn' -> 'nông nghiệp chăn nuôi'\n
                    - 'hàn bán tự động'->'Hàn xì', 'htnt' -> 'hoàn thiện nội thất'\n
                    - 'hàn btđ'->'Hàn bán tự động'\n
                    - 'kaigo'->'Điều dưỡng'\n
                    - 'vận hành máy','vhm','nhóm 1','nhóm ngành 1','nhóm 2','nhóm ngành 2','đgcn'->'Cơ khí, kim loại'\n
                    - 'GCCK','gcck'->'Gia công cơ khí'\n
                    - 'nội thất','dán giấy','đường ống'->'Xây dựng'\n
                    If unavailable -> 'Empty'."""
META_JOB_SCHEMA = {
    "name": "job",
    "strict": True,
    "schema": {
            "type": "object",
            "description": "Return raw JSON only, without adding ``` or any other formatting or any other AI content",
            "properties": {
                "postType": {
                    "type": "string",
                    "enum": ["ỨNG VIÊN"]
                },
                "visa": {
                    "type": "string",
                    "description": f"""- Dưới đây là danh sách tiêu đề và từ khóa liên quan:\n
                    {VISA_JOB_KEYWORDS}\n
                    - Lưu ý: \n
                        + các từ viết tắt đ.Việt -> đầu Việt, đ.Nhật -> đầu Nhật, ks -> kỹ sư, tts -> thực tập sinh, tkt -> tokutei\n
                        + Nếu nội dung có nhắc đến "quay lại"->đầu Việt\n
                        + Nếu nội dung có nhắc đến "về nước trước hạn" hoặc "về nước rồi, quay lại"->Tokutei đầu Việt\n
                        + Nếu nội dung có nhắc đến sắp hết hạn visa tts-> Tokutei đầu Nhật\n
                    - Yêu cầu:\n
                    Phân tích nội dung để tìm ra loại visa phù hợp nhất dựa trên các từ khóa liên quan. Nếu không có các từ khóa thể hiện là đầu Việt thì mặc định là đầu Nhật\n
                    - Output: Bắt buộc phải chọn ra 1 tiêu đề phù hợp nhất từ danh sách đã đưa và trả về. không bao gồm câu từ AI. nếu không có từ khóa trong nội dung để phân tích thì phân tích theo tên nhóm \n""",
                    "enum": ["Thực tập sinh 3 năm", "Thực tập sinh 1 năm", "Thực tập sinh 3 go", "Tokutei đầu Việt", "Tokutei đầu Nhật", "Kỹ sư đầu Nhật", "Kỹ sư đầu Việt"]
                },
                "job": {
                    "type": "string",
                    "description": """bất cứ ngành nghề , công việc nào được nhắc đến trong nội dung tin nhắn , tham khảo nếu xuất hiện từ khóa viết tắt trong {CAREER_NOTE}. Nếu không nhắc đến ngành nghề thì ứng viên có bằng thực phẩm => 'thực phẩm', có bằng nào đề cập đến thì trả về ngành đó',
                    Nếu không có công việc nào thì trả về 'Không cung cấp'. """,
                },

                "workLocation": {
                    "type": "string",
                    "description": "Trả về bất cứ tỉnh, thành phố, khu vực nào được nhắc đến trong đơn hàng. Nếu không có thông tin về địa điểm làm việc thì trả về 'Empty'.",
                },
              
                "languageLevel": {
                    "type": "string",
                    "description": "Trình độ ngoại ngữ trong đơn nếu có nhiều N4,N3,N2 thì chọn N thấp nhất. Có các từ khóa như 'ko yc tiếng', 'không tiếng' => 'Không yêu cầu tiếng' ."
                    "nếu không có trình độ ngôn ngữ nào thì trả về 'Không cung cấp'.",
                    "enum": ["Không yêu cầu tiếng","JLPT N5", "JLPT N4", "JLPT N3", "JLPT N2", "JLPT N1", "Kaiwa N5", "Kaiwa N4", "Kaiwa N3", "Kaiwa N2", "Kaiwa N1", "Kaiwa N1", "Kaiwa N1", "Không cung cấp"]               
                },

                "gender": {
                    "type": "string",
                    "description": """Giới tính yêu cầu
                    - Nam nếu chỉ yêu cầu nam
                    - Nữ nếu chỉ yêu cầu nữ
                    - Cả Nam và Nữ nếu trong đơn có cả nam và nữ
                    """,
                    "enum": ["Nam", "Nữ", "Cả Nam và Nữ", 'Không cung cấp']
                },
               "specialConditions": {
                    "type": "array",
                    "description": """Trả về mảng các lựa chọn. Nếu có nhiều giá trị khác nhau, nối với nhau bởi dấu ';' (ví dụ: 'Tăng ca;Lương tốt').
                    Các trường hợp cụ thể:
                    - Nếu có nhắc đến 'tăng ca', 'tg ca', 'tca', 'tc', 'ot' hay làm thêm giờ thì kết quả trả về phải có 'Tăng ca'.
                    - Nếu có từ 'tiến cử', 'bao đậu' thì trả về 'Bao đỗ'.
                    - Nếu có từ 'thưởng', 'thg' thì trả về 'Thưởng'.
                    - Nếu có cụm từ 'lương cao' thì trả về 'Lương tốt'.
                    - Nếu có nhắc đến 'vợ chồng' thì trả về 'Vợ chồng'.
                    - Nếu có nhắc đến 'không yêu cầu kinh nghiệm', 'ko yc kn'thì trả về 'không yêu cầu kinh nghiệm'.
                    - Nếu có nhắc đến 'hỗ trợ chỗ ở' thì trả về 'Hỗ trợ chỗ ở'.
                    - Không trả về giá trị nếu từ khóa không xuất hiện trong nội dung.
                    - không trả về các giá trị trùng lặp trong mảng, một giá trị chỉ xuất hiện 1 lần.
                    """,
                    "items": {
                        "type": "string",
                        "enum": ["Bao đỗ", "Tăng ca", "Lương tốt", "Vợ chồng", "Hỗ trợ chỗ ở", "không yêu cầu kinh nghiệm", "Thưởng"]
                    },
                },
               "makeAI": {
                     "type": "string",
                    "description": """Mô tả đơn hàng chuẩn hóa bằng tiếng Việt, tóm gọn nội dung chính theo nội dung gốc, không tự động thêm thông tin không có trong dữ liệu\n
                    - ví dụ "Em tts tìm đơn cho thực phẩm cơm hộp hoặc bánh kẹo cho nam ko kén tỉnh ạ. Mong muốn hỗ trợ gino 2 càng tốt. Về nước lấy nenkin trc khi vào cty OK. E có jlpt n3, kaiwa taamf n4 cứng. cc thực phẩm. hạn đến 3/6 ạ. Mọi người ai có đơn cứu e vs ạ. E cảm ơn ạ" 
                    => Nam, đã có chứng chỉ Thực phẩm, JLPT N3, kaiwa tầm N4 cứng. Mong muốn tìm đơn Tokutei ngành Thực phẩm (cơm hộp, bánh kẹo), không kén vùng. Ưu tiên đơn hỗ trợ lên Gino 2. Đồng ý về nước lấy Nenkin trước khi vào công ty. Hạn đến 03/06.\n
                    - **Loại bỏ:** Từ viết tắt, thông tin quảng cáo, số điện thoại. \n
                    - **Không được trả về 'không cung cấp'**. \n """, 
                },
            },
        "required": [
                "postType",
                "visa",
                "languageLevel",
                "gender",
                "job",
                "specialConditions",
                "workLocation",
                "makeAI",
            ],
        "additionalProperties": False
    }
}