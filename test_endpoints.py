import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

# Các endpoint cần thử
endpoints = [
    "https://api.openai.com/v1",  # Mặc định
    "https://api.ckey.vn",
    "https://api.ckey.vn/v1",
    "https://api.ckey.vn/api",
    "https://api.ckey.vn/openai",
    "https://api.ckey.vn/v1/chat/completions",
]

print("=" * 60)
print("🔍 TÌM ENDPOINT CỦA CKEY.VN")
print("=" * 60)

for endpoint in endpoints:
    try:
        print(f"\n⏳ Testing endpoint: {endpoint}")

        client = OpenAI(
            api_key=api_key,
            base_url=endpoint
        )

        response = client.chat.completions.create(
            model="gpt-5.6-sol",
            messages=[{"role": "user", "content": "Say OK"}],
            max_tokens=5,
            timeout=5
        )

        print(f"✅ THÀNH CÔNG!")
        print(f"   Endpoint: {endpoint}")
        print(f"   Response: {response.choices[0].message.content}")
        print("\n💡 Dùng endpoint này trong code!")
        break

    except Exception as e:
        error = str(e)
        if "404" in error:
            print(f"❌ {endpoint}: 404 Not Found")
        elif "401" in error:
            print(f"❌ {endpoint}: 401 Key không hợp lệ")
        else:
            print(f"❌ {endpoint}: {error[:60]}...")