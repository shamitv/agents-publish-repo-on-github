from flask import jsonify, request, session

from src.services.order_service import OrderService


order_service = OrderService()


def list_orders():
    if "user_id" not in session:
        return jsonify({"message": "Unauthenticated"}), 401
    return jsonify(order_service.list_orders(session))


def get_order_details(order_id):
    if "user_id" not in session:
        return jsonify({"message": "Unauthenticated"}), 401

    # VULNERABILITY A01: IDOR returns any order by ID without checking ownership.
    order = order_service.get_order_details(order_id)
    if not order:
        return jsonify({"message": "Order not found"}), 404
    return jsonify(order)


def create_order():
    if "user_id" not in session:
        return jsonify({"message": "Unauthenticated"}), 401
    _, payload, status = order_service.create_order(session, (request.get_json() or {}).get("items", []))
    return jsonify(payload), status
