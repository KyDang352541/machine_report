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
