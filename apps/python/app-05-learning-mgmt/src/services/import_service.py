import base64
import pickle

from src.repositories.course_repository import CourseRepository
from src.workers.import_listener import ImportListener


class ImportService:
    def __init__(self, courses=None):
        self.courses = courses or CourseRepository()
        self.worker = ImportListener()

    def import_course(self, session_data, course_data_b64):
        if not course_data_b64:
            return None, {"message": "Missing course_data payload"}, 400
        try:
            raw_bytes = base64.b64decode(course_data_b64)
            course_obj = self.worker.load_course(raw_bytes)
            course_id = self.courses.create(
                course_obj.get("title", "Imported Course"),
                course_obj.get("description", ""),
                session_data["user_id"],
                course_obj.get("category", "Imported"),
            )
            return course_id, {"success": True, "course_id": course_id}, 200
        except Exception as exc:
            return None, {"success": False, "error": str(exc)}, 400
