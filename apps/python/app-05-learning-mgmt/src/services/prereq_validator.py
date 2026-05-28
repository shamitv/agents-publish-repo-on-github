class PrereqValidator:
    def __init__(self, user_repo=None, course_repo=None, enrollment_repo=None):
        from src.repositories.user_repository import UserRepository
        from src.repositories.course_repository import CourseRepository
        from src.repositories.enrollment_repository import EnrollmentRepository
        self.users = user_repo or UserRepository()
        self.courses = course_repo or CourseRepository()
        self.enrollments = enrollment_repo or EnrollmentRepository()

    def validate_prerequisites(self, user_id, course_id):
        course = self.courses.find_by_id(course_id)
        if not course:
            return ["Course not found"]
        import json
        prereqs = course.get("prerequisites")
        if isinstance(prereqs, str):
            prereqs = json.loads(prereqs)
        if not prereqs:
            return []
        completed_courses = set()
        for enrollment in self.enrollments.list_for_user(user_id):
            try:
                from src.config.db_sql import get_db_cursor
                with get_db_cursor() as cur:
                    cur.execute(
                        "SELECT c.id, c.title FROM courses c "
                        "JOIN enrollments e ON e.course_id = c.id "
                        "WHERE e.user_id = %s AND e.status = 'COMPLETED'",
                        (user_id,),
                    )
                    for row in cur.fetchall():
                        completed_courses.add(row["id"])
            except Exception:
                pass
        missing = []
        for prereq_id in prereqs:
            prereq_id = int(prereq_id) if not isinstance(prereq_id, int) else prereq_id
            if prereq_id not in completed_courses:
                prereq_course = self.courses.find_by_id(prereq_id)
                title = prereq_course["title"] if prereq_course else f"Course {prereq_id}"
                missing.append(title)
        return missing
