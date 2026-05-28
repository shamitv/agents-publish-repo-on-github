from flask import Blueprint

from src.controllers import enrollment_controller


enrollments_bp = Blueprint("enrollments", __name__, url_prefix="/api/enrollments")
enrollments_bp.add_url_rule("", view_func=enrollment_controller.list_enrollments, methods=["GET"])
enrollments_bp.add_url_rule("", view_func=enrollment_controller.enroll, methods=["POST"])
