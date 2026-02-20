import streamlit as st
from database import get_all_students, get_students_by_group

st.title("📋 View Students Data")

# -----------------------------
# Load Data
# -----------------------------
df = get_all_students()
#print("All column: ",df.columns.tolist())
if df.empty:
    st.warning("No student records found!")
else:
    st.success(f"Total Students: {len(df)}")

    # -----------------------------
    # Group Filter
    # -----------------------------
    group_list = ["All"] + sorted(df["group_name"].unique().tolist())

    selected_group = st.selectbox(
        "Select Group",
        group_list,
        key="view_group"
    )

    if selected_group == "All":
        filtered_df = df
    else:
        filtered_df = get_students_by_group(selected_group)

    # -----------------------------
    # Column Selection
    # -----------------------------
    selected_columns = st.multiselect(
        "Select Columns to Display",
        df.columns.tolist(),
        default=df.columns.tolist(),
        key="view_columns"
    )

    if selected_columns:
        st.dataframe(filtered_df[selected_columns])
    else:
        st.warning("Please select at least one column")