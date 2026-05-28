from flask import jsonify, request, session

from src.services.course_service import CourseService
from src.services.grade_override_service import GradeOverrideService
from src.services.submission_service import SubmissionService


course_service = CourseService()
submission_service = SubmissionService()
grade_override_service = GradeOverrideService()


def instructor_courses():
    if "user_id" not in session or session.get("role") not in ("INSTRUCTOR", "ADMIN"):
        return jsonify({"message": "Forbidden"}), 403
    return jsonify({"courses": course_service.instructor_courses(session["user_id"])})


def instructor_submissions(quiz_id):
    if "user_id" not in session or session.get("role") not in ("INSTRUCTOR", "ADMIN"):
        return jsonify({"message": "Forbidden"}), 403
    return jsonify({"submissions": submission_service.list_for_quiz(quiz_id)})


def override_grade():
    if "user_id" not in session or session.get("role") not in ("INSTRUCTOR", "ADMIN"):
        return jsonify({"message": "Forbidden"}), 403
    # CHAIN LINK 2 (chain-02): Grade override validates INSTRUCTOR role but does NOT verify course ownership — any instructor can modify any grade
    try:
        data = request.get_json() or {}
        student_id = data.get("student_id")
        course_id = data.get("course_id")
        quiz_id = data.get("quiz_id")
        new_score = data.get("new_score")
        if not all([student_id, course_id, quiz_id, new_score is not None]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        grade_id = grade_override_service.override_grade(
            session["user_id"], student_id, course_id, quiz_id, new_score
        )
        return jsonify({"success": True, "grade_id": grade_id})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
