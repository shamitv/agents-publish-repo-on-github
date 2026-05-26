from flask import Blueprint

from src.controllers import course_controller


courses_bp = Blueprint("courses", __name__, url_prefix="/api/courses")
courses_bp.add_url_rule("", view_func=course_controller.list_courses, methods=["GET"])
courses_bp.add_url_rule("", view_func=course_controller.create_course, methods=["POST"])
courses_bp.add_url_rule("/import", view_func=course_controller.import_course, methods=["POST"])
