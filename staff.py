"""Staff functions for viewing students and entering performance data."""
from datetime import datetime
from database import connect_db, ask_nonempty, ask_number
from analytics import show_student_report


def list_students():
    """Display all student IDs, register numbers, names, and emails."""
    with connect_db() as conn:
        rows = conn.execute("""
            SELECT id, register_no, name, email FROM users
            WHERE role='student' ORDER BY register_no
        """).fetchall()
    if not rows:
        print("No students registered yet.")
        return []
    print("\nRegistered students:")
    for row in rows:
        print(f"ID {row['id']} | {row['register_no']} | {row['name']} | {row['email']}")
    return rows


def choose_student():
    """Find a student using database ID or register number."""
    if not list_students():
        return None
    identifier = ask_nonempty("Enter student database ID or register number: ").lower()
    with connect_db() as conn:
        return conn.execute("""
            SELECT id, register_no, name FROM users
            WHERE role='student'
              AND (CAST(id AS TEXT)=? OR lower(register_no)=?)
        """, (identifier, identifier)).fetchone()


def update_student_performance(staff_user):
    """Add/update marks, attendance, arrears, achievements, quiz points, remarks."""
    student = choose_student()
    if not student:
        print("Student not found.")
        return
    print(f"\nUpdating performance for {student['name']}")
    marks = ask_number("Exam marks earned: ", 0)
    max_marks = ask_number("Exam maximum marks: ", 1)
    if marks > max_marks:
        print("Marks cannot exceed maximum marks.")
        return
    attendance = ask_number("Attendance percentage (0-100): ", 0, 100)
    slip = ask_number("Slip-test marks (0-100): ", 0, 100)
    internal = ask_number("Internal marks (0-100): ", 0, 100)
    assignment = ask_number("Assignment marks (0-100): ", 0, 100)
    arrears = ask_number("Number of arrears: ", 0, integer=True)
    quiz_points = ask_number("Quiz points: ", 0)
    achievement = input("Achievement (Enter if none): ").strip()
    remarks = input("Staff remarks: ").strip()
    with connect_db() as conn:
        conn.execute("""
            UPDATE performance SET marks=?, max_marks=?, attendance=?,
                slip_test=?, internal_mark=?, assignment_mark=?, arrears=?,
                quiz_points=?, achievement=?, remarks=?, updated_by=?, updated_at=?
            WHERE student_id=?
        """, (
            marks, max_marks, attendance, slip, internal, assignment, arrears,
            quiz_points, achievement, remarks, staff_user["id"],
            datetime.now().isoformat(timespec="seconds"), student["id"]
        ))
    print("Student performance updated successfully.")


def staff_menu(user):
    """Staff dashboard."""
    while True:
        print("\n--- STAFF MENU ---")
        print("1. List students")
        print("2. Add/update student performance")
        print("3. View a student's report")
        print("4. Logout")
        choice = input("Choose: ").strip()
        if choice == "1":
            list_students()
        elif choice == "2":
            update_student_performance(user)
        elif choice == "3":
            student = choose_student()
            if student:
                show_student_report(student["id"])
        elif choice == "4":
            break
        else:
            print("Invalid choice.")
