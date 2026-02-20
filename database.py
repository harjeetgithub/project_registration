import sqlite3
import json, datetime
import pandas as pd
from config import DB_PATH

# def get_connection():
#     return sqlite3.connect(DB_PATH)
def get_connection():
    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,              # wait 30 sec if locked
        check_same_thread=False  # allow multi-thread access
    )
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def create_table():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
              CREATE TABLE IF NOT EXISTS teams (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              group_name TEXT,
              leader_roll TEXT UNIQUE,
              member_rolls TEXT,
              project_title TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              UNIQUE(group_name, leader_roll)
              )
    """)
    # Create indexes for faster queries
    c.execute("CREATE INDEX IF NOT EXISTS idx_teams_group ON teams(group_name);")

    conn.commit()
    conn.close()

def save_team(group, leader, members):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO project_teams (group_name, leader_roll, member_rolls) VALUES (?, ?, ?)",
        (group, leader, ",".join(members))
    )
    conn.commit()
    conn.close()

def get_teams(group=None):
    conn = get_connection()
    c = conn.cursor()

    if group:
        c.execute("SELECT * FROM project_teams WHERE group_name=?", (group,))
    else:
        c.execute("SELECT * FROM project_teams")

    rows = c.fetchall()
    conn.close()
    return rows

def get_used_students(group):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT leader_roll, member_rolls FROM project_teams WHERE group_name=?", (group,))
    rows = c.fetchall()
    conn.close()

    used = []
    for leader, members in rows:
        used.append(leader)
        if members:
            used.extend(members.split(","))
    return used

def create_student_table():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT,
            student_name TEXT,
            father_name TEXT,
            student_email TEXT,
            group_name TEXT,
            gender TEXT,
            father_mobile TEXT,
            student_mobile TEXT,
            mode_new TEXT,
            UNIQUE(roll_no, group_name)
        )
    """)
    # Create indexes for faster queries
    c.execute("CREATE INDEX IF NOT EXISTS idx_students_group ON students(group_name);")
    
    conn.commit()
    conn.close()


def insert_students_bulk(dataframe):
    conn = get_connection()
    c = conn.cursor()

    inserted_count = 0
    skipped_count = 0

    for _, row in dataframe.iterrows():
        try:
            c.execute("""
                INSERT INTO students (
                    roll_no, student_name, father_name,
                    student_email, group_name, gender,
                    father_mobile, student_mobile, mode_new
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(row["RollNo"]).strip(),
                row["StudentName"],
                row["FatherName"],
                row["StudentEmail"],
                row["GroupName"],
                row["Gender"],
                str(row["FatherMobileNo"]),
                str(row["StudentMobile"]),
                row["ModeNew"]
            ))

            inserted_count += 1   # Count successful insert

        except sqlite3.IntegrityError:
            skipped_count += 1    # Duplicate (primary key conflict)

    conn.commit()
    conn.close()

    return inserted_count, skipped_count


#DB_NAME = "database.db"

# -----------------------------
# Get All Students
# -----------------------------
def get_all_students():
    conn = get_connection()
    query = "SELECT * FROM students"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# -----------------------------
# Get Students Group Wise
# -----------------------------
def get_students_by_group(group_name):
    conn = get_connection()
    query = "SELECT * FROM students WHERE group_name = ?"
    df = pd.read_sql_query(query, conn, params=(group_name,))
    conn.close()
    return df

def show_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return tables

def count_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]
    conn.close()
    return count



# -----------------------------
# 1️⃣ Function: Save a team
# -----------------------------
def save_team(group_name, leader_roll, members_roll, project_title):
    """
    Save a new team into the SQLite database safely, handling parallel submissions.

    Returns True if team saved successfully,
    Returns False if leader already exists or DB is locked.
    """

    conn = get_connection()  # Make sure get_connection() uses timeout & check_same_thread=False
    c = conn.cursor()

    # Clean input
    group_name = group_name.strip()
    leader_roll = leader_roll.strip()
    project_title = project_title.strip()
    members_roll = [m.strip() for m in members_roll]

    members_json = json.dumps(members_roll)
    created_at = datetime.datetime.now()

    try:
        # Check if leader already exists in teams
        c.execute("SELECT 1 FROM teams WHERE leader_roll = ?", (leader_roll,))
        if c.fetchone():
            return False  # Duplicate leader

        # Insert new team
        c.execute("""
            INSERT INTO teams (group_name, leader_roll, member_rolls, project_title, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (group_name, leader_roll, members_json, project_title, created_at))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        # Handles UNIQUE constraint violations (e.g., duplicate leader)
        return False

    except sqlite3.OperationalError as e:
        # Handles database locks in concurrent submissions
        if "locked" in str(e):
            return False
        else:
            raise

    finally:
        c.close()
        conn.close()
# def save_team(group_name, leader_roll, members_roll, project_title):
#     conn = get_connection()
#     c = conn.cursor()
#     # Check if leader already exists
#     c.execute("SELECT 1 FROM teams WHERE leader_roll = ?", (leader_roll,))
#     if c.fetchone():
#         conn.close()
#         return False  # duplicate leader

#     members_json = json.dumps(members_roll)
#     created_at = datetime.datetime.now()

#     c.execute("""
#         INSERT INTO teams (group_name, leader_roll, member_rolls, project_title, created_at)
#         VALUES (?, ?, ?, ?, ?)
#     """, (group_name, leader_roll, members_json, project_title, created_at))

#     conn.commit()
#     conn.close()

#     return True
# -----------------------------
# 2️⃣ Function: Get students group-wise
# -----------------------------
def get_students_groupwise(group_name=None):
    """
    Fetch students from 'students' table.
    If group_name is provided, return students of that group.
    Returns a list of dictionaries: [{'roll_no': ..., 'student_name': ...}, ...]
    """
    conn = get_connection()
    c = conn.cursor()
    
    if group_name:
        c.execute("""
            SELECT roll_no, student_name
            FROM students
            WHERE group_name = ?
            ORDER BY student_name
        """, (group_name,))
    else:
        c.execute("""
            SELECT roll_no, student_name, group_name
            FROM students
            ORDER BY group_name, student_name
        """)
    
    rows = c.fetchall()
    conn.close()
    
    # Convert to list of dicts
    if group_name:
        return [{'roll_no': r[0], 'student_name': r[1]} for r in rows]
    else:
        return [{'roll_no': r[0], 'student_name': r[1], 'group_name': r[2]} for r in rows]



def get_available_students(group_name):

    conn = get_connection()
    c = conn.cursor()

    # 1️⃣ Get all students of selected group
    c.execute("""
        SELECT roll_no, student_name 
        FROM students 
        WHERE group_name = ?
        ORDER BY student_name
    """, (group_name,))
    all_students = c.fetchall()

    # 2️⃣ Get already assigned students (leaders + members)
    c.execute("""
        SELECT leader_roll, member_rolls 
        FROM teams 
        WHERE group_name = ?
    """, (group_name,))
    assigned_data = c.fetchall()
    
    assigned_rolls = set()

    for leader_roll, members_json in assigned_data:
        assigned_rolls.add(str(leader_roll))

        if members_json:
            members = json.loads(members_json)
            assigned_rolls.update([str(m) for m in members])

    conn.close()

    # 3️⃣ Remove assigned students
    available_students = [
        f"{roll} - {name}"
        for roll, name in all_students
        if str(roll) not in assigned_rolls
    ]

    return available_students

