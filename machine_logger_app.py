# file: machine_report_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import BytesIO

FILE_PATH = 'machine_logs.xlsx'

st.set_page_config(page_title="Machine Time Report", layout="wide")
st.title("📊 Machine Usage Report")

# === Load dữ liệu ===
@st.cache_data
def load_data():
    if os.path.exists(FILE_PATH):
        return pd.read_excel(FILE_PATH, sheet_name='Logs', parse_dates=['Date'])
    else:
        st.warning("⚠️ No data found.")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()
def append_log_to_excel(filepath, log_data: dict, sheet_name="Logs"):
    """
    Append a dictionary as a new row into an Excel file, creating it if necessary.

    Parameters:
    - filepath: str - path to the Excel file
    - log_data: dict - keys = column names, values = row values
    - sheet_name: str - target sheet
    """
    df_new = pd.DataFrame([log_data])

    if not os.path.exists(filepath):
        # File doesn't exist -> create new with header
        df_new.to_excel(filepath, index=False, sheet_name=sheet_name)
        print(f"✅ Created new log file at {filepath}")
    else:
        try:
            with pd.ExcelWriter(filepath, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                # Load existing sheet to find starting row
                try:
                    existing_df = pd.read_excel(filepath, sheet_name=sheet_name)
                    startrow = len(existing_df) + 1
                except ValueError:
                    # Sheet doesn't exist -> write from row 0
                    startrow = 0

                df_new.to_excel(writer, sheet_name=sheet_name, index=False, header=startrow == 0, startrow=startrow)
                print(f"✅ Appended log to {filepath} (sheet: {sheet_name})")

        except InvalidFileException as e:
            print("❌ Error reading the Excel file:", e)
# === Bộ lọc cơ bản ===
with st.expander("🔍 Filter Options"):
    col1, col2, col3 = st.columns(3)

    with col1:
        machines = st.multiselect("🛠️ Machine", df['Machine'].unique(), default=df['Machine'].unique())
        projects = st.multiselect("📁 Project", df['Project'].unique(), default=df['Project'].unique())

    with col2:
        operators = st.multiselect("👷 Operator", df['Operator'].unique(), default=df['Operator'].unique())
        shifts = st.multiselect("⏱️ Shift", df['Shift'].unique(), default=df['Shift'].unique())

    with col3:
        date_range = st.date_input("📅 Date Range", value=[df['Date'].min(), df['Date'].max()])

# === Áp dụng bộ lọc ===
start_date, end_date = date_range
filtered_df = df[
    (df['Machine'].isin(machines)) &
    (df['Project'].isin(projects)) &
    (df['Operator'].isin(operators)) &
    (df['Shift'].isin(shifts)) &
    (df['Date'] >= pd.to_datetime(start_date)) &
    (df['Date'] <= pd.to_datetime(end_date))
]

st.subheader(f"📋 Filtered Logs ({len(filtered_df)} records)")
st.dataframe(filtered_df, use_container_width=True)

# === Tổng hợp dữ liệu ===
summary = filtered_df.groupby(["Project", "Machine"]).agg({"Hours": "sum"}).reset_index()
summary = summary.rename(columns={"Hours": "Total Hours"})

st.subheader("📊 Tổng thời gian theo Project và Machine")
st.dataframe(summary, use_container_width=True)

# === Biểu đồ lựa chọn ===
st.subheader("📈 Visualization")

chart_option = st.selectbox(
    "Chọn kiểu biểu đồ",
    ["Total Hours by Project", "Total Hours by Machine"]
)

if chart_option == "Total Hours by Project":
    fig = px.bar(
        summary.groupby("Project")["Total Hours"].sum().reset_index(),
        x="Project", y="Total Hours",
        title="Total Machine Hours by Project",
        color="Project", text_auto='.2s'
    )
else:
    fig = px.bar(
        summary.groupby("Machine")["Total Hours"].sum().reset_index(),
        x="Machine", y="Total Hours",
        title="Total Machine Hours by Machine",
        color="Machine", text_auto='.2s'
    )

st.plotly_chart(fig, use_container_width=True)

# === Xuất Excel ===
def convert_df_to_excel(df_filtered, df_summary):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_filtered.to_excel(writer, sheet_name='Filtered Logs', index=False)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
    output.seek(0)
    return output

excel_file = convert_df_to_excel(filtered_df, summary)

st.download_button(
    label="📥 Download Excel Report",
    data=excel_file,
    file_name="machine_usage_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
