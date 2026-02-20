import streamlit as st
from config import MAX_TEAM_MEMBERS
from database import get_connection, create_table, save_team, get_available_students  # We'll define this function

create_table()

st.title("📝 Create Project Team")

# -----------------------------
# 1️⃣ Fetch distinct groups dynamically from the database
# -----------------------------
import sqlite3
DB_PATH = "data/teams.db"  # adjust your path if needed

def get_groups():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT DISTINCT group_name FROM students")
    groups = [row[0] for row in c.fetchall()]
    conn.close()
    return groups

groups = get_groups()

if not groups:
    st.warning("No groups found in database.")
else:
    group = st.selectbox("Select Group", groups)

    

    available_students = get_available_students(group)
    #st.write("Assigned Data: ",available_students)
    if not available_students:
        st.warning("All students already assigned.")
    else:
        st.write("No. of Students:", len(available_students))
        leader = st.selectbox("Select Team Leader", available_students)
        
        remaining = [s for s in available_students if s != leader]

        members = st.multiselect(
            "Select Team Members: (Max 2 allowed)",
            remaining,
            max_selections=MAX_TEAM_MEMBERS
        )
        project_title = st.text_input("Enter Proposed Project Title")
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
        