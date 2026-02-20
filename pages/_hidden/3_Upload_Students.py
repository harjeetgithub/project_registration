import streamlit as st
import pandas as pd
from database import create_student_table, insert_students_bulk

st.title("📂 Upload Student Excel Data")

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

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.subheader("Preview Data")
    # Keep only rows where 'roll_no' and 'student_name' are not empty
    df = df.dropna(subset=["RollNo","StudentName"])

    # Optional: remove rows where all columns are empty
    df = df.dropna(how="all")

    # Convert roll_no to string (removes .0)
    df["RollNo"] = df["RollNo"].apply(lambda x: str(int(x)) if pd.notna(x) else "")
    # Reset index
    df = df.reset_index(drop=True)
    st.dataframe(df)

    # Validate Columns
    if all(col in df.columns for col in required_columns):

        if st.button("Create Table & Insert Records"):
            create_student_table()
            insert_students_bulk(df)
            st.success("✅ Student records inserted successfully!")

    else:
        st.error("❌ Excel file format is incorrect!")
        st.write("Required Columns:")
        st.write(required_columns)