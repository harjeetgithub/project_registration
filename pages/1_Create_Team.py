import streamlit as st
import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from database import log_page_visit
MAX_TEAM_MEMBERS=2
# -----------------------------
# 🔐 Login Protection
# -----------------------------
if "user_email" not in st.session_state or not st.session_state.user_email:
    st.warning("Please login first.")
    st.switch_page("app.py")

# -----------------------------
# 🔹 Supabase Setup
# -----------------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

log_page_visit(st.session_state.user_email, "Create Team Page")
st.title("📝 Create Project Team")

# -----------------------------
# 1️⃣ Fetch distinct groups dynamically
# -----------------------------
def get_groups():
    response = supabase.table("students").select("group_name").execute()
    data = response.data
    groups = list(set([row["group_name"] for row in data]))
    return sorted(groups)

groups = get_groups()

if not groups:
    st.warning("No groups found in database.")
else:
    group = st.selectbox("Select Group", groups)

    # -----------------------------
    # 2️⃣ Get available students
    # -----------------------------
    def get_available_students(group_name):

        # All students in this group
        students_response = (
            supabase.table("students")
            .select("roll_no, student_name")
            .eq("group_name", group_name)
            .execute()
        )

        students = students_response.data

        # Already assigned leaders
        teams_response = (
            supabase.table("teams")
            .select("leader_roll, member_rolls")
            .eq("group_name", group_name)
            .execute()
        )

        assigned_rolls = []

        for team in teams_response.data:
            assigned_rolls.append(team["leader_roll"])
            if team["member_rolls"]:
                try:
                    assigned_rolls.extend(json.loads(team["member_rolls"]))
                except:
                    pass

        available = []
        for s in students:
            if s["roll_no"] not in assigned_rolls:
                available.append(f"{s['roll_no']} - {s['student_name']}")

        return available

    available_students = get_available_students(group)

    if not available_students:
        st.warning("All students already assigned.")
    else:
        st.write("No. of Students:", len(available_students))

        leader = st.selectbox("Select Team Leader", available_students)

        remaining = [s for s in available_students if s != leader]

        members = st.multiselect(
            "Select Team Members (Max allowed)",
            remaining,
            max_selections=MAX_TEAM_MEMBERS
        )

        project_title = st.text_input("Enter Proposed Project Title")

        # -----------------------------
        # 3️⃣ Save Team
        # -----------------------------
        def save_team(group_name, leader_roll, members_roll, project_title):

            # Check if leader already exists
            check = (
                supabase.table("teams")
                .select("id")
                .eq("leader_roll", leader_roll)
                .execute()
            )

            if check.data:
                return False

            insert_response = (
                supabase.table("teams")
                .insert({
                    "group_name": group_name,
                    "leader_roll": leader_roll,
                    "member_rolls": json.dumps(members_roll),
                    "project_title": project_title
                })
                .execute()
            )

            return True

        if st.button("Create Team"):
            if len(members) == 0:
                st.error("Select at least one member")
            elif not project_title.strip():
                st.error("Project Title is required")
            else:
                leader_roll = leader.split(" - ")[0]
                members_roll = [m.split(" - ")[0] for m in members]

                success = save_team(group, leader_roll, members_roll, project_title)

                if success:
                    st.success("Team Created Successfully!")
                    st.rerun()
                else:
                    st.error("This leader already has a team!")
# import streamlit as st
# from config import MAX_TEAM_MEMBERS
# from database import get_connection, create_table, save_team, get_available_students  # We'll define this function






# if "user_email" not in st.session_state or not st.session_state.user_email:
#     st.warning("Please login first.")
#     st.switch_page("app.py")


# create_table()

# st.title("📝 Create Project Team")

# # -----------------------------
# # 1️⃣ Fetch distinct groups dynamically from the database
# # -----------------------------
# import sqlite3
# DB_PATH = "data/teams.db"  # adjust your path if needed

# def get_groups():
#     conn = get_connection()
#     c = conn.cursor()
#     c.execute("SELECT DISTINCT group_name FROM students")
#     groups = [row[0] for row in c.fetchall()]
#     conn.close()
#     return groups

# groups = get_groups()

# if not groups:
#     st.warning("No groups found in database.")
# else:
#     group = st.selectbox("Select Group", groups)

    

#     available_students = get_available_students(group)
#     #st.write("Assigned Data: ",available_students)
#     if not available_students:
#         st.warning("All students already assigned.")
#     else:
#         st.write("No. of Students:", len(available_students))
#         leader = st.selectbox("Select Team Leader", available_students)
        
#         remaining = [s for s in available_students if s != leader]

#         members = st.multiselect(
#             "Select Team Members: (Max 2 allowed)",
#             remaining,
#             max_selections=MAX_TEAM_MEMBERS
#         )
#         project_title = st.text_input("Enter Proposed Project Title")
#         if st.button("Create Team"):
#             if len(members) == 0:
#                 st.error("Select at least one member")
#             elif not project_title.strip():
#                 st.error("Project Title is required")
#             else:
#                 leader_roll = leader.split(" - ")[0]
#                 members_roll = [m.split(" - ")[0] for m in members]

#                 success = save_team(group, leader_roll, members_roll, project_title)

#                 if success:
#                     st.success("Team Created Successfully!")
#                     st.rerun()
#                 else:
#                     st.error("This leader already has a team!")
        