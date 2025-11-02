import csv
import os
import re
import requests
import unicodedata

# === Hàm loại bỏ dấu tiếng Việt và ký tự không hợp lệ ===
def clean_filename(name):
    name = unicodedata.normalize('NFKD', name)
    name = ''.join([c for c in name if not unicodedata.combining(c)])
    name = re.sub(r'[^\x00-\x7F]', '', name)  # bỏ ký tự không phải ASCII
    name = name.replace(' ', '_')
    name = re.sub(r'[\\/:*?"<>|]', '', name)  # bỏ ký tự cấm trong tên file
    return name.strip('_')

# === Cấu hình ===
csv_file = "restaurants.csv"     # file CSV đầu vào
output_dir = "restaurants"       # thư mục lưu ảnh
os.makedirs(output_dir, exist_ok=True)

# === Biến đếm ===
success_count = 0
error_count = 0

# === Đọc file CSV và tải ảnh ===
with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        image_url = row.get("image_path")
        location = row.get("LOCATION")

        if not image_url or not location:
            continue

        clean_name = clean_filename(location)

        ext = os.path.splitext(image_url)[1].split('?')[0]
        if not ext:
            ext = ".jpg"

        file_path = os.path.join(output_dir, f"{clean_name}{ext}")

        try:
            response = requests.get(image_url, timeout=15)
            response.raise_for_status()

            with open(file_path, "wb") as img_file:
                img_file.write(response.content)

            print(f"✅ Đã tải: {file_path}")
            success_count += 1

        except Exception as e:
            print(f"❌ Lỗi khi tải {image_url}: {e}")
            error_count += 1

# === Tổng kết ===
print("\n====================")
print(f"Ảnh tải thành công: {success_count}")
print(f"Ảnh bị lỗi:         {error_count}")

