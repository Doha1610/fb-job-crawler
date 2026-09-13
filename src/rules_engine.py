import json
import os
import re

RULES_FILE = "rules.json"

# Tự động gán visa_type, japanese_level, gender từ từ khóa nếu AI không detect được.
def get_default_rules() -> dict:
    """Rules mặc định"""
    return {
        "visa_keywords": {
            "kỹ sư": ["kỹ sư", "ky su", "engineer", "技人国", "gijinkoku"],
            "tokutei": ["tokutei", "特定技能", "đặc định"],
            "thực tập sinh": ["thực tập sinh", "tts", "研修生", "kenshusei"],
            "du học": ["du học", "du hoc", "留学生"],
            "kỹ năng đặc định": ["kỹ năng đặc định", "đặc định"]
        },
        "language_keywords": {
            "N1": ["n1", "n 1"],
            "N2": ["n2", "n 2"],
            "N3": ["n3", "n 3"],
            "N4": ["n4", "n 4"],
            "N5": ["n5", "n 5"]
        },
        "gender_keywords": {
            "nam": ["nam", "男", "male"],
            "nữ": ["nữ", "nu", "女", "female"]
        }
    }


def load_rules() -> dict:
    """Đọc rules từ file, tạo mới nếu chưa có"""
    if not os.path.exists(RULES_FILE):
        rules = get_default_rules()
        with open(RULES_FILE, "w", encoding="utf-8") as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)
        print(f"✅ Đã tạo file rules: {RULES_FILE}")
        return rules

    try:
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Lỗi đọc rules: {e}, dùng mặc định")
        return get_default_rules()


def find_keyword_match(content: str, keywords: dict) -> str:
    """
    Tìm từ khóa trong content.
    Trả về key của nhóm khớp đầu tiên.
    """
    content_lower = content.lower()
    
    for key, kws in keywords.items():
        for kw in kws:
            # Dùng word boundary để tránh match nhầm
            pattern = r'\b' + re.escape(kw.lower()) + r'\b'
            if re.search(pattern, content_lower):
                return key
            # Fallback: kiểm tra substring đơn giản
            if kw.lower() in content_lower:
                return key
    return ""


def apply_rules(content: str, analyzed: dict, rules: dict) -> dict:
    """
    Áp rules để bổ sung thông tin mà AI bỏ sót.
    Không ghi đè nếu AI đã detect được.
    """
    result = analyzed.copy()
    content_lower = content.lower()

    # ===== 1. VISA =====
    if not result.get("visa_type"):
        visa = find_keyword_match(content, rules.get("visa_keywords", {}))
        if visa:
            result["visa_type"] = visa
            print(f"   📌 Rules bổ sung visa: {visa}")

    # ===== 2. JAPANESE LEVEL =====
    if not result.get("japanese_level"):
        level = find_keyword_match(content, rules.get("language_keywords", {}))
        if level:
            result["japanese_level"] = level
            print(f"   📌 Rules bổ sung tiếng Nhật: {level}")

    # ===== 3. GENDER =====
    if not result.get("gender"):
        gender = find_keyword_match(content, rules.get("gender_keywords", {}))
        if gender:
            result["gender"] = gender
            print(f"   📌 Rules bổ sung giới tính: {gender}")

    return result