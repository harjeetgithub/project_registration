import streamlit as st
import pandas as pd
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



st.markdown(
    """
    <marquee style="
        color:red;
        font-size:20px;
        font-weight:bold;
    ">
    ⚠️ Last Date for Project Registration: 14 March 2026 (11:59 PM). Late submissions will be marked automatically.
    </marquee>
    """,
    unsafe_allow_html=True
)



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


# # -----------------------------
# # 📌 Display Project Ideas
# # -----------------------------
# import pandas as pd

# st.divider()
# import streamlit as st
# import pandas as pd
# from supabase import create_client
# import os
# from dotenv import load_dotenv

# # -----------------------------
# # Supabase Connection
# # -----------------------------
# load_dotenv()

# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# # -----------------------------
# # Upload CSV UI
# # -----------------------------
# st.subheader("📂 Upload Project Ideas CSV")

# uploaded_file = st.file_uploader(
#     "Upload CSV File",
#     type=["csv"]
# )

# # -----------------------------
# # Insert Function
# # -----------------------------
# def insert_project_ideas(df):

#     # Replace NaN with None (important for JSON)
#     df = df.where(pd.notnull(df), None)

#     records = df.to_dict(orient="records")

#     response = supabase.table("project_ideas").insert(records).execute()

#     return response


# # -----------------------------
# # Process File
# # -----------------------------
# if uploaded_file is not None:

#     df = pd.read_csv(uploaded_file)

#     st.write("Preview of CSV Data")
#     st.dataframe(df)

#     if st.button("Insert All Records"):

#         try:

#             # Rename columns to match database
#             df.columns = [
#                 "domain",
#                 "project_title",
#                 "problem_definition",
#                 "dataset_features",
#                 "methodology",
#                 "target_applications"
#             ]

#             response = insert_project_ideas(df)

#             st.success(f"✅ {len(df)} records inserted successfully!")

#         except Exception as e:
#             st.error(f"Error inserting data: {e}")



st.title("📂 Project Ideas Repository")
st.markdown(
    """
    **📌 Note for Students Regarding Project Ideas**

    The project ideas listed in the repository are meant to **guide and inspire you** in selecting a project for your team. 
    You are encouraged to **take an idea from the list and adapt it** to propose a **real-world novel problem**.

    **Important Guidelines:**
    1. You **cannot use the project title exactly as it appears** in the repository.
    2. You should **modify, extend, or apply the idea** to a new context or problem.
    3. The goal is to demonstrate **originality, creativity, and problem-solving** in your project proposal.
    4. Make sure your **project objectives, methodology, and applications** reflect your unique approach.

    Following these guidelines ensures that your project is **authentic, innovative, and aligned with academic integrity**.  
    Please read the project ideas carefully, discuss with your team, and submit a **novel and well-defined project title**.
    """,
    unsafe_allow_html=True
)

st.divider()
# -----------------------------
# Fetch Data Function
# -----------------------------
def fetch_project_ideas():
    
    response = supabase.table("project_ideas").select("*").order("domain").execute()
    
    if response.data:
        return pd.DataFrame(response.data)
    else:
        return pd.DataFrame()


# -----------------------------
# Display Data
# -----------------------------
if st.button("Load Project Ideas"):

    df = fetch_project_ideas()

    if df.empty:
        st.warning("No project ideas found in database.")
    else:
        st.success(f"{len(df)} Project Ideas Found")

        st.dataframe(
            df[
                [
                    "domain",
                    "project_title",
                    "problem_definition",
                    "dataset_features",
                    "methodology",
                    "target_applications",
                ]
            ],
            use_container_width=True
        )