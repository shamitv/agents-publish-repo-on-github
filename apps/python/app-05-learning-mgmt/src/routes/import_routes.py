from flask import Blueprint, jsonify, request

from src.services.import_service import ImportService


import_bp = Blueprint("import_bp", __name__, url_prefix="/api/import")
import_service = ImportService()


@import_bp.route("/fetch", methods=["POST"])
def fetch():
    url = request.args.get("url") or (request.get_json() or {}).get("url")
    if not url:
        return jsonify({"error": "Missing url parameter"}), 400
    try:
        resp = import_service.fetch_content(url)
        return jsonify({"status": resp.status_code, "body": resp.text[:500]})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
