from google import genai
import os
from dotenv import load_dotenv

# ===== 1️⃣ Load environment =====
load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")
print("🔑 API KEY =", api_key)

# ===== 2️⃣ Khởi tạo client =====
client = genai.Client(api_key=api_key)

# ===== 3️⃣ Gọi model test =====
resp = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Say hello from Gemini!"
)

# ===== 4️⃣ In cấu trúc trả về =====
print("\n🧠 Response object:", type(resp))
print("📦 Raw response:\n", resp)
print("\n📄 Text output:", getattr(resp, "text", None))
