"""Authentication routes for the supplier portal API."""

from flask import Blueprint

from ..controllers.auth_controller import login, verify

auth_bp = Blueprint("portal_auth", __name__)


@auth_bp.route("/portal/auth/login", methods=["POST"])
def login_route():
    return login()


@auth_bp.route("/portal/auth/verify", methods=["GET"])
def verify_route():
    return verify()
