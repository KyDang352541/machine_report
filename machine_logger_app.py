import streamlit as st 
import pandas as pd
import plotly.express as px

def load_all_sheets(file):
    try:
        xls = pd.ExcelFile(file)
        sheet_data = {}

        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)

            df.columns = df.columns.map(str).str.strip()
            df = df.loc[:, ~df.columns.map(str).str.contains("^Unnamed")]
            df["Loại máy"] = sheet_name

            if "Ngày/Date" in df.columns:
                df["Ngày/Date"] = pd.to_datetime(df["Ngày/Date"], errors="coerce", dayfirst=True)

            if "SL/Qty" in df.columns:
                df["SL/Qty"] = df["SL/Qty"].astype(str).str.extract(r"(\d+(?:\.\d+)?)")
                df["SL/Qty"] = pd.to_numeric(df["SL/Qty"], errors="coerce")

            col_min = "Tổng thời gian gia công/Total machining time (min)"
            if col_min in df.columns:
                df[col_min] = pd.to_numeric(df[col_min], errors="coerce")
                df["Thời gian (giờ)/Total time (hr)"] = df[col_min] / 60

            sheet_data[sheet_name] = df

        return sheet_data

    except Exception as e:
        st.error(f"❌ Không thể đọc file Excel: {e}")
        return {}

# === BIỂU ĐỒ CỘT: GIỜ THEO MÁY
def plot_machine_bar_chart(df, project_name, selected_machines):
    col_machine = "Machine/máy"
    col_total_min = "Tổng thời gian gia công/Total machining time (min)"

    df_group = (
        df[df[col_machine].isin(selected_machines)]
        .groupby(col_machine)[col_total_min]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        df_group,
        x=col_machine,
        y=col_total_min,
        text_auto=".2s",
        color=col_machine,
        title=f"📊 Tổng thời gian theo máy - Dự án {project_name}"
    )
    st.plotly_chart(fig, use_container_width=True)

# === BIỂU ĐỒ PHÂN CẤP: GIỜ THEO TASK/MÁY
def plot_sunburst(df, selected_machines):
    col_machine = "Machine/máy"
    col_desc = "Mô tả/Description"
    col_total_min = "Tổng thời gian gia công/Total machining time (min)"

    if any(col not in df.columns for col in [col_machine, col_desc, col_total_min]):
        st.warning("⚠️ Thiếu cột để vẽ biểu đồ phân cấp.")
        return

    df_sun = df[df[col_machine].isin(selected_machines)]

    fig = px.sunburst(
        df_sun,
        path=[col_machine, col_desc],
        values=col_total_min,
        title="🌀 Phân bổ thời gian theo Máy và Task"
    )
    st.plotly_chart(fig, use_container_width=True)

# === APP CHÍNH
def main():
    st.set_page_config(page_title="📂 Machine Report Viewer", layout="wide")
    st.title("📄 Báo cáo thời gian gia công theo Loại Máy & Dự Án")

    uploaded_file = st.file_uploader("📤 Tải lên file Excel", type=["xlsx"])
    if not uploaded_file:
        return

    sheet_data = load_all_sheets(uploaded_file)
    if not sheet_data:
        return

    machine_types = list(sheet_data.keys())
    selected_machine = st.selectbox("🛠️ Chọn loại máy (sheet)", machine_types)

    df = sheet_data[selected_machine]
    col_project = "Mã dự án/Project"

    if col_project not in df.columns:
        st.error(f"❌ Không tìm thấy cột '{col_project}'.")
        st.write("Cột hiện có:", df.columns.tolist())
        return

    available_projects = df[col_project].dropna().unique().tolist()
    selected_project = st.selectbox("📁 Chọn dự án", available_projects)

    df_project = df[df[col_project] == selected_project]

    # Chọn nhiều máy
    col_machine = "Machine/máy"
    if col_machine not in df_project.columns:
        st.error(f"❌ Không tìm thấy cột '{col_machine}'.")
        return

    available_machines = df_project[col_machine].dropna().unique().tolist()
    selected_machines = st.multiselect("🔧 Chọn máy cần xem", available_machines, default=available_machines)

    if not selected_machines:
        st.warning("⚠️ Vui lòng chọn ít nhất một máy.")
        return

    df_filtered = df_project[df_project[col_machine].isin(selected_machines)]

    # Hiển thị bảng dữ liệu
    st.markdown("### 📄 Dữ liệu chi tiết đã lọc")
    st.dataframe(df_filtered, use_container_width=True)

    # Biểu đồ cột tổng giờ theo máy
    st.markdown("### 📊 Tổng thời gian theo máy")
    plot_machine_bar_chart(df_filtered, selected_project, selected_machines)

    # Biểu đồ phân cấp theo máy và task
    st.markdown("### 🌀 Phân bổ thời gian theo mô tả")
    plot_sunburst(df_filtered, selected_machines)

if __name__ == "__main__":
    main()
