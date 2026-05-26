from flask import jsonify, request, session

from src.services.enrollment_service import EnrollmentService


enrollment_service = EnrollmentService()


def list_enrollments():
    if "user_id" not in session:
        return jsonify({"message": "Unauthenticated"}), 401
    return jsonify({"enrollments": enrollment_service.list_for_user(session["user_id"])})


def enroll():
    if "user_id" not in session:
        return jsonify({"message": "Unauthenticated"}), 401
    try:
        enrollment_id = enrollment_service.create(session["user_id"], (request.get_json() or {}).get("course_id"))
        return jsonify({"success": True, "enrollment_id": enrollment_id})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
