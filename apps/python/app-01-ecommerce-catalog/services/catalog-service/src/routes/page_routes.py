from flask import Blueprint, current_app, send_from_directory


pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def serve_index():
    return current_app.send_static_file("index.html")


@pages_bp.route("/<path:path>")
def serve_static(path):
    return send_from_directory(current_app.static_folder, path)
