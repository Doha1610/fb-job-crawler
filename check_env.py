import os
from dotenv import load_dotenv
import sys

# In ra đường dẫn hiện tại
print(f"📁 Thư mục hiện tại: {os.getcwd()}")

# Load .env
load_dotenv()

# Lấy API key
api_key = os.getenv("OPENAI_API_KEY")

# Kiểm tra
if api_key:
    # Chỉ in 10 ký tự đầu và 5 ký tự cuối để bảo mật
    masked = api_key[:10] + "..." + api_key[-5:]
    print(f"🔑 API key: {masked}")
    print(f"📏 Độ dài key: {len(api_key)} ký tự")

    # Kiểm tra định dạng
    if api_key.startswith("sk-proj-"):
        print("✅ Key mới (sk-proj-)")
    elif api_key.startswith("sk-"):
        print("✅ Key cũ (sk-)")
    else:
        print("⚠️ Key không đúng định dạng!")
else:
    print("❌ KHÔNG tìm thấy API key!")

# Kiểm tra file .env tồn tại
env_path = os.path.join(os.getcwd(), ".env")
if os.path.exists(env_path):
    print(f"✅ File .env tồn tại tại: {env_path}")
else:
    print(f"❌ Không tìm thấy file .env tại: {env_path}")