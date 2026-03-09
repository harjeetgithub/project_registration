import json
from supabase_client import supabase

def save_team(group_name, leader_roll, members_roll, project_title):

    data = {
        "group_name": group_name.strip(),
        "leader_roll": leader_roll.strip(),
        "member_rolls": members_roll,  # JSON automatically
        "project_title": project_title.strip()
    }

    response = supabase.table("teams").insert(data).execute()

    if response.data:
        return True
    return False
def get_teams(group_name=None):
    query = supabase.table("teams").select("*")

    if group_name:
        query = query.eq("group_name", group_name)

    response = query.execute()
    return response.data
def insert_students_bulk(df):

    records = df.to_dict(orient="records")

    response = supabase.table("students").insert(records).execute()

    return len(response.data)
def get_all_students():
    response = supabase.table("students").select("*").execute()
    return response.data
# -----------------------------
# Log Page Visit
# -----------------------------
def log_page_visit(email, page):
    try:
        supabase.table("page_visits").insert({
            "email": email,
            "page_name": page
        }).execute()
    except Exception as e:
        print("Page visit logging failed:", e)
