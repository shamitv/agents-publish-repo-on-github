from flask import jsonify, request, session

from src.services.auth_service import AuthService


auth_service = AuthService()


def login():
    data = request.get_json() or {}
    user = auth_service.authenticate(data.get("username", ""), data.get("password", ""))
    if not user:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["role"] = user["role"]
    return jsonify({"success": True, "user": {"username": user["username"], "role": user["role"]}})


def logout():
    session.clear()
    return jsonify({"success": True})


def get_me():
    user = auth_service.current_user(session)
    if not user:
        return jsonify({"message": "Unauthenticated"}), 401
    return jsonify({"username": user["username"], "role": user["role"]})
