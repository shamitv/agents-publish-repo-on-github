from src.config.db_sql import get_db_connection


class CourseRepository:
    def list_courses(self):
        cursor = get_db_connection().cursor()
        cursor.execute(
            "SELECT c.id, c.title, c.description, c.category, u.username as instructor "
            "FROM courses c JOIN users u ON c.instructor_id = u.id"
        )
        return cursor.fetchall()

    def create(self, title, description, instructor_id, category):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO courses (title, description, instructor_id, category) VALUES (?, ?, ?, ?)",
            (title, description, instructor_id, category),
        )
        conn.commit()
        return cursor.lastrowid

    def instructor_courses(self, instructor_id):
        cursor = get_db_connection().cursor()
        cursor.execute(
            "SELECT c.id, c.title, c.category, "
            "(SELECT COUNT(*) FROM enrollments e WHERE e.course_id = c.id) as enrollment_count "
            "FROM courses c WHERE c.instructor_id = ?",
            (instructor_id,),
        )
        return cursor.fetchall()
