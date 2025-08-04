import streamlit as st
import pandas as pd
import plotly.express as px

# ================================================
# ✅ ĐỌC FILE EXCEL ĐÃ UPLOAD
# ================================================
def load_uploaded_excel(file):
    try:
        df = pd.read_excel(file)
        df.columns = df.columns.str.strip()  # Làm sạch tên cột
        return df
    except Exception as e:
        st.error(f"❌ Không thể đọc file Excel: {e}")
        return None

# ================================================
# 📊 BIỂU ĐỒ TỔNG GIỜ THEO DỰ ÁN
# ================================================
def plot_project_summary(df):
    st.subheader("📊 Tổng thời gian gia công theo từng dự án")

    col_project = "Mã dự án/Project"
    col_total_time = "Tổng thời gian gia công/Total machining time (min)"

    if col_project not in df.columns or col_total_time not in df.columns:
        st.warning("⚠️ Không tìm thấy cột cần thiết trong dữ liệu.")
        return

    df_group = df.groupby(col_project)[col_total_time].sum().reset_index()

    fig = px.bar(
        df_group,
        x=col_project,
        y=col_total_time,
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
    col_total_time = "Tổng thời gian gia công/Total machining time (min)"

    if any(col not in df.columns for col in [col_project, col_machine, col_total_time]):
        st.warning("⚠️ Không tìm thấy cột cần thiết trong dữ liệu.")
        return

    projects = df[col_project].dropna().unique()
    for proj in projects:
        st.markdown(f"### 📁 Dự án: `{proj}`")
        df_proj = df[df[col_project] == proj]

        df_group = df_proj.groupby(col_machine)[col_total_time].sum().reset_index()
        if df_group.empty:
            st.info("⛔ Không có dữ liệu máy cho dự án này.")
            continue

        fig = px.bar(
            df_group,
            x=col_machine,
            y=col_total_time,
            text_auto=".2s",
            color=col_machine,
            title=f"⏱️ Tổng thời gian theo máy - Dự án {proj}"
        )
        st.plotly_chart(fig, use_container_width=True)

# ================================================
# 🚀 APP CHÍNH
# ================================================
def main():
    st.set_page_config(page_title="📂 Machine Report per Project", layout="wide")
    st.title("📄 Báo cáo thời gian gia công theo Dự Án & Máy")

    uploaded_file = st.file_uploader("📤 Tải lên file Excel", type=["xlsx"])
    if uploaded_file:
        df = load_uploaded_excel(uploaded_file)

        if df is not None and not df.empty:
            st.success("✅ Đã đọc file thành công!")
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
