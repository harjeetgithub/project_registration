import streamlit as st
import pandas as pd
import json
from database import create_table,get_connection  # path to your database

st.title("View Teams")

# -----------------------------
# 1️⃣ Fetch distinct groups dynamically
# -----------------------------
def get_groups():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT group_name FROM students")
    groups = [row[0] for row in c.fetchall()]
    conn.close()
    return groups

groups = get_groups()
group = st.selectbox("Filter by Group", ["All"] + groups)

# -----------------------------
# 2️⃣ Fetch teams
# -----------------------------
def get_teams(group_name=None):
    """
    Fetch teams from database. 
    If group_name is provided, filter by that group.
    Returns list of dicts with keys: id, group_name, leader_roll, member_rolls, created_at
    """
    create_table()
    conn = get_connection()
    c = conn.cursor()
    
    
    
    if group_name and group_name != "All":
        c.execute("SELECT id, group_name, leader_roll, member_rolls, project_title, created_at FROM teams WHERE group_name = ?", (group_name,))
    else:
        c.execute("SELECT id, group_name, leader_roll, member_rolls, project_title, created_at FROM teams")
    
    rows = c.fetchall()
    conn.close()
    
    # Convert member_rolls from JSON to string
    teams = []
    for r in rows:
        members = json.loads(r[3])  # convert JSON string back to list
        members_str = ", ".join(members)
        teams.append({
            "ID": r[0],
            "Group": r[1],
            "Leader": r[2],
            "Members": members_str,
            "Created At": r[4]
        })
    return teams

# -----------------------------
# 3️⃣ Display in Streamlit
# -----------------------------
data = get_teams(group)
df = pd.DataFrame(data)
st.dataframe(df)





ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]


st.markdown("---")
st.subheader("🔐 Admin Authentication")

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

admin_password_input = st.text_input("Enter Admin Password", type="password")

if st.button("Login as Admin"):
    if admin_password_input == ADMIN_PASSWORD:
        st.session_state.admin_authenticated = True
        st.success("✅ Admin access granted")
    else:
        st.error("❌ Incorrect password")
# -----------------------------
# 4️⃣ Delete Team
# -----------------------------
if st.session_state.admin_authenticated:

    st.markdown("---")
    st.subheader("🗑️ Delete Team")

    def delete_team(team_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM teams WHERE id = ?", (team_id,))
        conn.commit()
        conn.close()

    if not df.empty:

        display_options = [
            f"ID {row['ID']} - Leader: {row['Leader']} ({row['Group']})"
            for _, row in df.iterrows()
        ]

        selected_display = st.selectbox("Select Team to Delete", display_options)
        selected_team_id = int(selected_display.split(" - ")[0].replace("ID ", ""))

        selected_row = df[df["ID"] == selected_team_id].iloc[0]
        st.write("Group:", selected_row["Group"])
        st.write("Leader:", selected_row["Leader"])
        st.write("Members:", selected_row["Members"])

        confirm = st.checkbox("⚠️ Confirm deletion")

        if st.button("Delete Team"):
            if confirm:
                delete_team(selected_team_id)
                st.success("✅ Team deleted successfully!")
                st.rerun()
            else:
                st.warning("Please confirm deletion.")

else:
    st.warning("🔒 Admin login required to delete teams.")




import io
from openpyxl import Workbook

if st.session_state.admin_authenticated:

    st.markdown("---")
    st.subheader("📥 Download Teams Data")

    def generate_excel(df):
        wb = Workbook()
        ws = wb.active
        ws.title = "Teams Data"

        ws.append(df.columns.tolist())

        for _, row in df.iterrows():
            ws.append(row.tolist())

        file_buffer = io.BytesIO()
        wb.save(file_buffer)
        file_buffer.seek(0)
        return file_buffer

    if not df.empty:
        excel_file = generate_excel(df)

        st.download_button(
            label="Download Teams Data as Excel",
            data=excel_file,
            file_name="All_Teams_Data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("🔒 Admin login required to download data.")