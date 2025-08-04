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
            # Đọc dữ liệu
            df = pd.read_excel(xls, sheet_name=sheet_name)

            # Làm sạch tên cột
            df.columns = df.columns.map(str).str.strip()
            df = df.loc[:, ~df.columns.map(str).str.contains("^Unnamed")]

            # Gán tên loại máy
            df["Loại máy"] = sheet_name

            # Làm sạch ngày nếu có
            if "Ngày/Date" in df.columns:
                df["Ngày/Date"] = pd.to_datetime(df["Ngày/Date"], errors="coerce", dayfirst=True)

            # Làm sạch SL/Qty nếu cần
            if "SL/Qty" in df.columns:
                df["SL/Qty"] = df["SL/Qty"].astype(str).str.extract(r"(\d+(?:\.\d+)?)")
                df["SL/Qty"] = pd.to_numeric(df["SL/Qty"], errors="coerce")

            # Làm sạch thời gian và chuyển phút sang giờ
            col_min = "Tổng thời gian gia công/Total machining time (min)"
            if col_min in df.columns:
                df[col_min] = pd.to_numeric(df[col_min], errors="coerce")
                df["Thời gian (giờ)/Total time (hr)"] = df[col_min] / 60

            # Lưu lại
            sheet_data[sheet_name] = df

        return sheet_data

    except Exception as e:
        st.error(f"❌ Không thể đọc file Excel: {e}")
        return {}

# ================================================
# 📊 VẼ BIỂU ĐỒ GIỜ THEO MÁY
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
# 🚀 ỨNG DỤNG CHÍNH
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

    # 🔍 Kiểm tra cột "Mã dự án/Project"
    col_project = "Mã dự án/Project"
    if col_project not in df.columns:
        st.error(f"❌ Không tìm thấy cột '{col_project}'.")
        st.write("Cột hiện có:", df.columns.tolist())
        return

    available_projects = df[col_project].dropna().unique().tolist()
    selected_project = st.selectbox("📁 Chọn dự án", available_projects)

    df_filtered = df[df[col_project] == selected_project]

    # 📋 Hiển thị bảng dữ liệu
    st.markdown("### 📄 Dữ liệu chi tiết")
    st.dataframe(df_filtered, use_container_width=True)

    # 📊 Vẽ biểu đồ
    st.markdown("---")
    plot_machine_by_project(df_filtered, selected_project)

# ================================================
# 🔁 CHẠY APP
# ================================================
if __name__ == "__main__":
    main()
