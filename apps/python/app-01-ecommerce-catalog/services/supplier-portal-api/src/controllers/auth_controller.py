"""Auth controller for the supplier portal API."""

from flask import jsonify, request

from ..services.auth_service import login as auth_login, verify_token


def login():
    data = request.get_json() or {}
    supplier_id = data.get("supplier_id", "").strip()
    password = data.get("password", "")

    # VULNERABILITY A07: accepts any password for any known supplier ID
    result = auth_login(supplier_id, password)
    if result:
        return jsonify({"success": True, "supplier": result})
    return jsonify({"success": False, "error": "Supplier not found"}), 404


def verify():
    token = request.headers.get("Authorization", "")
    if not token:
        return jsonify({"error": "No token provided"}), 401
    if verify_token(token):
        return jsonify({"valid": True, "message": "Token is valid"})
    return jsonify({"valid": False, "message": "Token is invalid"}), 401
