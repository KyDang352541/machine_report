import streamlit as st
import pandas as pd
import plotly.express as px

# ================================================
# ✅ ĐỌC TOÀN BỘ SHEET TRONG FILE EXCEL
# ================================================
def load_all_sheets(file):
    try:
        xls = pd.ExcelFile(file)
        sheet_data = {}
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            df.columns = df.columns.str.strip()
            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]  # Xóa cột thừa
            df["Loại máy"] = sheet_name  # Gắn tên sheet
            sheet_data[sheet_name] = df
        return sheet_data
    except Exception as e:
        st.error(f"❌ Không thể đọc file Excel: {e}")
        return {}

# ================================================
# 📊 BIỂU ĐỒ TỔNG GIỜ THEO MÁY TRONG DỰ ÁN
# ================================================
def plot_machine_by_project(df_filtered, project_name):
    col_machine = "Machine/máy"
    col_total_min = "Tổng thời gian gia công/Total machining time (min)"

    if any(col not in df_filtered.columns for col in [col_machine, col_total_min]):
        st.warning("⚠️ Thiếu cột cần thiết.")
        return

    df_group = df_filtered.groupby(col_machine)[col_total_min].sum().reset_index()

    fig = px.bar(
        df_group,
        x=col_machine,
        y=col_total_min,
        text_auto=".2s",
        color=col_machine,
        title=f"⏱️ Tổng thời gian theo máy - Dự án {project_name}"
    )
    st.plotly_chart(fig, use_container_width=True)

# ================================================
# 🚀 APP CHÍNH
# ================================================
def main():
    st.set_page_config(page_title="📂 Machine Report Viewer", layout="wide")
    st.title("📄 Báo cáo thời gian gia công theo Loại Máy & Dự Án")

    uploaded_file = st.file_uploader("📤 Tải lên file Excel", type=["xlsx"])
    if not uploaded_file:
        return

    sheet_data = load_all_sheets(uploaded_file)
    if not sheet_data:
        return

    # 👉 Chọn loại máy (tên sheet)
    machine_types = list(sheet_data.keys())
    selected_machine = st.selectbox("🛠️ Chọn loại máy (sheet)", machine_types)

    df = sheet_data[selected_machine]
    time_col = "Tổng thời gian gia công/Total machining time (min)"

    # Chuyển phút -> giờ
    if time_col in df.columns:
        df[time_col] = pd.to_numeric(df[time_col], errors="coerce")
        df["Thời gian (giờ)/Total time (hr)"] = df[time_col] / 60

    # 👉 Chọn dự án trong sheet đó
    col_project = "Mã dự án/Project"
    available_projects = df[col_project].dropna().unique().tolist()
    selected_project = st.selectbox("📁 Chọn dự án", available_projects)

    # 👉 Lọc dữ liệu theo dự án
    df_filtered = df[df[col_project] == selected_project]

    # 📋 Xem dữ liệu
    st.markdown("### 📄 Dữ liệu chi tiết")
    st.dataframe(df_filtered, use_container_width=True)

    # 📊 Vẽ biểu đồ tổng thời gian theo máy trong dự án
    st.markdown("---")
    plot_machine_by_project(df_filtered, selected_project)

# ================================================
# 🔁 CHẠY APP
# ================================================
if __name__ == "__main__":
    main()
