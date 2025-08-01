# file: machine_report_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os

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

# === Bộ lọc ===
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

# === Tổng hợp theo máy ===
st.subheader("📌 Total Hours by Machine")
summary_machine = filtered_df.groupby('Machine')['Hours'].sum().reset_index()
st.dataframe(summary_machine, use_container_width=True)
fig1 = px.bar(summary_machine, x='Machine', y='Hours', title='Total Hours per Machine', text='Hours')
st.plotly_chart(fig1, use_container_width=True)

# === Tổng hợp theo dự án ===
st.subheader("📌 Total Hours by Project")
summary_project = filtered_df.groupby('Project')['Hours'].sum().reset_index()
fig2 = px.pie(summary_project, names='Project', values='Hours', title='Hours by Project')
st.plotly_chart(fig2, use_container_width=True)

# === Tổng hợp theo operator ===
st.subheader("📌 Total Hours by Operator")
summary_op = filtered_df.groupby('Operator')['Hours'].sum().reset_index()
fig3 = px.bar(summary_op, x='Operator', y='Hours', title='Hours by Operator', text='Hours')
st.plotly_chart(fig3, use_container_width=True)
    # =========================================
    # BƯỚC 2: HIỂN THỊ & LỌC DỮ LIỆU
    # =========================================
    st.markdown("---")
    st.subheader("📋 Dữ liệu đã nhập")

    if not df.empty:
        with st.expander("🔍 Tùy chọn lọc dữ liệu", expanded=False):
            col1, col2 = st.columns(2)

            # Bộ lọc theo ngày
            with col1:
                date_filter = st.date_input("Lọc theo ngày:", value=None)
            with col2:
                machine_filter = st.multiselect("Lọc theo máy:", options=df["Machine"].unique())

            # Áp dụng bộ lọc
            filtered_df = df.copy()
            if date_filter:
    # =========================================
    # BƯỚC 3: PHÂN TÍCH VÀ BIỂU ĐỒ
    # =========================================
    st.markdown("---")
    st.subheader("📈 Thống kê theo giờ máy")

    if not df.empty:
        # Chuyển cột Date sang datetime nếu chưa đúng định dạng
        df["Date"] = pd.to_datetime(df["Date"])

        # Tính tổng giờ theo máy
        total_hours_by_machine = df.groupby("Machine")["Hours"].sum().reset_index()

        # Biểu đồ tổng giờ theo máy
        st.markdown("### 🛠️ Tổng giờ làm theo Máy")
        fig1 = px.bar(total_hours_by_machine, x="Machine", y="Hours", title="Tổng giờ làm theo Máy", color="Machine", text="Hours")
        st.plotly_chart(fig1, use_container_width=True)

        # Biểu đồ theo ngày
        daily_hours = df.groupby("Date")["Hours"].sum().reset_index()
        st.markdown("### 📅 Tổng giờ làm theo Ngày")
        fig2 = px.line(daily_hours, x="Date", y="Hours", markers=True, title="Tổng giờ theo Ngày")
        st.plotly_chart(fig2, use_container_width=True)

        # Biểu đồ theo tháng
        df["Month"] = df["Date"].dt.t
        # Tiếp nối từ phần trước
st.markdown("## 📅 Report Viewer")

# Bộ lọc thời gian
col1, col2 = st.columns(2)
with col1:
    from_date = st.date_input("From date", pd.to_datetime(df["Start Time"]).min().date())
with col2:
    to_date = st.date_input("To date", pd.to_datetime(df["End Time"]).max().date())

# Bộ lọc dự án và máy
projects = st.multiselect("Select Projects", options=df["Project"].unique(), default=df["Project"].unique())
machines = st.multiselect("Select Machines", options=df["Machine"].unique(), default=df["Machine"].unique())

# Lọc dữ liệu
filtered_df = df[
    (df["Start Time"].dt.date >= from_date) &
    (df["End Time"].dt.date <= to_date) &
    (df["Project"].isin(projects)) &
    (df["Machine"].isin(machines))
]

st.markdown(f"### 📋 Filtered Machine Logs ({len(filtered_df)} records)")
st.dataframe(filtered_df)

# Tổng thời gian sử dụng theo Project + Machine
summary = filtered_df.groupby(["Project", "Machine"]).agg({"Duration (hrs)": "sum"}).reset_index()
summary = summary.rename(columns={"Duration (hrs)": "Total Hours"})

st.markdown("### 📊 Total Machine Hours by Project and Machine")
st.dataframe(summary)

# Cho phép tải xuống báo cáo
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
st.markdown("## 📈 Visualization")

# Lựa chọn loại biểu đồ
chart_option = st.selectbox(
    "Select chart type",
    ["Total Hours by Project", "Total Hours by Machine"]
)

# Tạo biểu đồ tùy theo lựa chọn
if chart_option == "Total Hours by Project":
    fig = px.bar(
        summary.groupby("Project")["Total Hours"].sum().reset_index(),
        x="Project", y="Total Hours",
        title="Total Machine Hours by Project",
        labels={"Total Hours": "Hours"},
        color="Project",
        text_auto='.2s'
    )
elif chart_option == "Total Hours by Machine":
    fig = px.bar(
        summary.groupby("Machine")["Total Hours"].sum().reset_index(),
        x="Machine", y="Total Hours",
        title="Total Machine Hours by Machine",
        labels={"Total Hours": "Hours"},
        color="Machine",
        text_auto='.2s'
    )

st.plotly_chart(fig, use_container_width=True)

