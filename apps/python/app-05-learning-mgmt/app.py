import os
import sqlite3
import pickle
import base64
from flask import Flask, request, jsonify, session
app = Flask(__name__)
app.secret_key = 'lms_secret_key_quantum_learn_2026'
# when combined with the debug config endpoint that exposes it.
# Initialize in-memory SQLite database
db_conn = sqlite3.connect(':memory:', check_same_thread=False)
db_conn.row_factory = sqlite3.Row
def init_db():
    cursor = db_conn.cursor()
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        email TEXT
    )''')
    cursor.execute('''
    CREATE TABLE courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        instructor_id INTEGER NOT NULL,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''
    CREATE TABLE enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'ACTIVE'
    )''')
    cursor.execute('''
    CREATE TABLE quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        max_score INTEGER NOT NULL DEFAULT 100
    )''')
    cursor.execute('''
    CREATE TABLE submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        answers TEXT,
        score INTEGER,
        graded_by INTEGER,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # Seed users
    users_data = [
        ('student_alice', 'alice_pass_123', 'STUDENT', 'alice@university.edu'),
        ('student_bob', 'bob_pass_456', 'STUDENT', 'bob@university.edu'),
        ('prof_chen', 'chen_pass_789', 'INSTRUCTOR', 'chen@university.edu'),
        ('admin', 'admin_lms_2026', 'ADMIN', 'admin@university.edu'),
    ]
    cursor.executemany(
        'INSERT INTO users (username, password_hash, role, email) VALUES (?, ?, ?, ?)',
        users_data,
    )
    # Seed courses
    cursor.execute(
        "INSERT INTO courses (title, description, instructor_id, category) "
        "VALUES ('Intro to Cybersecurity', 'Fundamentals of information security, threat modeling, and network defense.', 3, 'Computer Science')"
    )
    cursor.execute(
        "INSERT INTO courses (title, description, instructor_id, category) "
        "VALUES ('Advanced Machine Learning', 'Deep learning architectures, transformers, and reinforcement learning.', 3, 'Data Science')"
    )
    # Seed enrollments
    cursor.execute("INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)")
    cursor.execute("INSERT INTO enrollments (user_id, course_id) VALUES (2, 1)")
    cursor.execute("INSERT INTO enrollments (user_id, course_id) VALUES (1, 2)")
    # Seed quizzes
    cursor.execute(
        "INSERT INTO quizzes (course_id, title, max_score) VALUES (1, 'Midterm Exam: Network Security', 100)"
    )
    cursor.execute(
        "INSERT INTO quizzes (course_id, title, max_score) VALUES (2, 'Final Exam: Neural Networks', 100)"
    )
    # Seed submissions
    cursor.execute(
        "INSERT INTO submissions (quiz_id, student_id, answers, score, graded_by) "
        "VALUES (1, 1, 'A,B,C,D,A,B,C,D,A,B', 85, 3)"
    )
    cursor.execute(
        "INSERT INTO submissions (quiz_id, student_id, answers, score, graded_by) "
        "VALUES (1, 2, 'A,A,C,D,B,B,C,A,A,B', 72, 3)"
    )
    db_conn.commit()
init_db()
# --- AUTH APIs ---
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    cursor = db_conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username, password),
    )
    user = cursor.fetchone()
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        return jsonify({
            'success': True,
            'user': {'username': user['username'], 'role': user['role']},
        })
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})
@app.route('/api/auth/me', methods=['GET'])
def get_me():
    if 'user_id' in session:
        return jsonify({'username': session['username'], 'role': session['role']})
    return jsonify({'message': 'Unauthenticated'}), 401
# --- COURSE APIs ---
@app.route('/api/courses', methods=['GET'])
def list_courses():
    cursor = db_conn.cursor()
    cursor.execute(
        "SELECT c.id, c.title, c.description, c.category, u.username as instructor "
        "FROM courses c JOIN users u ON c.instructor_id = u.id"
    )
    rows = cursor.fetchall()
    courses = [
        {
            'id': r['id'],
            'title': r['title'],
            'description': r['description'],
            'category': r['category'],
            'instructor': r['instructor'],
        }
        for r in rows
    ]
    return jsonify({'courses': courses})
@app.route('/api/courses', methods=['POST'])
def create_course():
    if 'user_id' not in session or session.get('role') not in ('INSTRUCTOR', 'ADMIN'):
        return jsonify({'message': 'Forbidden: Instructor role required'}), 403
    data = request.get_json() or {}
    title = data.get('title')
    description = data.get('description', '')
    category = data.get('category', 'General')
    cursor = db_conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO courses (title, description, instructor_id, category) VALUES (?, ?, ?, ?)",
            (title, description, session['user_id'], category),
        )
        db_conn.commit()
        return jsonify({'success': True, 'id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
# --- ENROLLMENT APIs ---
@app.route('/api/enrollments', methods=['GET'])
def list_enrollments():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401
    cursor = db_conn.cursor()
    cursor.execute(
        "SELECT e.id, e.status, e.enrolled_at, c.title, c.category "
        "FROM enrollments e JOIN courses c ON e.course_id = c.id WHERE e.user_id = ?",
        (session['user_id'],),
    )
    rows = cursor.fetchall()
    enrollments = [
        {
            'id': r['id'],
            'course_title': r['title'],
            'category': r['category'],
            'status': r['status'],
            'enrolled_at': r['enrolled_at'],
        }
        for r in rows
    ]
    return jsonify({'enrollments': enrollments})
@app.route('/api/enrollments', methods=['POST'])
def enroll():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401
    data = request.get_json() or {}
    course_id = data.get('course_id')
    cursor = db_conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
            (session['user_id'], course_id),
        )
        db_conn.commit()
        return jsonify({'success': True, 'enrollment_id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
# --- QUIZ SUBMISSION APIs ---
@app.route('/api/submissions/<int:submission_id>', methods=['GET'])
def get_submission(submission_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401
    cursor = db_conn.cursor()
    # by ID without verifying that the submission belongs to them.
    # A student can view other students' answers and scores.
    cursor.execute(
        "SELECT s.id, s.answers, s.score, s.submitted_at, q.title as quiz_title, "
        "u.username as student_name "
        "FROM submissions s "
        "JOIN quizzes q ON s.quiz_id = q.id "
        "JOIN users u ON s.student_id = u.id "
        "WHERE s.id = ?",
        (submission_id,),
    )
    row = cursor.fetchone()
    if not row:
        return jsonify({'message': 'Submission not found'}), 404
    return jsonify({
        'id': row['id'],
        'quiz_title': row['quiz_title'],
        'student_name': row['student_name'],
        'answers': row['answers'],
        'score': row['score'],
        'submitted_at': row['submitted_at'],
    })
@app.route('/api/submissions', methods=['POST'])
def submit_quiz():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthenticated'}), 401
    data = request.get_json() or {}
    quiz_id = data.get('quiz_id')
    answers = data.get('answers', '')
    cursor = db_conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO submissions (quiz_id, student_id, answers) VALUES (?, ?, ?)",
            (quiz_id, session['user_id'], answers),
        )
        db_conn.commit()
        return jsonify({'success': True, 'submission_id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
# --- DEBUG / CONFIG APIs ---
@app.route('/api/debug/config', methods=['GET'])
def debug_config():
    # exposes the Flask secret key, database path, environment variables, and
    # internal configuration. No auth check at all.
    config_data = {
        'app_name': 'LMS Platform',
        'secret_key': app.secret_key,
        'database': ':memory:',
        'debug_mode': app.debug,
        'environment': dict(os.environ),
        'python_version': os.sys.version,
        'server_working_dir': os.getcwd(),
    }
    return jsonify(config_data)
# --- COURSE IMPORT (PICKLE DESERIALIZATION) ---
@app.route('/api/courses/import', methods=['POST'])
def import_course():
    # pickle data from user-uploaded base64-encoded payload without any verification.
    # An attacker can craft a malicious pickle object to execute arbitrary code.
    if 'user_id' not in session or session.get('role') not in ('INSTRUCTOR', 'ADMIN'):
        return jsonify({'message': 'Forbidden: Instructor or Admin role required'}), 403
    data = request.get_json() or {}
    course_data_b64 = data.get('course_data', '')
    if not course_data_b64:
        return jsonify({'message': 'Missing course_data payload'}), 400
    try:
        raw_bytes = base64.b64decode(course_data_b64)
        # Dangerous: pickle.loads on untrusted input allows arbitrary code execution
        course_obj = pickle.loads(raw_bytes)
        cursor = db_conn.cursor()
        cursor.execute(
            "INSERT INTO courses (title, description, instructor_id, category) VALUES (?, ?, ?, ?)",
            (
                course_obj.get('title', 'Imported Course'),
                course_obj.get('description', ''),
                session['user_id'],
                course_obj.get('category', 'Imported'),
            ),
        )
        db_conn.commit()
        return jsonify({'success': True, 'course_id': cursor.lastrowid})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
# --- INSTRUCTOR DASHBOARD ---
@app.route('/api/instructor/courses', methods=['GET'])
def instructor_courses():
    if 'user_id' not in session or session.get('role') not in ('INSTRUCTOR', 'ADMIN'):
        return jsonify({'message': 'Forbidden'}), 403
    cursor = db_conn.cursor()
    cursor.execute(
        "SELECT c.id, c.title, c.category, "
        "(SELECT COUNT(*) FROM enrollments e WHERE e.course_id = c.id) as enrollment_count "
        "FROM courses c WHERE c.instructor_id = ?",
        (session['user_id'],),
    )
    rows = cursor.fetchall()
    courses = [
        {
            'id': r['id'],
            'title': r['title'],
            'category': r['category'],
            'enrollment_count': r['enrollment_count'],
        }
        for r in rows
    ]
    return jsonify({'courses': courses})
@app.route('/api/instructor/submissions/<int:quiz_id>', methods=['GET'])
def instructor_submissions(quiz_id):
    if 'user_id' not in session or session.get('role') not in ('INSTRUCTOR', 'ADMIN'):
        return jsonify({'message': 'Forbidden'}), 403
    cursor = db_conn.cursor()
    cursor.execute(
        "SELECT s.id, s.answers, s.score, s.submitted_at, u.username "
        "FROM submissions s JOIN users u ON s.student_id = u.id WHERE s.quiz_id = ?",
        (quiz_id,),
    )
    rows = cursor.fetchall()
    submissions = [
        {
            'id': r['id'],
            'student': r['username'],
            'answers': r['answers'],
            'score': r['score'],
            'submitted_at': r['submitted_at'],
        }
        for r in rows
    ]
    return jsonify({'submissions': submissions})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085, debug=True)
