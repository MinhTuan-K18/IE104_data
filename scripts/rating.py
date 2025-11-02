import pandas as pd
import random

def randomize_rating(df, column_name="RATING (MAX = 5)"):
    # Kiểm tra cột có tồn tại không
    if column_name not in df.columns:
        print(f"❌ Không tìm thấy cột '{column_name}' trong file CSV.")
        print("📄 Các cột hiện có:", list(df.columns))
        return df

    # In thống kê trước khi sửa
    zero_before = (df[column_name] == 0).sum() + df[column_name].isna().sum()
    print(f"🔍 Trước khi sửa: {zero_before} giá trị 0 hoặc NaN trong cột '{column_name}'")

    # Random lại các giá trị 0 hoặc NaN
    df[column_name] = df[column_name].apply(
        lambda x: round(random.uniform(3.5, 5.0), 1) if pd.isna(x) or x == 0 else x
    )

    # In thống kê sau khi sửa
    zero_after = (df[column_name] == 0).sum() + df[column_name].isna().sum()
    print(f"✅ Sau khi sửa: {zero_after} giá trị 0 hoặc NaN còn lại trong cột '{column_name}'")

    return df


def main():
    input_file = "test_data.csv"
    output_file = "test_data_updated.csv"

    # Đọc file CSV
    df = pd.read_csv(input_file)

    # Gọi hàm xử lý rating
    df = randomize_rating(df, column_name="RATING (MAX = 5)")

    # Ghi lại file mới
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"💾 Đã ghi dữ liệu mới vào '{output_file}'")


if __name__ == "__main__":
    main()
