import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from database import log_page_visit
st.title("📂 Upload Student Excel Data")

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


log_page_visit(st.session_state.user_email, "Upload Student Excel Data")

# -----------------------------
# 📤 File Upload
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx"]
)

required_columns = [
    "RollNo",
    "StudentName",
    "FatherName",
    "StudentEmail",
    "GroupName",
    "Gender",
    "FatherMobileNo",
    "StudentMobile",
    "ModeNew"
]

# -----------------------------
# Process File
# -----------------------------
if uploaded_file is not None:

    df = pd.read_excel(uploaded_file)

    st.subheader("Preview Data")

    # Remove empty rows
    df = df.dropna(subset=["RollNo", "StudentName"])
    df = df.dropna(how="all")

    # Convert roll_no to string
    df["RollNo"] = df["RollNo"].apply(
        lambda x: str(int(x)) if pd.notna(x) else ""
    )

    df = df.reset_index(drop=True)

    st.dataframe(df)

    # -----------------------------
    # Validate Columns
    # -----------------------------
    if all(col in df.columns for col in required_columns):

        if st.button("Insert Records into Supabase"):

            records = []

            for _, row in df.iterrows():
                records.append({
                    "roll_no": row["RollNo"],
                    "student_name": row["StudentName"],
                    "father_name": row["FatherName"],
                    "student_email": row["StudentEmail"],
                    "group_name": row["GroupName"],
                    "gender": row["Gender"],
                    "father_mobile": str(row["FatherMobileNo"]),
                    "student_mobile": str(row["StudentMobile"]),
                    "mode_new": row["ModeNew"]
                })

            try:
                response = supabase.table("students").insert(records).execute()

                if response.data:
                    st.success("✅ Student records inserted successfully!")
                else:
                    st.warning("No data inserted.")

            except Exception as e:
                st.error(f"❌ Error inserting data: {e}")

    else:
        st.error("❌ Excel file format is incorrect!")
        st.write("Required Columns:")
        st.write(required_columns)
        
