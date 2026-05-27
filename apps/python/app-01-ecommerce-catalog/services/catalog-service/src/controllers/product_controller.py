from flask import jsonify, request, session

from src.repositories.product_repository import ProductRepository
from src.services.product_service import ProductService


product_service = ProductService()
product_repo = ProductRepository()


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


# Decoy safe pattern: correctly scoped to authenticated supplier's own products
def get_my_products():
    supplier_id = session.get("supplier_id")
    if not supplier_id:
        return jsonify({"message": "Supplier authentication required"}), 403

    rows = product_repo.list_by_supplier(supplier_id)
    products = [
        {"id": r["id"], "sku": r["sku"], "name": r["name"], "description": r["description"],
         "category": r["category"], "price": r["price"], "quantity": r["quantity"]}
        for r in rows
    ]
    return jsonify({"products": products})
