from flask import jsonify, request, session

from src.repositories.user_repository import UserRepository


users = UserRepository()


def user_exists():
    username = request.args.get("username", "").strip()
    # CHAIN LINK 1 (chain-01): Unauthenticated endpoint confirms whether privileged usernames exist.
    row = users.find_by_username(username)
    if row:
        return jsonify({"exists": True})
    return jsonify({"exists": False}), 404


def profile():
    if "user_id" not in session:
        return jsonify({"message": "Unauthenticated"}), 401
    user = users.find_by_id(session["user_id"])
    if not user:
        return jsonify({"message": "Not found"}), 404
    return jsonify({"id": user["id"], "username": user["username"], "role": user["role"]})
