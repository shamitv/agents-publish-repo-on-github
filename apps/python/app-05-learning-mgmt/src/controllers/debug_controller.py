from flask import current_app, jsonify

from src.services.debug_service import DebugService


debug_service = DebugService()


def debug_config():
    return jsonify(debug_service.collect(current_app))
