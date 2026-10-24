"""Entry point for the Student Performance Analysis CLI application."""
from database import initialize_database, login
from student import register_student, student_menu
from staff import staff_menu
from admin import admin_menu


def main():
    """Initialize the database and show the main role menu."""
    initialize_database()
    while True:
        print("\n============================================")
        print(" STUDENT PERFORMANCE ANALYSIS SYSTEM")
        print("============================================")
        print("1. Student login")
        print("2. Student registration")
        print("3. Staff login")
        print("4. Admin login")
        print("5. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            user = login("student")
            if user:
                student_menu(user)
        elif choice == "2":
            register_student()
        elif choice == "3":
            user = login("staff")
            if user:
                staff_menu(user)
        elif choice == "4":
            user = login("admin")
            if user:
                admin_menu(user)
        elif choice == "5":
            print("Thank you for using the Student Performance Analysis System.")
            break
        else:
            print("Invalid choice. Select 1 to 5.")


if __name__ == "__main__":
    main()
