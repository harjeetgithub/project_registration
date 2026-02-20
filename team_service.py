from config import STUDENTS_PER_GROUP
from database import get_used_students

def generate_students(group):
    return [f"{group}-R{str(i).zfill(2)}" for i in range(1, STUDENTS_PER_GROUP + 1)]

def get_available_students(group):
    all_students = generate_students(group)
    used = get_used_students(group)
    return [s for s in all_students if s not in used]