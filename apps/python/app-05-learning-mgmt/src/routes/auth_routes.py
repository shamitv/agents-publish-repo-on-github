from flask import Blueprint

from src.controllers import auth_controller


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
auth_bp.add_url_rule("/login", view_func=auth_controller.login, methods=["POST"])
auth_bp.add_url_rule("/logout", view_func=auth_controller.logout, methods=["POST"])
auth_bp.add_url_rule("/me", view_func=auth_controller.get_me, methods=["GET"])
