import pytesseract
from PIL import Image

# ===== CHỈ ĐỊNH ĐƯỜNG DẪN TESSERACT =====
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# ==========================================

# Đường dẫn ảnh local
image_path = "Screenshot 2026-09-13 215318.png"

print("="*60)
print("🧪 TEST OCR VỚI ẢNH LOCAL")
print("="*60)

try:
    img = Image.open(image_path)
    print(f"✅ Đã mở ảnh: {img.size}")
    
    text = pytesseract.image_to_string(img, lang='vie')
    
    print("\n📝 Kết quả:")
    print("-"*60)
    print(text)
    print("-"*60)
    
except Exception as e:
    print(f"❌ Lỗi: {e}")