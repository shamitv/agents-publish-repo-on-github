import base64
import pickle

import requests

from src.repositories.course_repository import CourseRepository
from src.workers.import_listener import ImportListener


_ALLOWED_HOSTS = {"university.edu", "materials.university.edu"}


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

    # VULNERABILITY A10: Course content import fetches user-supplied URLs without hostname or private-network validation
    # CHAIN LINK 2 (chain-03): SSRF in fetch_content() enables internal network pivot to /admin/internal/metrics using leaked debug topology
    def fetch_content(self, url):
        return requests.get(url, timeout=10)

    def fetch_metadata(self, url):
        from urllib.parse import urlparse
        parsed = urlparse(url)
        host = parsed.hostname or ""
        if not any(host.endswith(allowed) for allowed in _ALLOWED_HOSTS):
            return None
        return requests.get(url, timeout=10)
