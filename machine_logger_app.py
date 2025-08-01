import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import os

FILE_PATH = 'machine_logs.xlsx'

# === Hàm ghi dữ liệu vào file Excel ===
def save_log_to_excel(log_entry):
    if not os.path.exists(FILE_PATH):
        df = pd.DataFrame([log_entry])
    else:
        try:
            df = pd.read_excel(FILE_PATH, sheet_name='Logs')
        except ValueError:
            df = pd.DataFrame()

        df = pd.concat([df, pd.DataFrame([log_entry])], ignore_index=True)

    with pd.ExcelWriter(FILE_PATH, engine='openpyxl', mode='w') as writer:
        df.to_excel(writer, sheet_name='Logs', index=False)

# === Giao diện nhập liệu ===
st.set_page_config(page_title="Machine Time Log", layout="centered")
st.title("🛠️ Machine Time Log Entry")

with st.form("machine_time_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        log_date = st.date_input("📅 Date", value=date.today())
        machine = st.selectbox("🛠️ Machine", ["CNC-1", "CNC-2", "Autoclave", "Robot"])
        operator = st.text_input("👷 Operator")

    with col2:
        project = st.text_input("📁 Project")
        shift = st.selectbox("⏱️ Shift", ["Morning", "Afternoon", "Night"])
        start_time = st.time_input("▶️ Start Time", value=time(7, 30))

    with col3:
        end_time = st.time_input("⏹️ End Time", value=time(11, 30))
        notes = st.text_input("📝 Notes")

    submitted = st.form_submit_button("✅ Save")

    if submitted:
        # Tính giờ
        start_dt = datetime.combine(log_date, start_time)
        end_dt = datetime.combine(log_date, end_time)

        if end_dt <= start_dt:
            st.error("❌ End time must be after start time.")
        else:
            hours = round((end_dt - start_dt).total_seconds() / 3600, 2)

            log_entry = {
                "Date": log_date,
                "Machine": machine,
                "Project": project,
                "Shift": shift,
                "Start": start_time.strftime("%H:%M"),
                "End": end_time.strftime("%H:%M"),
                "Hours": hours,
                "Operator": operator,
                "Notes": notes
            }

            save_log_to_excel(log_entry)
            st.success(f"✅ Log saved: {hours} hours recorded for {machine}.")
