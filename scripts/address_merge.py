import os
import pandas as pd
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

# ======= Load .env =======
load_dotenv()

cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
api_key = os.getenv("CLOUDINARY_API_KEY")
api_secret = os.getenv("CLOUDINARY_API_SECRET")

if not all([cloud_name, api_key, api_secret]):
    raise ValueError("Missing Cloudinary credentials in .env file.")

# ======= Cấu hình Cloudinary =======
cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret
)

# ======= Đường dẫn file CSV và thư mục ảnh =======
csv_file = "data.csv"
image_folder = os.path.dirname(os.path.abspath(__file__))  # thư mục chứa file script

# ======= Đọc file CSV =======
df = pd.read_csv(csv_file)

# ======= Các đuôi ảnh được hỗ trợ =======
supported_extensions = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp")

# ======= Biến log =======
deleted_count = 0
uploaded_count = 0
updated_codes = []

# ======= Duyệt từng file ảnh trong thư mục =======
for filename in os.listdir(image_folder):
    if not filename.lower().endswith(supported_extensions):
        continue
    
    code_name = os.path.splitext(filename)[0]  # tách tên file bỏ phần mở rộng
    
    # ======= Xóa ảnh trùng tên trên Cloudinary =======
    try:
        cloudinary.api.delete_resources([code_name])
        print(f"[DELETE] Deleted existing image on Cloudinary: {code_name}")
        deleted_count += 1
    except cloudinary.api.Error:
        print(f"[DELETE] No existing image to delete for {code_name}.")
    
    # ======= Upload ảnh mới =======
    local_path = os.path.join(image_folder, filename)
    upload_result = cloudinary.uploader.upload(local_path, public_id=code_name)
    
    image_url = upload_result.get('secure_url')
    print(f"[UPLOAD] Uploaded {filename} -> {image_url}")
    uploaded_count += 1
    
    # ======= Ghi link vào đúng dòng trong CSV dựa trên CODE =======
    if df['CODE'].isin([code_name]).any():
        df.loc[df['CODE'] == code_name, 'image_url'] = image_url
        updated_codes.append(code_name)
        print(f"[UPDATE] Updated image_url for CODE: {code_name}")
    else:
        print(f"[WARN] CODE {code_name} not found in CSV.")

# ======= Lưu CSV đã cập nhật =======
output_csv = "data_with_images.csv"
df.to_csv(output_csv, index=False)

# ======= Log tổng hợp =======
print("\n===== SUMMARY =====")
print(f"Total images deleted from Cloudinary: {deleted_count}")
print(f"Total images uploaded: {uploaded_count}")
print(f"Total codes updated in CSV: {len(updated_codes)}")
print(f"Updated codes: {', '.join(updated_codes)}")
print(f"Updated CSV saved as: {output_csv}")
