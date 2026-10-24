"""SQLite database, account creation, password hashing, and validation helpers."""
import sqlite3
import hashlib
import hmac
import secrets
from datetime import datetime

DB_FILE = "student_data.db"


def connect_db():
    """Open SQLite database with named-column access and foreign keys enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password, salt=None):
    """Store passwords as salted PBKDF2 hashes, never plain text."""
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 200_000
    ).hex()
    return f"{salt}${digest}"


def verify_password(password, saved_hash):
    """Compare a submitted password to the saved hash safely."""
    try:
        salt, expected = saved_hash.split("$", 1)
        actual = hash_password(password, salt).split("$", 1)[1]
        return hmac.compare_digest(actual, expected)
    except (ValueError, AttributeError):
        return False


def initialize_database():
    """Create application tables and seed a demo admin on first run."""
    with connect_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL CHECK(role IN ('student','staff','admin')),
            register_no TEXT UNIQUE,
            username TEXT UNIQUE,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            dob TEXT,
            phone TEXT,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL UNIQUE,
            marks REAL NOT NULL DEFAULT 0,
            max_marks REAL NOT NULL DEFAULT 100,
            attendance REAL NOT NULL DEFAULT 0,
            slip_test REAL NOT NULL DEFAULT 0,
            internal_mark REAL NOT NULL DEFAULT 0,
            assignment_mark REAL NOT NULL DEFAULT 0,
            arrears INTEGER NOT NULL DEFAULT 0,
            achievement TEXT DEFAULT '',
            quiz_points REAL NOT NULL DEFAULT 0,
            remarks TEXT DEFAULT '',
            updated_by INTEGER,
            updated_at TEXT,
            FOREIGN KEY(student_id) REFERENCES users(id),
            FOREIGN KEY(updated_by) REFERENCES users(id)
        );
        """)
        exists = conn.execute(
            "SELECT id FROM users WHERE role='admin' LIMIT 1"
        ).fetchone()
        if not exists:
            conn.execute("""
                INSERT INTO users
                (role, username, name, email, password_hash, created_at)
                VALUES ('admin', ?, ?, ?, ?, ?)
            """, (
                "admin", "System Administrator", "admin@example.local",
                hash_password("Admin@123"), datetime.now().isoformat(timespec="seconds")
            ))
    print("Database ready. Demo admin: admin / Admin@123 (change before real use).")


def ask_nonempty(prompt):
    """Prompt until a non-empty value is entered."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def ask_email():
    """Basic email format validation; it does not verify ownership."""
    while True:
        value = input("Gmail/email: ").strip().lower()
        if "@" in value and "." in value.rsplit("@", 1)[-1]:
            return value
        print("Enter a valid email address.")


def ask_password(prompt="Password: "):
    """Read a password without echoing it to the terminal."""
    import getpass
    return getpass.getpass(prompt)


def ask_number(prompt, minimum=0, maximum=None, integer=False):
    """Read a number and enforce optional bounds."""
    while True:
        try:
            value = int(input(prompt).strip()) if integer else float(input(prompt).strip())
            if value < minimum or (maximum is not None and value > maximum):
                print(f"Enter a value from {minimum} to {maximum}.")
                continue
            return value
        except ValueError:
            print("Enter a valid number.")


def ask_date(prompt="Date of birth (YYYY-MM-DD): "):
    """Validate a date in YYYY-MM-DD format and reject future dates."""
    from datetime import date
    while True:
        raw = input(prompt).strip()
        try:
            parsed = datetime.strptime(raw, "%Y-%m-%d").date()
            if parsed > date.today():
                print("Date cannot be in the future.")
                continue
            return parsed.isoformat()
        except ValueError:
            print("Use YYYY-MM-DD, for example 2007-05-21.")


def login(role):
    """Login with register number, username, or email in one field."""
    from getpass import getpass
    print(f"\n=== {role.upper()} LOGIN ===")
    identifier = ask_nonempty("Register number / username / Gmail: ").lower()
    password = getpass("Password: ")
    with connect_db() as conn:
        user = conn.execute("""
            SELECT * FROM users
            WHERE lower(COALESCE(register_no,''))=?
               OR lower(COALESCE(username,''))=?
               OR lower(email)=?
        """, (identifier, identifier, identifier)).fetchone()
    if not user or user["role"] != role or not verify_password(password, user["password_hash"]):
        print("Login failed. Check your details and account role.")
        return None
    print(f"Welcome, {user['name']}!")
    return dict(user)
