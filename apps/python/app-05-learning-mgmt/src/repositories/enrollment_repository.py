from src.config.db_sql import get_db_cursor


class EnrollmentRepository:
    def list_for_user(self, user_id):
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT e.id, e.status, e.enrolled_at, c.title, c.category "
                "FROM enrollments e JOIN courses c ON e.course_id = c.id WHERE e.user_id = %s",
                (user_id,),
            )
            return cur.fetchall()

    def create(self, user_id, course_id, role="STUDENT"):
        with get_db_cursor() as cur:
            cur.execute(
                "INSERT INTO enrollments (user_id, course_id, role) VALUES (%s, %s, %s) RETURNING id",
                (user_id, course_id, role),
            )
            return cur.fetchone()["id"]
