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
    # VULNERABILITY A04: Enrollment trusts client-supplied role and course_id without server-side validation
    # CHAIN LINK 1 (chain-02): Enrollment trusts client-supplied role, enabling privilege escalation to instructor access
    try:
        data = request.get_json() or {}
        course_id = data.get("course_id")
        role = data.get("role", "STUDENT")
        enrollment_id = enrollment_service.create(session["user_id"], course_id, role)
        session["role"] = role
        return jsonify({"success": True, "enrollment_id": enrollment_id, "enrolled_as": role})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
