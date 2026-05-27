from flask import Blueprint

from src.controllers import product_controller


products_bp = Blueprint("products", __name__, url_prefix="/api/products")
products_bp.add_url_rule("", view_func=product_controller.list_products, methods=["GET"])
products_bp.add_url_rule("", view_func=product_controller.create_product, methods=["POST"])
products_bp.add_url_rule("/my-products", view_func=product_controller.get_my_products, methods=["GET"])
