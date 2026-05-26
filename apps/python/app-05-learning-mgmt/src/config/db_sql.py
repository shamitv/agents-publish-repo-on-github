import sqlite3
from threading import Lock


_db_conn = None
_db_lock = Lock()


def get_db_connection():
    global _db_conn
    if _db_conn is None:
        _db_conn = sqlite3.connect(":memory:", check_same_thread=False)
        _db_conn.row_factory = sqlite3.Row
    return _db_conn


def init_db():
    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone():
            return
        cursor.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                email TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                instructor_id INTEGER NOT NULL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'ACTIVE'
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                max_score INTEGER NOT NULL DEFAULT 100
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                answers TEXT,
                score INTEGER,
                graded_by INTEGER,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.executemany(
            "INSERT INTO users (username, password_hash, role, email) VALUES (?, ?, ?, ?)",
            [
                ("student_alice", "alice_pass_123", "STUDENT", "alice@university.edu"),
                ("student_bob", "bob_pass_456", "STUDENT", "bob@university.edu"),
                ("prof_chen", "chen_pass_789", "INSTRUCTOR", "chen@university.edu"),
                ("admin", "admin_lms_2026", "ADMIN", "admin@university.edu"),
            ],
        )
        cursor.execute(
            "INSERT INTO courses (title, description, instructor_id, category) VALUES "
            "('Intro to Cybersecurity', 'Fundamentals of information security, threat modeling, and network defense.', 3, 'Computer Science')"
        )
        cursor.execute(
            "INSERT INTO courses (title, description, instructor_id, category) VALUES "
            "('Advanced Machine Learning', 'Deep learning architectures, transformers, and reinforcement learning.', 3, 'Data Science')"
        )
        cursor.execute("INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)")
        cursor.execute("INSERT INTO enrollments (user_id, course_id) VALUES (2, 1)")
        cursor.execute("INSERT INTO enrollments (user_id, course_id) VALUES (1, 2)")
        cursor.execute("INSERT INTO quizzes (course_id, title, max_score) VALUES (1, 'Midterm Exam: Network Security', 100)")
        cursor.execute("INSERT INTO quizzes (course_id, title, max_score) VALUES (2, 'Final Exam: Neural Networks', 100)")
        cursor.execute(
            "INSERT INTO submissions (quiz_id, student_id, answers, score, graded_by) "
            "VALUES (1, 1, 'A,B,C,D,A,B,C,D,A,B', 85, 3)"
        )
        cursor.execute(
            "INSERT INTO submissions (quiz_id, student_id, answers, score, graded_by) "
            "VALUES (1, 2, 'A,A,C,D,B,B,C,A,A,B', 72, 3)"
        )
        conn.commit()
