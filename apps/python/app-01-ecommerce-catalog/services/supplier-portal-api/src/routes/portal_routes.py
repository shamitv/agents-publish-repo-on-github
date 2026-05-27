"""Portal dashboard and report list routes."""

from flask import Blueprint

from ..controllers.portal_controller import dashboard, list_reports

portal_bp = Blueprint("portal", __name__)


@portal_bp.route("/portal/dashboard", methods=["GET"])
def dashboard_route():
    return dashboard()


@portal_bp.route("/portal/reports", methods=["GET"])
def reports_route():
    return list_reports()
