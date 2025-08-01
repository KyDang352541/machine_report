import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ==========================
# 🔧 Cấu hình đường dẫn file
# ==========================
FILE_PATH = "machine_logs.xlsx"
SHEET_NAME = "Logs"

# ==========================
# ✅ Hàm ghi log vào Excel
# ==========================
def append_log_to_excel(file_path, new_log):
    try:
        df = pd.read_excel(file_path, sheet_name=SHEET_NAME)
    except (FileNotFoundError, ValueError):
        df = pd.DataFrame()

    df = pd.concat([df, pd.DataFrame([new_log])], ignore_index=True)

    with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=SHEET_NAME, index=False)

# ==========================
# ✅ Hàm tải dữ liệu từ Excel
# ==========================
def load_logs(file_path):
    try:
        df = pd.read_excel(file_path, sheet_name=SHEET_NAME)
        return df
    except Exception:
        return pd.DataFrame()

# ==========================
# 🖼️ Giao diện Streamlit
# ==========================
st.set_page_config(page_title="Machine Log", layout="centered")
st.title("📊 Machine Usage Report")

# ================
# 🔽 Nhập dữ liệu
# ================
st.markdown("## 📝 Add New Machine Log")

with st.form("log_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("📅 Date", value=datetime.today())
        machine = st.text_input("🛠️ Machine")
        project = st.text_input("📁 Project")
    with col2:
        operator = st.text_input("👷 Operator")
        shift = st.selectbox("⏱️ Shift", ["Morning", "Evening", "Night"])
        hours = st.number_input("⏰ Hours", min_value=0.0, step=0.5)

    submitted = st.form_submit_button("➕ Save Log")

    if submitted:
        log_entry = {
            "Date": pd.to_datetime(date),
            "Machine": machine,
            "Project": project,
            "Operator": operator,
            "Shift": shift,
            "Hours": hours,
        }
        try:
            append_log_to_excel(FILE_PATH, log_entry)
            st.success("✅ Log saved successfully!")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"❌ Failed to save log: {e}")

# ==========================
# 📄 Hiển thị dữ liệu đã nhập
# ==========================
st.markdown("## 📋 Logged Data")

log_df = load_logs(FILE_PATH)
if not log_df.empty:
    st.dataframe(log_df, use_container_width=True)
else:
    st.info("Chưa có dữ liệu nào được ghi.")
