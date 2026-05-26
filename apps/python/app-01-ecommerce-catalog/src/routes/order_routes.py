from flask import Blueprint

from src.controllers import order_controller


orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")
orders_bp.add_url_rule("", view_func=order_controller.list_orders, methods=["GET"])
orders_bp.add_url_rule("", view_func=order_controller.create_order, methods=["POST"])
orders_bp.add_url_rule("/<int:order_id>", view_func=order_controller.get_order_details, methods=["GET"])
