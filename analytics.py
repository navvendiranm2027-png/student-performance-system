"""Pandas and NumPy reporting for student performance."""
import numpy as np
import pandas as pd
from database import connect_db


WEIGHTS = np.array([0.35, 0.20, 0.15, 0.15, 0.15])


def performance_band(score):
    """Convert a percentage score into a simple performance category."""
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Very Good"
    if score >= 55:
        return "Good"
    if score >= 40:
        return "Needs Improvement"
    return "At Risk"


def calculate_score(row):
    """Calculate weighted score from exam, attendance, slip, internal, assignment."""
    maximum = float(row["max_marks"] or 100)
    exam_pct = float(row["marks"] or 0) / maximum * 100 if maximum else 0
    values = np.clip(np.array([
        exam_pct, row["attendance"], row["slip_test"],
        row["internal_mark"], row["assignment_mark"]
    ], dtype=float), 0, 100)
    return float(np.dot(values, WEIGHTS))


def show_student_report(student_id):
    """Print one student's academic record and calculated performance."""
    with connect_db() as conn:
        row = conn.execute("""
            SELECT u.id, u.register_no, u.name, u.email, p.*
            FROM users u JOIN performance p ON p.student_id=u.id
            WHERE u.id=? AND u.role='student'
        """, (student_id,)).fetchone()
    if not row:
        print("No performance record found.")
        return
    score = calculate_score(row)
    print("\n========== STUDENT PERFORMANCE REPORT ==========")
    print(f"Name             : {row['name']}")
    print(f"Register number  : {row['register_no']}")
    print(f"Email            : {row['email']}")
    print(f"Exam marks       : {row['marks']} / {row['max_marks']}")
    print(f"Attendance       : {row['attendance']}%")
    print(f"Slip-test marks  : {row['slip_test']} / 100")
    print(f"Internal marks   : {row['internal_mark']} / 100")
    print(f"Assignment marks : {row['assignment_mark']} / 100")
    print(f"Arrears          : {row['arrears']}")
    print(f"Quiz points      : {row['quiz_points']}")
    print(f"Achievement      : {row['achievement'] or 'None recorded'}")
    print(f"Staff remarks    : {row['remarks'] or 'None recorded'}")
    print(f"Performance score: {score:.2f}%")
    print(f"Performance band : {performance_band(score)}")
    print("================================================")


def monitor_all_students():
    """Use Pandas/NumPy for a class summary and export a CSV report."""
    with connect_db() as conn:
        df = pd.read_sql_query("""
            SELECT u.register_no, u.name, u.email, p.marks, p.max_marks,
                   p.attendance, p.slip_test, p.internal_mark,
                   p.assignment_mark, p.arrears, p.quiz_points,
                   p.achievement, p.remarks
            FROM users u JOIN performance p ON p.student_id=u.id
            WHERE u.role='student'
            ORDER BY u.register_no
        """, conn)
    if df.empty:
        print("No student data available.")
        return
    maximum = df["max_marks"].replace(0, np.nan)
    df["exam_percent"] = (df["marks"] / maximum * 100).fillna(0).clip(0, 100)
    matrix = df[[
        "exam_percent", "attendance", "slip_test", "internal_mark", "assignment_mark"
    ]].fillna(0).to_numpy(dtype=float)
    df["performance_score"] = np.clip(matrix, 0, 100) @ WEIGHTS
    df["performance_band"] = df["performance_score"].apply(performance_band)
    print("\n========== CLASS PERFORMANCE MONITOR ==========")
    print(df[[
        "register_no", "name", "exam_percent", "attendance", "arrears",
        "quiz_points", "performance_score", "performance_band"
    ]].to_string(index=False, formatters={
        "exam_percent": "{:.1f}%".format,
        "attendance": "{:.1f}%".format,
        "performance_score": "{:.1f}%".format
    }))
    scores = df["performance_score"].to_numpy(dtype=float)
    print("\nClass analytics:")
    print(f"Students monitored   : {len(df)}")
    print(f"Average score        : {np.mean(scores):.2f}%")
    print(f"Median score         : {np.median(scores):.2f}%")
    print(f"Highest score        : {np.max(scores):.2f}%")
    print(f"Lowest score         : {np.min(scores):.2f}%")
    print(f"Attendance below 75% : {(df['attendance'] < 75).sum()}")
    print(f"Students with arrears: {(df['arrears'] > 0).sum()}")
    output = "student_performance_report.csv"
    df.to_csv(output, index=False)
    print(f"CSV report saved as: {output}")
