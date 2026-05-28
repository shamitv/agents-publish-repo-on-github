import time
from contextlib import contextmanager

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from src.config.settings import DATABASE_URL


_pool = None


def get_db_pool():
    global _pool
    if _pool is None:
        _pool = pool.SimpleConnectionPool(1, 10, dsn=DATABASE_URL)
    return _pool


@contextmanager
def get_db():
    p = get_db_pool()
    conn = p.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        p.putconn(conn)


@contextmanager
def get_db_cursor():
    with get_db() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur


def get_db_connection():
    return get_db_pool().getconn()


def return_conn(conn):
    get_db_pool().putconn(conn)


def wait_for_db(max_retries=15, delay=2):
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.close()
            return True
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(delay)
    return False


def init_db():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM information_schema.tables WHERE table_name='users'")
            if cur.fetchone():
                return
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    email VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS courses (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    instructor_id INTEGER NOT NULL REFERENCES users(id),
                    category VARCHAR(100),
                    prerequisites JSONB DEFAULT '[]',
                    status VARCHAR(50) DEFAULT 'ACTIVE',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS enrollments (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    course_id INTEGER NOT NULL REFERENCES courses(id),
                    role VARCHAR(50) DEFAULT 'STUDENT',
                    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(50) DEFAULT 'ACTIVE'
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS quizzes (
                    id SERIAL PRIMARY KEY,
                    course_id INTEGER NOT NULL REFERENCES courses(id),
                    title VARCHAR(255) NOT NULL,
                    max_score INTEGER NOT NULL DEFAULT 100
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS submissions (
                    id SERIAL PRIMARY KEY,
                    quiz_id INTEGER NOT NULL REFERENCES quizzes(id),
                    student_id INTEGER NOT NULL REFERENCES users(id),
                    answers TEXT,
                    score INTEGER,
                    graded_by INTEGER REFERENCES users(id),
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS grades (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    course_id INTEGER NOT NULL REFERENCES courses(id),
                    quiz_id INTEGER,
                    score FLOAT,
                    graded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    action VARCHAR(100),
                    entity_type VARCHAR(100),
                    entity_id INTEGER,
                    old_value TEXT,
                    new_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            cur.execute(
                "INSERT INTO users (username, password_hash, role, email) VALUES "
                "('student_alice', 'alice_pass_123', 'STUDENT', 'alice@university.edu'), "
                "('student_bob', 'bob_pass_456', 'STUDENT', 'bob@university.edu'), "
                "('prof_chen', 'chen_pass_789', 'INSTRUCTOR', 'chen@university.edu'), "
                "('admin', 'admin_lms_2026', 'ADMIN', 'admin@university.edu') "
                "ON CONFLICT (username) DO NOTHING"
            )
            cur.execute(
                "INSERT INTO courses (title, description, instructor_id, category) VALUES "
                "('Intro to Cybersecurity', 'Fundamentals of information security, threat modeling, and network defense.', 3, 'Computer Science') "
                "ON CONFLICT DO NOTHING"
            )
            cur.execute(
                "INSERT INTO courses (title, description, instructor_id, category) VALUES "
                "('Advanced Machine Learning', 'Deep learning architectures, transformers, and reinforcement learning.', 3, 'Data Science') "
                "ON CONFLICT DO NOTHING"
            )
            cur.execute(
                "INSERT INTO enrollments (user_id, course_id) VALUES (1, 1), (2, 1), (1, 2) ON CONFLICT DO NOTHING"
            )
            cur.execute(
                "INSERT INTO quizzes (course_id, title, max_score) VALUES (1, 'Midterm Exam: Network Security', 100) ON CONFLICT DO NOTHING"
            )
            cur.execute(
                "INSERT INTO quizzes (course_id, title, max_score) VALUES (2, 'Final Exam: Neural Networks', 100) ON CONFLICT DO NOTHING"
            )
            cur.execute(
                "INSERT INTO submissions (quiz_id, student_id, answers, score, graded_by) "
                "VALUES (1, 1, 'A,B,C,D,A,B,C,D,A,B', 85, 3) ON CONFLICT DO NOTHING"
            )
            cur.execute(
                "INSERT INTO submissions (quiz_id, student_id, answers, score, graded_by) "
                "VALUES (1, 2, 'A,A,C,D,B,B,C,A,A,B', 72, 3) ON CONFLICT DO NOTHING"
            )
