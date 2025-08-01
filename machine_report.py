import pandas as pd

# === Đọc dữ liệu từ file Excel ===
def load_machine_logs(file_path='machine_logs.xlsx'):
    df = pd.read_excel(file_path, sheet_name='Logs')
    
    # Đảm bảo định dạng ngày và giờ
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Start'] = pd.to_datetime(df['Start'].astype(str), format='%H:%M', errors='coerce')
    df['End'] = pd.to_datetime(df['End'].astype(str), format='%H:%M', errors='coerce')
    
    # Tính lại số giờ nếu cần
    df['Hours'] = (df['End'] - df['Start']).dt.total_seconds() / 3600
    
    return df

# === Test: In dữ liệu ===
if __name__ == "__main__":
    df_logs = load_machine_logs()
    print(df_logs.head())
