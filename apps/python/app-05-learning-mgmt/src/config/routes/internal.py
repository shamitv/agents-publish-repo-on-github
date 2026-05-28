import os
import platform

from flask import Blueprint, jsonify


internal_bp = Blueprint("internal", __name__, url_prefix="/admin/internal")


@internal_bp.route("/metrics", methods=["GET"])
def metrics():
    return jsonify({
        "hostname": platform.node(),
        "python_version": platform.python_version(),
        "pid": os.getpid(),
        "cwd": os.getcwd(),
        "internal_services": {
            "postgresql": "db:5432",
            "mongodb": "mongodb:27017",
            "kafka": "kafka:9092",
        },
        "active_connections": "simulated",
    })
