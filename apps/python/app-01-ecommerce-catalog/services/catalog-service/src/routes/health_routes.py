from flask import Blueprint

from src.controllers import health_controller


health_bp = Blueprint("health", __name__, url_prefix="/api")
health_bp.add_url_rule("/health", view_func=health_controller.health, methods=["GET"])
