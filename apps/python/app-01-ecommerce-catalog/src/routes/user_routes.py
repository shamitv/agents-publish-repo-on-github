from flask import Blueprint

from src.controllers import user_controller


users_bp = Blueprint("users", __name__, url_prefix="/api")
users_bp.add_url_rule("/users/exists", view_func=user_controller.user_exists, methods=["GET"])
users_bp.add_url_rule("/user/profile", view_func=user_controller.profile, methods=["GET"])
