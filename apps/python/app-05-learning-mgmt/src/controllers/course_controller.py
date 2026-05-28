from flask import jsonify, request, session

from src.services.course_service import CourseService
from src.services.import_service import ImportService


course_service = CourseService()
import_service = ImportService()


def list_courses():
    return jsonify({"courses": course_service.list_courses()})


def create_course():
    if "user_id" not in session or session.get("role") not in ("INSTRUCTOR", "ADMIN"):
        return jsonify({"message": "Forbidden: Instructor role required"}), 403
    try:
        course_id = course_service.create_course(session, request.get_json() or {})
        return jsonify({"success": True, "id": course_id})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


def import_course():
    if "user_id" not in session or session.get("role") not in ("INSTRUCTOR", "ADMIN"):
        return jsonify({"message": "Forbidden: Instructor or Admin role required"}), 403
    _, payload, status = import_service.import_course(session, (request.get_json() or {}).get("course_data", ""))
    return jsonify(payload), status
