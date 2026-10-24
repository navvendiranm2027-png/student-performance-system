# Student Performance Analysis System

## Modules
- `main.py`: CLI menu and routing
- `database.py`: SQLite, password hashing, login, input helpers
- `student.py`: student registration and student dashboard
- `staff.py`: student listing and performance data entry
- `admin.py`: staff creation and admin monitoring menu
- `analytics.py`: Pandas/NumPy reports and CSV export
- `requirements.txt`: dependencies

## Run on Windows CMD
```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## First-run administrator
Username: `admin`
Password: `Admin@123`

Change this default password before real use. The current CLI does not yet include a password-change feature.

## Notes
- `student_data.db` is created automatically on first launch.
- Gmail is used as a login identifier. Actual Google OAuth and email verification are not implemented.
- Admin class reports export to `student_performance_report.csv`.
- This is a local starter app; do not expose it publicly with demo credentials.
