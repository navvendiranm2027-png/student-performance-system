"""Student registration and student dashboard."""
from datetime import datetime
from database import connect_db, ask_nonempty, ask_email, ask_password, ask_date, hash_password
from analytics import show_student_report


def register_student():
    """Register a student without requiring an existing account."""
    print("\n=== STUDENT REGISTRATION ===")
    name = ask_nonempty("Full name: ")
    email = ask_email()
    dob = ask_date()
    phone = ask_nonempty("Phone number: ")
    while True:
        password = ask_password("Create password (minimum 8 characters): ")
        if len(password) < 8:
            print("Password must contain at least 8 characters.")
            continue
        if password != ask_password("Confirm password: "):
            print("Passwords do not match. Try again.")
            continue
        break

    with connect_db() as conn:
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM users WHERE role='student'"
        ).fetchone()["n"]
        register_no = f"STU{count + 1:04d}"
        try:
            cursor = conn.execute("""
                INSERT INTO users
                (role, register_no, username, name, email, dob, phone,
                 password_hash, created_at)
                VALUES ('student', ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                register_no, register_no, name, email, dob, phone,
                hash_password(password), datetime.now().isoformat(timespec="seconds")
            ))
            conn.execute("""
                INSERT INTO performance (student_id, updated_at)
                VALUES (?, ?)
            """, (cursor.lastrowid, datetime.now().isoformat(timespec="seconds")))
        except Exception as exc:
            # Usually a duplicate email or register number; do not print database secrets.
            if "UNIQUE constraint failed" in str(exc):
                print("This email or register number is already registered.")
                return
            raise
    print("Registration successful!")
    print(f"Register number / username: {register_no}")


def student_menu(user):
    """Students can view only their own performance record."""
    while True:
        print("\n--- STUDENT MENU ---")
        print("1. View my performance report")
        print("2. Logout")
        choice = input("Choose: ").strip()
        if choice == "1":
            show_student_report(user["id"])
        elif choice == "2":
            break
        else:
            print("Invalid choice.")
