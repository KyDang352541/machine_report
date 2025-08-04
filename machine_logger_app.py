import streamlit as st
import pandas as pd
import plotly.express as px

# ================================================
# ✅ ĐỌC TẤT CẢ SHEET VÀ LÀM SẠCH
# ================================================
def load_all_sheets(file):
    try:
        xls = pd.ExcelFile(file)
        sheet_data = {}
        for sheet_name in xls.sheet_names:
            if sheet_name == "ROBOT":
                df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=1)
            else:
                df = pd.read_excel(xls, sheet_name=sheet_name)

            df.columns = df.columns.map(str).str.strip()
            df = df.loc[:, ~df.columns.map(str).str.contains("^Unnamed")]
            df["Loại máy"] = sheet_name

            # Làm sạch cột ngày
            if "Ngày/Date" in df.columns:
                df["Ngày/Date"] = pd.to_datetime(df["Ngày/Date"], errors="coerce", dayfirst=True)

            # Làm sạch thời gian (phút → giờ)
            col_min = "Tổng thời gian gia công/Total machining time (min)"
            if col_min in df.columns:
                df[col_min] = pd.to_numeric(df[col_min], errors="coerce")
                df["Thời gian (giờ)/Total time (hr)"] = df[col_min] / 60

            sheet_data[sheet_name] = df

        return sheet_data
    except Exception as e:
        st.error(f"❌ Không thể đọc file Excel: {e}")
        return {}
# ================================================
# 📊 VẼ BIỂU ĐỒ THEO MÁY
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

    # 👉 Chọn loại máy (sheet)
    machine_types = list(sheet_data.keys())
    selected_machine = st.selectbox("🛠️ Chọn loại máy", machine_types)

    df = sheet_data[selected_machine]

    # 🔍 Xác định cột dự án
    project_col = "Mã dự án/Project"
    if project_col not in df.columns:
        st.error("❌ Không tìm thấy cột 'Mã dự án/Project'.")
        st.write("Các cột có trong dữ liệu:", df.columns.tolist())
        return

    # 👉 Chọn dự án
    available_projects = df[project_col].dropna().unique().tolist()
    selected_project = st.selectbox("📁 Chọn dự án", available_projects)

    # 👉 Lọc và hiển thị
    df_filtered = df[df[project_col] == selected_project]

    st.markdown("### 📄 Dữ liệu chi tiết")
    st.dataframe(df_filtered, use_container_width=True)

    st.markdown("---")
    plot_machine_by_project(df_filtered, selected_project)

# ================================================
# 🔁 CHẠY APP
# ================================================
if __name__ == "__main__":
    main()
