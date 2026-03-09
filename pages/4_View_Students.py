import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from database import log_page_visit
st.title("📋 View Students Data")

# -----------------------------
# 🔹 Supabase Setup
# -----------------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



admin_email = "harjeet.singh@chitkara.edu.in"

if st.session_state.user_email != admin_email:
    st.error("You are not authorized to view this page")
    st.stop()



log_page_visit(st.session_state.user_email, "View Students Data")

# -----------------------------
# 📥 Load All Students
# -----------------------------
@st.cache_data
def load_students():
    response = supabase.table("students").select("*").execute()
    return pd.DataFrame(response.data)

df = load_students()

# -----------------------------
# Display Data
# -----------------------------
if df.empty:
    st.warning("No student records found!")
else:
    st.success(f"Total Students: {len(df)}")

    # -----------------------------
    # Group Filter
    # -----------------------------
    group_list = ["All"] + sorted(df["group_name"].dropna().unique().tolist())

    selected_group = st.selectbox(
        "Select Group",
        group_list,
        key="view_group"
    )

    if selected_group == "All":
        filtered_df = df
    else:
        filtered_df = df[df["group_name"] == selected_group]

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
        st.dataframe(filtered_df[selected_columns], use_container_width=True)
    else:
        st.warning("Please select at least one column")
