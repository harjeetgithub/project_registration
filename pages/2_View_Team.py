import streamlit as st
import pandas as pd
import sqlite3
import json
from database import get_connection  # path to your database

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
    conn = get_connection()
    c = conn.cursor()
    
    # Make sure teams table exists
    c.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL,
            leader_roll TEXT NOT NULL,
            member_rolls TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
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


# -----------------------------
# 4️⃣ Delete Team
# -----------------------------
st.markdown("---")
st.subheader("🗑️ Delete Team")


ADMIN_PASSWORD = "admin@123" 

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

    # Show selected team details
    selected_row = df[df["ID"] == selected_team_id].iloc[0]
    st.markdown("### 🔍 Selected Team Details")
    st.write("Group:", selected_row["Group"])
    st.write("Leader:", selected_row["Leader"])
    st.write("Members:", selected_row["Members"])

    st.markdown("### 🔐 Enter Admin Password to Enable Delete")
    password_input = st.text_input("Password", type="password")

    confirm = st.checkbox("⚠️ Confirm deletion")

    if st.button("Delete Team"):
        if password_input != ADMIN_PASSWORD:
            st.error("❌ Incorrect password! Delete not allowed.")
        elif not confirm:
            st.warning("Please confirm deletion first.")
        else:
            delete_team(selected_team_id)
            st.success(f"✅ Team ID {selected_team_id} deleted successfully!")
            st.rerun()

else:
    st.info("No teams available to delete.")