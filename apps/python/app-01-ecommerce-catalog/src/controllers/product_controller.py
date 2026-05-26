from flask import jsonify, request, session

from src.services.product_service import ProductService


product_service = ProductService()


def list_products():
    query_text = request.args.get("q", "").strip()
    try:
        return jsonify(product_service.list_products(query_text))
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


def create_product():
    if "user_id" not in session or session.get("role") != "ADMIN":
        return jsonify({"message": "Forbidden: Administrator role required"}), 403

    # CHAIN LINK 3 (chain-01): Admin product mutation trusts a forgeable session role.
    data = request.get_json() or {}
    try:
        product_id = product_service.create_product(data)
        return jsonify({"success": True, "id": product_id})
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
