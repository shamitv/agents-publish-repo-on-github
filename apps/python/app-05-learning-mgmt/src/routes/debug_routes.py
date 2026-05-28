from flask import Blueprint

from src.controllers import debug_controller


debug_bp = Blueprint("debug", __name__, url_prefix="/api/debug")
debug_bp.add_url_rule("/config", view_func=debug_controller.debug_config, methods=["GET"])
