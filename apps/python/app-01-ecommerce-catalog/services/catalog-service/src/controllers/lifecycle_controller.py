from flask import jsonify, session
from src.services.lifecycle_service import advance_lifecycle, get_lifecycle_history, get_lifecycle


def advance(product_id: int, action: str):
    if "user_id" not in session or session.get("role") != "ADMIN":
        return jsonify({"message": "Forbidden: Administrator role required"}), 403

    try:
        entry = advance_lifecycle(product_id, action)
        return jsonify({"success": True, "entry": entry})
    except ValueError as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


def history(product_id: int):
    if "user_id" not in session:
        return jsonify({"message": "Authentication required"}), 401

    lifecycle = get_lifecycle(product_id)
    entries = get_lifecycle_history(product_id)
    return jsonify({
        "product_id": product_id,
        "current_state": lifecycle.state.value if lifecycle else "unknown",
        "history": entries,
    })