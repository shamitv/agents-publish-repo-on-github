from flask import Blueprint

from src.controllers import lifecycle_controller


lifecycle_bp = Blueprint("lifecycle", __name__, url_prefix="/api/products")


lifecycle_bp.add_url_rule(
    "/<int:product_id>/lifecycle/<action>",
    view_func=lifecycle_controller.advance,
    methods=["POST"],
)
lifecycle_bp.add_url_rule(
    "/<int:product_id>/lifecycle",
    view_func=lifecycle_controller.history,
    methods=["GET"],
)