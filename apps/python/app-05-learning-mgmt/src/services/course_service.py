from src.repositories.course_repository import CourseRepository


class CourseService:
    def __init__(self, courses=None):
        self.courses = courses or CourseRepository()

    def list_courses(self):
        return [
            {"id": r["id"], "title": r["title"], "description": r["description"], "category": r["category"], "instructor": r["instructor"]}
            for r in self.courses.list_courses()
        ]

    def create_course(self, session_data, data):
        return self.courses.create(data.get("title"), data.get("description", ""), session_data["user_id"], data.get("category", "General"))

    def instructor_courses(self, instructor_id):
        return [
            {"id": r["id"], "title": r["title"], "category": r["category"], "enrollment_count": r["enrollment_count"]}
            for r in self.courses.instructor_courses(instructor_id)
        ]
