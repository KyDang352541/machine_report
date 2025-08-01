import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from openpyxl import load_workbook
import os

# Constants
FILE_PATH = "machine_logs.xlsx"
SHEET_NAME = "Logs"

# Ensure the Excel file exists with correct structure
def initialize_excel_file():
    if not os.path.exists(FILE_PATH):
        df = pd.DataFrame(columns=["Date", "Machine", "Activity", "Hours", "User"])
        with pd.ExcelWriter(FILE_PATH, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=SHEET_NAME)

# Load log data from Excel
@st.cache_data
def load_data():
    return pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME, parse_dates=["Date"])

# Append new log entry to Excel
def append_log_to_excel(new_log):
    try:
        if os.path.exists(FILE_PATH):
            wb = load_workbook(FILE_PATH)
            ws = wb[SHEET_NAME]
            ws.append(new_log)
            wb.save(FILE_PATH)
        else:
            initialize_excel_file()
            append_log_to_excel(new_log)
    except Exception as e:
        st.error(f"Lỗi khi lưu log: {e}")

# Main UI
def main():
    st.title("📘 Machine Usage Logger")

    tab1, tab2 = st.tabs(["📝 Nhập dữ liệu", "📊 Báo cáo & Biểu đồ"])

    with tab1:
        st.subheader("Nhập thông tin sử dụng máy")
        with st.form("log_form"):
            col1, col2 = st.columns(2)
            with col1:
                log_date = st.date_input("Ngày", value=datetime.today())
                machine = st.text_input("Tên máy")
                user = st.text_input("Người sử dụng")
            with col2:
                activity = st.text_area("Hoạt động")
                hours = st.number_input("Số giờ", min_value=0.0, step=0.5)

            submitted = st.form_submit_button("Lưu log")
            if submitted:
                if not machine or not activity or not user:
                    st.warning("Vui lòng nhập đầy đủ thông tin.")
                else:
                    new_log = [log_date, machine, activity, hours, user]
                    append_log_to_excel(new_log)
                    st.success("✅ Đã lưu log thành công!")

    with tab2:
        st.subheader("Lọc & xuất báo cáo")

        df = load_data()
        if df.empty:
            st.info("Chưa có dữ liệu để hiển thị.")
            return

        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(by="Date")

        # Bộ lọc
        col1, col2 = st.columns(2)
        with col1:
            date_range = st.date_input("Khoảng ngày", value=[df["Date"].min(), df["Date"].max()])
        with col2:
            machine_filter = st.multiselect("Chọn máy", options=df["Machine"].unique(), default=df["Machine"].unique())

        filtered_df = df[
            (df["Date"] >= pd.to_datetime(date_range[0])) &
            (df["Date"] <= pd.to_datetime(date_range[1])) &
            (df["Machine"].isin(machine_filter))
        ]

        st.markdown(f"### 📄 Báo cáo: {len(filtered_df)} dòng dữ liệu")
        st.dataframe(filtered_df, use_container_width=True)

        # Xuất biểu đồ
        if not filtered_df.empty:
            st.markdown("### 📈 Thời gian sử dụng theo máy")
            chart_data = filtered_df.groupby("Machine")["Hours"].sum().sort_values()
            fig, ax = plt.subplots(figsize=(8, 4))
            chart_data.plot(kind="barh", ax=ax)
            ax.set_xlabel("Tổng số giờ")
            ax.set_ylabel("Máy")
            ax.set_title("Tổng thời gian sử dụng theo máy")
            st.pyplot(fig)

        # Nút tải về báo cáo Excel
        if not filtered_df.empty:
            to_download = filtered_df.copy()
            to_download["Date"] = to_download["Date"].dt.strftime("%Y-%m-%d")
            csv_data = to_download.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Tải báo cáo CSV",
                data=csv_data,
                file_name="machine_usage_report.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    initialize_excel_file()
    main()
