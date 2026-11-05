
import json
import os
import re
import unicodedata

# =========================================================
# CẤU HÌNH
# =========================================================

RULES_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "rules.json"
)


# =========================================================
# 1. RULES MẶC ĐỊNH
# =========================================================

def get_default_rules() -> dict:
    """
    Rules mặc định.

    Chỉ sử dụng các từ khóa có ý nghĩa rõ ràng.
    Không dùng từ khóa chung chung để tự suy đoán thông tin.
    """

    return {
        "visa_keywords": {
            "Kỹ sư": [
                "visa kỹ sư",
                "visa kĩ sư",
                "技術・人文知識・国際業務",
                "gijinkoku"
            ],

            "Tokutei": [
                "tokutei",
                "特定技能",
                "kỹ năng đặc định",
                "ky nang dac dinh"
            ],

            "Thực tập sinh": [
                "thực tập sinh",
                "thuc tap sinh",
                "tts",
                "技能実習"
            ],

            "Du học": [
                "du học",
                "du hoc",
                "留学生"
            ]
        },

        "language_keywords": {
            "N1": [
                "jlpt n1",
                "jlptn1",
                "n1 tiếng nhật",
                "tiếng nhật n1",
                "trình độ n1"
            ],

            "N2": [
                "jlpt n2",
                "jlptn2",
                "n2 tiếng nhật",
                "tiếng nhật n2",
                "trình độ n2"
            ],

            "N3": [
                "jlpt n3",
                "jlptn3",
                "n3 tiếng nhật",
                "tiếng nhật n3",
                "trình độ n3"
            ],

            "N4": [
                "jlpt n4",
                "jlptn4",
                "n4 tiếng nhật",
                "tiếng nhật n4",
                "trình độ n4"
            ],

            "N5": [
                "jlpt n5",
                "jlptn5",
                "n5 tiếng nhật",
                "tiếng nhật n5",
                "trình độ n5"
            ]
        }
    }


# =========================================================
# 2. LOAD RULES
# =========================================================

def load_rules() -> dict:
    """
    Đọc rules.json.

    Nếu chưa tồn tại thì tự tạo file mới.
    Nếu file lỗi thì sử dụng rules mặc định.
    """

    if not os.path.exists(RULES_FILE):

        rules = get_default_rules()

        try:
            with open(RULES_FILE, "w", encoding="utf-8") as f:
                json.dump(
                    rules,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            print(f"✅ Đã tạo file rules: {RULES_FILE}")

        except Exception as e:
            print(f"⚠️ Không thể tạo rules.json: {e}")

        return rules

    try:

        with open(RULES_FILE, "r", encoding="utf-8") as f:
            rules = json.load(f)

        # Đảm bảo các nhóm từ khóa cần thiết tồn tại
        default_rules = get_default_rules()

        for key, value in default_rules.items():
            if key not in rules or not isinstance(rules[key], dict):
                rules[key] = value

        return rules

    except (json.JSONDecodeError, OSError) as e:

        print(f"⚠️ Lỗi đọc rules.json: {e}")

        return get_default_rules()


# =========================================================
# 3. CHUẨN HÓA NỘI DUNG
# =========================================================

def normalize_text(text: str) -> str:
    """
    Chuẩn hóa văn bản để tìm kiếm từ khóa.

    - Chuyển chữ thường.
    - Chuẩn hóa Unicode.
    - Xóa khoảng trắng thừa.
    """

    if not text:
        return ""

    text = unicodedata.normalize("NFC", str(text))

    text = text.lower()

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================================================
# 4. KIỂM TRA TỪ KHÓA
# =========================================================

def contains_keyword(content: str, keyword: str) -> bool:
    """
    Kiểm tra từ khóa xuất hiện trong nội dung.

    Với từ khóa tiếng Việt có dấu hoặc cụm từ,
    sử dụng kiểm tra cụm từ để tránh match nhầm.
    """

    content = normalize_text(content)
    keyword = normalize_text(keyword)

    if not content or not keyword:
        return False

    # Các từ khóa có ký tự tiếng Nhật hoặc cụm từ
    if re.search(r"[\u3040-\u30ff\u3400-\u9fff]", keyword):
        return keyword in content

    # Dùng ranh giới từ cho từ khóa ngắn
    pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"

    return bool(re.search(pattern, content))


def find_keyword_match(content: str, keywords: dict) -> str:
    """
    Tìm nhóm từ khóa khớp đầu tiên.

    Trả về tên nhóm nếu tìm thấy.
    Không tìm thấy thì trả về chuỗi rỗng.
    """

    if not isinstance(keywords, dict):
        return ""

    for key, keyword_list in keywords.items():

        if not isinstance(keyword_list, list):
            continue

        for keyword in keyword_list:

            if contains_keyword(content, keyword):
                return key

    return ""


# =========================================================
# 5. XÁC ĐỊNH TRÌNH ĐỘ TIẾNG NHẬT
# =========================================================

def detect_language_level(content: str) -> str:
    """
    Chỉ nhận diện JLPT khi bài đăng ghi rõ trình độ.

    Không tự suy luận N4 từ câu Kaiwa N4.
    Không tự suy luận trình độ từ các từ như:
    giao tiếp tốt, tiếng Nhật khá, biết tiếng Nhật.
    """

    text = normalize_text(content)

    # Chỉ nhận diện khi có ngữ cảnh JLPT rõ ràng
    patterns = {
        "N1": [
            r"\bjlpt\s*n\s*1\b",
            r"\bjlptn1\b",
            r"\btrình độ\s*n\s*1\b",
            r"\btiếng nhật\s*n\s*1\b",
            r"\bn\s*1\s*tiếng nhật\b"
        ],

        "N2": [
            r"\bjlpt\s*n\s*2\b",
            r"\bjlptn2\b",
            r"\btrình độ\s*n\s*2\b",
            r"\btiếng nhật\s*n\s*2\b",
            r"\bn\s*2\s*tiếng nhật\b"
        ],

        "N3": [
            r"\bjlpt\s*n\s*3\b",
            r"\bjlptn3\b",
            r"\btrình độ\s*n\s*3\b",
            r"\btiếng nhật\s*n\s*3\b",
            r"\bn\s*3\s*tiếng nhật\b"
        ],

        "N4": [
            r"\bjlpt\s*n\s*4\b",
            r"\bjlptn4\b",
            r"\btrình độ\s*n\s*4\b",
            r"\btiếng nhật\s*n\s*4\b",
            r"\bn\s*4\s*tiếng nhật\b"
        ],

        "N5": [
            r"\bjlpt\s*n\s*5\b",
            r"\bjlptn5\b",
            r"\btrình độ\s*n\s*5\b",
            r"\btiếng nhật\s*n\s*5\b",
            r"\bn\s*5\s*tiếng nhật\b"
        ]
    }

    for level, level_patterns in patterns.items():

        for pattern in level_patterns:

            if re.search(pattern, text):
                return level

    return ""


# =========================================================
# 6. ÁP DỤNG RULES CHO THÔNG TIN ỨNG VIÊN
# =========================================================

def apply_rules(content: str, analyzed: dict, rules: dict) -> dict:
    """
    Bổ sung thông tin AI còn thiếu.

    Nguyên tắc:
    1. Không ghi đè dữ liệu AI đã có.
    2. Không tự đoán giới tính.
    3. Không tự đoán visa.
    4. Không tự suy luận trình độ tiếng Nhật.
    5. Chỉ bổ sung khi nội dung có bằng chứng rõ ràng.

    Hỗ trợ cả tên trường cũ và tên trường mới.
    """

    if not isinstance(analyzed, dict):
        analyzed = {}

    if not isinstance(rules, dict):
        rules = get_default_rules()

    result = analyzed.copy()

    # -----------------------------------------------------
    # 1. VISA
    # -----------------------------------------------------

    # Hỗ trợ schema mới: visa
    # Và schema cũ: visa_type

    visa_key = None

    if "visa" in result:
        visa_key = "visa"

    elif "visa_type" in result:
        visa_key = "visa_type"

    else:
        visa_key = "visa"

    current_visa = result.get(visa_key)

    unknown_values = [
        None,
        "",
        "không cung cấp",
        "chưa cung cấp",
        "không rõ",
        "unknown",
        "none"
    ]

    if normalize_text(current_visa) in unknown_values:

        visa = find_keyword_match(
            content,
            rules.get("visa_keywords", {})
        )

        if visa:

            result[visa_key] = visa

            print(f"   📌 Rules bổ sung visa: {visa}")

    # -----------------------------------------------------
    # 2. TRÌNH ĐỘ TIẾNG NHẬT
    # -----------------------------------------------------

    # Hỗ trợ schema mới: languageLevel
    # Và schema cũ: japanese_level

    language_key = None

    if "languageLevel" in result:
        language_key = "languageLevel"

    elif "japanese_level" in result:
        language_key = "japanese_level"

    else:
        language_key = "languageLevel"

    current_level = result.get(language_key)

    if normalize_text(current_level) in unknown_values:

        level = detect_language_level(content)

        if level:

            result[language_key] = level

            print(f"   📌 Rules bổ sung tiếng Nhật: {level}")

    # -----------------------------------------------------
    # 3. GIỚI TÍNH
    # -----------------------------------------------------

    # Không tự động xác định giới tính bằng từ khóa nam/nữ.
    #
    # Ví dụ:
    # "Nam nữ đều được" không có nghĩa người đăng là nam.
    # "Tìm đơn cho vợ" không có nghĩa người đăng là nữ.
    #
    # AI chỉ nên trích xuất khi người đăng nói rõ giới tính
    # của chính mình.

    # Không thực hiện tự động bổ sung gender.

    return result
