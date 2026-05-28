from flask import Blueprint

from src.controllers import instructor_controller


instructor_bp = Blueprint("instructor", __name__, url_prefix="/api/instructor")
instructor_bp.add_url_rule("/courses", view_func=instructor_controller.instructor_courses, methods=["GET"])
instructor_bp.add_url_rule("/submissions/<int:quiz_id>", view_func=instructor_controller.instructor_submissions, methods=["GET"])
instructor_bp.add_url_rule("/grades/override", view_func=instructor_controller.override_grade, methods=["POST"])
