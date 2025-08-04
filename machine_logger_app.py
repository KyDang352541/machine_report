import streamlit as st
import pandas as pd
import plotly.express as px

# ================================================
# ✅ ĐỌC TOÀN BỘ SHEET TRONG FILE EXCEL
# ================================================
def load_all_sheets(file):
    try:
        xls = pd.ExcelFile(file)
        sheet_dfs = []

        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            df.columns = df.columns.str.strip()
            df["Nguồn sheet"] = sheet_name  # Gắn tên sheet vào dữ liệu
            sheet_dfs.append(df)

        df_all = pd.concat(sheet_dfs, ignore_index=True)
        return df_all
    except Exception as e:
        st.error(f"❌ Không thể đọc file Excel: {e}")
        return None

# ================================================
# 📊 BIỂU ĐỒ TỔNG GIỜ THEO DỰ ÁN
# ================================================
def plot_project_summary(df):
    col_project = "Mã dự án/Project"
    col_total_min = "Tổng thời gian gia công/Total machining time (min)"

    st.subheader("📊 Tổng thời gian gia công theo từng dự án")

    if col_project not in df.columns or col_total_min not in df.columns:
        st.warning("⚠️ Thiếu cột cần thiết.")
        return

    df_group = df.groupby(col_project)[col_total_min].sum().reset_index()

    fig = px.bar(
        df_group,
        x=col_project,
        y=col_total_min,
        text_auto=".2s",
        color=col_project,
        title="Tổng thời gian gia công theo từng dự án"
    )
    st.plotly_chart(fig, use_container_width=True)

# ================================================
# 📊 BIỂU ĐỒ THEO MÁY TRONG TỪNG DỰ ÁN
# ================================================
def plot_machine_per_project(df):
    col_project = "Mã dự án/Project"
    col_machine = "Machine/máy"
    col_total_min = "Tổng thời gian gia công/Total machining time (min)"

    if any(col not in df.columns for col in [col_project, col_machine, col_total_min]):
        st.warning("⚠️ Thiếu cột cần thiết.")
        return

    projects = df[col_project].dropna().unique()
    for proj in projects:
        st.markdown(f"### 📁 Dự án: `{proj}`")
        df_proj = df[df[col_project] == proj]

        df_group = df_proj.groupby(col_machine)[col_total_min].sum().reset_index()
        if df_group.empty:
            st.info("⛔ Không có dữ liệu máy cho dự án này.")
            continue

        fig = px.bar(
            df_group,
            x=col_machine,
            y=col_total_min,
            text_auto=".2s",
            color=col_machine,
            title=f"⏱️ Tổng thời gian theo máy - Dự án {proj}"
        )
        st.plotly_chart(fig, use_container_width=True)

# ================================================
# 🚀 APP CHÍNH
# ================================================
def main():
    st.set_page_config(page_title="📂 Machine Report by Sheet & Project", layout="wide")
    st.title("📄 Báo cáo thời gian gia công tổng hợp từ nhiều sheet")

    uploaded_file = st.file_uploader("📤 Tải lên file Excel (nhiều sheet)", type=["xlsx"])
    if uploaded_file:
        df = load_all_sheets(uploaded_file)

        if df is not None and not df.empty:
            st.success("✅ Đã đọc thành công toàn bộ dữ liệu!")

            # 💡 Loại bỏ cột Unnamed
            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

            # ➕ Tạo thêm cột "Thời gian (giờ)"
            time_col = "Tổng thời gian gia công/Total machining time (min)"
            if time_col in df.columns:
                df["Thời gian (giờ)/Total time (hr)"] = df[time_col] / 60
            else:
                st.warning("⚠️ Không tìm thấy cột thời gian (phút) để quy đổi sang giờ.")

            # 📋 Hiển thị bảng dữ liệu
            st.dataframe(df.head(20), use_container_width=True)

            # 📊 Biểu đồ tổng hợp theo dự án
            st.markdown("---")
            plot_project_summary(df)

            # 📊 Biểu đồ theo máy trong từng dự án
            st.markdown("---")
            plot_machine_per_project(df)
        else:
            st.warning("⚠️ File không có dữ liệu hợp lệ.")

# ================================================
# 🔁 CHẠY APP
# ================================================
if __name__ == "__main__":
    main()
