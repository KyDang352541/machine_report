import streamlit as st 
import pandas as pd
import plotly.express as px

# === Đọc toàn bộ sheet và gộp vào một DataFrame
def load_all_data(file):
    try:
        xls = pd.ExcelFile(file)
        all_dfs = []

        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name, header=0)

            df.columns = df.columns.map(str).str.strip()
            df = df.loc[:, ~df.columns.map(str).str.contains("^Unnamed")]
            df["Loại máy"] = sheet_name

            # Chuyển định dạng ngày
            if "Ngày/Date" in df.columns:
                df["Ngày/Date"] = pd.to_datetime(df["Ngày/Date"], errors="coerce", dayfirst=True)

            # Sửa lỗi SL/Qty
            if "SL/Qty" in df.columns:
                df["SL/Qty"] = df["SL/Qty"].astype(str).str.extract(r"(\d+(?:\.\d+)?)")
                df["SL/Qty"] = pd.to_numeric(df["SL/Qty"], errors="coerce")

            # Thêm cột giờ
            col_min = "Tổng thời gian gia công/Total machining time (min)"
            if col_min in df.columns:
                df[col_min] = pd.to_numeric(df[col_min], errors="coerce")
                df["Thời gian (giờ)/Total time (hr)"] = df[col_min] / 60

            all_dfs.append(df)

        df_all = pd.concat(all_dfs, ignore_index=True)
        return df_all

    except Exception as e:
        st.error(f"❌ Không thể đọc file Excel: {e}")
        return pd.DataFrame()

# === BIỂU ĐỒ CỘT
def plot_bar(df, project_name, selected_machines):
    col_machine = "Machine/máy"
    col_min = "Tổng thời gian gia công/Total machining time (min)"

    df_group = (
        df[df[col_machine].isin(selected_machines)]
        .groupby(col_machine)[col_min]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        df_group,
        x=col_machine,
        y=col_min,
        text_auto=".2s",
        color=col_machine,
        title=f"📊 Tổng thời gian theo máy - Dự án {project_name}"
    )
    st.plotly_chart(fig, use_container_width=True)

# === BIỂU ĐỒ SUNBURST
def plot_sunburst(df, selected_machines):
    col_machine = "Machine/máy"
    col_desc = "Mô tả/Description"
    col_min = "Tổng thời gian gia công/Total machining time (min)"

    if any(col not in df.columns for col in [col_machine, col_desc, col_min]):
        st.warning("⚠️ Thiếu cột để vẽ biểu đồ phân cấp.")
        return

    df_sun = df[df[col_machine].isin(selected_machines)]

    fig = px.sunburst(
        df_sun,
        path=[col_machine, col_desc],
        values=col_min,
        title="🌀 Phân bổ thời gian theo Máy và Task"
    )
    st.plotly_chart(fig, use_container_width=True)

# === APP CHÍNH
def main():
    st.set_page_config(page_title="📂 Machine Report Viewer", layout="wide")
    st.title("📄 Báo cáo thời gian gia công toàn bộ máy và dự án")

    uploaded_file = st.file_uploader("📤 Tải lên file Excel", type=["xlsx"])
    if not uploaded_file:
        return

    df_all = load_all_data(uploaded_file)
    if df_all.empty:
        return

    col_project = "Mã dự án/Project"
    col_machine = "Machine/máy"

    if col_project not in df_all.columns or col_machine not in df_all.columns:
        st.error(f"❌ Thiếu cột '{col_project}' hoặc '{col_machine}'.")
        st.write("Cột hiện có:", df_all.columns.tolist())
        return

    available_projects = df_all[col_project].dropna().unique().tolist()
    selected_project = st.selectbox("📁 Chọn dự án", available_projects)

    df_project = df_all[df_all[col_project] == selected_project]

    available_machines = df_project[col_machine].dropna().unique().tolist()
    selected_machines = st.multiselect("🔧 Chọn máy cần xem", available_machines, default=available_machines)

    if not selected_machines:
        st.warning("⚠️ Vui lòng chọn ít nhất một máy.")
        return

    df_filtered = df_project[df_project[col_machine].isin(selected_machines)]

    # 📋 Hiển thị bảng
    st.markdown("### 📄 Dữ liệu chi tiết đã lọc")
    st.dataframe(df_filtered, use_container_width=True)

    # 📊 Biểu đồ
    st.markdown("### 📊 Tổng thời gian theo máy")
    plot_bar(df_filtered, selected_project, selected_machines)

    st.markdown("### 🌀 Phân bổ thời gian theo mô tả")
    plot_sunburst(df_filtered, selected_machines)

if __name__ == "__main__":
    main()
