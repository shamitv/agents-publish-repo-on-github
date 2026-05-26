from src.config.db_sql import get_db_connection


class EnrollmentRepository:
    def list_for_user(self, user_id):
        cursor = get_db_connection().cursor()
        cursor.execute(
            "SELECT e.id, e.status, e.enrolled_at, c.title, c.category "
            "FROM enrollments e JOIN courses c ON e.course_id = c.id WHERE e.user_id = ?",
            (user_id,),
        )
        return cursor.fetchall()

    def create(self, user_id, course_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", (user_id, course_id))
        conn.commit()
        return cursor.lastrowid
