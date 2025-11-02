import os
import json
import time
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
import google.generativeai as genai

# ==== CONFIG ====
load_dotenv()  # Load file .env chứa GEMINI_API_KEY
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env")

INPUT_FILE = "hotels.csv"
OUTPUT_FILE = "hotels_with_address.csv"
CACHE_FILE = "address_cache.json"
MODEL_NAME = "gemini-2.0-flash"
BATCH_SIZE = 10             # số lượng địa điểm mỗi request
SLEEP_BETWEEN_CALLS = 2     # nghỉ giữa các batch (giây)
# =================

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(MODEL_NAME)

# Load cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
else:
    cache = {}

# Đọc dữ liệu
df = pd.read_csv(INPUT_FILE)
if "Address" not in df.columns:
    df["Address"] = ""

# Lấy danh sách cần xử lý
pending_locations = [
    (idx, str(row["LOCATION"]).strip())
    for idx, row in df.iterrows()
    if str(row["LOCATION"]).strip() and not str(row["Address"]).strip()
]

print(f"🔍 Need to query {len(pending_locations)} locations")

# Chia batch
for i in tqdm(range(0, len(pending_locations), BATCH_SIZE)):
    batch = pending_locations[i : i + BATCH_SIZE]
    batch_locations = [loc for _, loc in batch]

    # Kiểm tra cache trước
    remaining = [loc for loc in batch_locations if loc not in cache]
    if not remaining:
        for idx, loc in batch:
            df.at[idx, "Address"] = cache[loc]
        continue

    prompt = (
        "You are a helpful assistant that provides full English addresses.\n"
        "For each of the following hotel or location names, "
        "return only the correct English address in one line (no description, no numbering).\n"
        "All places are located in or near Ho Chi Minh City, Vietnam (Binh Duong, Dong Nai, Vung Tau also acceptable).\n\n"
        "Format your answer strictly as JSON like this:\n"
        "{\n"
        "  \"Hotel A\": \"Address A\",\n"
        "  \"Hotel B\": \"Address B\"\n"
        "}\n\n"
        f"Here are the locations:\n{json.dumps(remaining, ensure_ascii=False, indent=2)}"
    )

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # tìm phần JSON trong phản hồi
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start : end + 1]

        try:
            result = json.loads(text)
        except Exception:
            print("⚠️ Could not parse JSON, using fallback matching")
            result = {}

        # Ghi kết quả
        for idx, loc in batch:
            address = result.get(loc) or "Not found"
            cache[loc] = address
            df.at[idx, "Address"] = address

        # Lưu cache và output tạm thời
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

        time.sleep(SLEEP_BETWEEN_CALLS)

    except Exception as e:
        print(f"❌ Error with batch {i // BATCH_SIZE + 1}: {e}")
        time.sleep(5)
        continue

print(f"✅ Done! All results saved to {OUTPUT_FILE}")
