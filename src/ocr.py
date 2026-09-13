import pytesseract
from PIL import Image
import requests
from io import BytesIO

# ===== CHỈ ĐỊNH ĐƯỜNG DẪN TESSERACT =====
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# ==========================================


def extract_text_from_image(image_url: str) -> str:
    """Đọc chữ từ ảnh bằng OCR"""
    try:
        print(f"🖼️ Đang tải ảnh...")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content))
        text = pytesseract.image_to_string(img, lang='vie')
        
        text = text.replace("\n", " ").strip()
        text = " ".join(text.split())
        
        print(f"✅ Đọc được {len(text)} ký tự từ ảnh")
        return text
        
    except Exception as e:
        print(f"❌ Lỗi OCR: {e}")
        return ""