from src.config.db_sql import get_db_connection


class SubmissionRepository:
    def find_by_id(self, submission_id):
        cursor = get_db_connection().cursor()
        cursor.execute(
            "SELECT s.id, s.answers, s.score, s.submitted_at, q.title as quiz_title, u.username as student_name "
            "FROM submissions s JOIN quizzes q ON s.quiz_id = q.id "
            "JOIN users u ON s.student_id = u.id WHERE s.id = ?",
            (submission_id,),
        )
        return cursor.fetchone()

    def create(self, quiz_id, student_id, answers):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO submissions (quiz_id, student_id, answers) VALUES (?, ?, ?)",
            (quiz_id, student_id, answers),
        )
        conn.commit()
        return cursor.lastrowid

    def list_for_quiz(self, quiz_id):
        cursor = get_db_connection().cursor()
        cursor.execute(
            "SELECT s.id, s.answers, s.score, s.submitted_at, u.username "
            "FROM submissions s JOIN users u ON s.student_id = u.id WHERE s.quiz_id = ?",
            (quiz_id,),
        )
        return cursor.fetchall()
