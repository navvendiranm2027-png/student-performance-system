"""Admin-only staff account creation and class monitoring."""
from datetime import datetime
from database import connect_db, ask_nonempty, ask_email, ask_password, hash_password
from staff import list_students, update_student_performance, choose_student
from analytics import monitor_all_students, show_student_report


def add_staff():
    """Create a staff login; only the admin menu calls this function."""
    print("\n=== ADD STAFF ACCOUNT ===")
    name = ask_nonempty("Staff full name: ")
    username = ask_nonempty("Staff username: ")
    email = ask_email()
    password = ask_password("Temporary password (minimum 8 characters): ")
    if len(password) < 8:
        print("Password must be at least 8 characters.")
        return
    with connect_db() as conn:
        try:
            conn.execute("""
                INSERT INTO users
                (role, username, name, email, password_hash, created_at)
                VALUES ('staff', ?, ?, ?, ?, ?)
            """, (
                username, name, email, hash_password(password),
                datetime.now().isoformat(timespec="seconds")
            ))
            print("Staff account created successfully.")
        except Exception as exc:
            if "UNIQUE constraint failed" in str(exc):
                print("Username or email already exists.")
                return
            raise


def admin_menu(user):
    """Admin dashboard for staff accounts and student monitoring."""
    while True:
        print("\n--- ADMIN MENU ---")
        print("1. Add staff account")
        print("2. List students")
        print("3. Add/update student performance")
        print("4. Monitor all student performance")
        print("5. View one student report")
        print("6. Logout")
        choice = input("Choose: ").strip()
        if choice == "1":
            add_staff()
        elif choice == "2":
            list_students()
        elif choice == "3":
            update_student_performance(user)
        elif choice == "4":
            monitor_all_students()
        elif choice == "5":
            student = choose_student()
            if student:
                show_student_report(student["id"])
        elif choice == "6":
            break
        else:
            print("Invalid choice.")
