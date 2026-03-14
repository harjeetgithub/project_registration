import streamlit as st
import pandas as pd
import json
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import io
from openpyxl import Workbook
from database import log_page_visit

# -----------------------------
# 🔹 Supabase Setup
# -----------------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# login protection
if "user_email" not in st.session_state or st.session_state.user_email is None:
    st.warning("Please login first")
    st.switch_page("app.py")
    st.stop()

# log page visit
log_page_visit(st.session_state.user_email, "View Teams")

st.title("View Teams")


# -----------------------------
# Deadline Date
# -----------------------------
deadline = pd.to_datetime("2026-03-15")   # change date as required

# -----------------------------
# 1️⃣ Fetch distinct groups dynamically
# -----------------------------
def get_groups():
    response = supabase.table("students").select("group_name").execute()
    data = response.data

    groups = list(set([row["group_name"] for row in data]))
    return sorted(groups)

groups = get_groups()
group = st.selectbox("Filter by Group", ["All"] + groups)

# -----------------------------
# 2️⃣ Fetch Teams
# -----------------------------
def get_teams(group_name=None):

    if group_name and group_name != "All":
        response = (
            supabase.table("teams")
            .select("*")
            .eq("group_name", group_name)
            .order("created_at", desc=True)
            .execute()
        )
    else:
        response = (
            supabase.table("teams")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

    rows = response.data

    teams = []
    for r in rows:
        try:
            members = json.loads(r["member_rolls"]) if r["member_rolls"] else []
        except:
            members = []

        members_str = ", ".join(members)

        teams.append({
            "ID": r["id"],
            "Group": r["group_name"],
            "Leader": r["leader_roll"],
            "Members": members_str,
            "Project Title": r.get("project_title", ""),
            "Created At": r["created_at"]
        })

    return teams

# -----------------------------
# 3️⃣ Display
# -----------------------------
data = get_teams(group)
df = pd.DataFrame(data)
df["Created At"] = pd.to_datetime(df["Created At"])
# highlight function
# function to style only the column
def highlight_created_at(val):
    if val > deadline:
        return 'color: red'      # late submission
    else:
        return 'color: green'    # on-time submission
# st.dataframe(df)
styled_df = df.style.applymap(highlight_created_at, subset=["Created At"])
st.dataframe(styled_df, use_container_width=True)
# -----------------------------
# 🔐 Admin Authentication
# -----------------------------
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
# 4️⃣ Delete Team (Supabase Version)
# -----------------------------
if st.session_state.admin_authenticated:

    st.markdown("---")
    st.subheader("🗑️ Delete Team")

    def delete_team(team_id):
        supabase.table("teams").delete().eq("id", team_id).execute()

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

# -----------------------------
# 5️⃣ Download Excel
# -----------------------------
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
    

