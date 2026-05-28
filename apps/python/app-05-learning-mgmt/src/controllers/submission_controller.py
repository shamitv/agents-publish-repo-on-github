from flask import jsonify, request, session

from src.services.submission_service import SubmissionService


submission_service = SubmissionService()


def get_submission(submission_id):
    if "user_id" not in session:
        return jsonify({"message": "Unauthenticated"}), 401
    submission = submission_service.get_submission(submission_id)
    if not submission:
        return jsonify({"message": "Submission not found"}), 404
    return jsonify(submission)


def submit_quiz():
    if "user_id" not in session:
        return jsonify({"message": "Unauthenticated"}), 401
    try:
        submission_id = submission_service.submit(session["user_id"], request.get_json() or {})
        return jsonify({"success": True, "submission_id": submission_id})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
