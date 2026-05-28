from src.config.db_sql import get_db_cursor


class CourseRepository:
    def list_courses(self):
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT c.id, c.title, c.description, c.category, u.username as instructor "
                "FROM courses c JOIN users u ON c.instructor_id = u.id ORDER BY c.id"
            )
            return cur.fetchall()

    def create(self, title, description, instructor_id, category):
        with get_db_cursor() as cur:
            cur.execute(
                "INSERT INTO courses (title, description, instructor_id, category) VALUES (%s, %s, %s, %s) RETURNING id",
                (title, description, instructor_id, category),
            )
            return cur.fetchone()["id"]

    def instructor_courses(self, instructor_id):
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT c.id, c.title, c.category, "
                "(SELECT COUNT(*) FROM enrollments e WHERE e.course_id = c.id) as enrollment_count "
                "FROM courses c WHERE c.instructor_id = %s",
                (instructor_id,),
            )
            return cur.fetchall()

    def find_by_id(self, course_id):
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT id, title, description, instructor_id, category, prerequisites, status "
                "FROM courses WHERE id = %s",
                (course_id,),
            )
            return cur.fetchone()
