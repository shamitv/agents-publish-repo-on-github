from flask import Blueprint

from src.controllers import submission_controller


submissions_bp = Blueprint("submissions", __name__, url_prefix="/api/submissions")
submissions_bp.add_url_rule("", view_func=submission_controller.submit_quiz, methods=["POST"])
submissions_bp.add_url_rule("/<int:submission_id>", view_func=submission_controller.get_submission, methods=["GET"])
