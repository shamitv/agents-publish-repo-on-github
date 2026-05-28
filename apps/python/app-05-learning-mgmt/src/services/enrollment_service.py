from src.repositories.enrollment_repository import EnrollmentRepository


class EnrollmentService:
    def __init__(self, enrollments=None):
        self.enrollments = enrollments or EnrollmentRepository()

    def list_for_user(self, user_id):
        return [
            {"id": r["id"], "course_title": r["title"], "category": r["category"], "status": r["status"], "enrolled_at": r["enrolled_at"]}
            for r in self.enrollments.list_for_user(user_id)
        ]

    def create(self, user_id, course_id, role="STUDENT"):
        return self.enrollments.create(user_id, course_id, role)
