from flask import jsonify, session

from src.services.course_service import CourseService
from src.services.submission_service import SubmissionService


course_service = CourseService()
submission_service = SubmissionService()


def instructor_courses():
    if "user_id" not in session or session.get("role") not in ("INSTRUCTOR", "ADMIN"):
        return jsonify({"message": "Forbidden"}), 403
    return jsonify({"courses": course_service.instructor_courses(session["user_id"])})


def instructor_submissions(quiz_id):
    if "user_id" not in session or session.get("role") not in ("INSTRUCTOR", "ADMIN"):
        return jsonify({"message": "Forbidden"}), 403
    return jsonify({"submissions": submission_service.list_for_quiz(quiz_id)})
