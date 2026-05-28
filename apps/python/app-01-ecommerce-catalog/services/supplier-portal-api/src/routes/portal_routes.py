"""Portal dashboard, report list, and async job routes."""

from flask import Blueprint

from ..controllers.portal_controller import (
    dashboard,
    list_reports,
    request_report,
    get_job_status,
    download_report,
    get_feature_flags,
)

portal_bp = Blueprint("portal", __name__)


@portal_bp.route("/portal/dashboard", methods=["GET"])
def dashboard_route():
    return dashboard()


@portal_bp.route("/portal/reports", methods=["GET"])
def reports_route():
    return list_reports()


@portal_bp.route("/portal/reports/request", methods=["POST"])
def request_report_route():
    return request_report()


@portal_bp.route("/portal/reports/<job_id>/status", methods=["GET"])
def job_status_route(job_id: str):
    return get_job_status(job_id)


@portal_bp.route("/portal/reports/<job_id>/download", methods=["GET"])
def download_report_route(job_id: str):
    return download_report(job_id)


@portal_bp.route("/portal/feature-flags", methods=["GET"])
def feature_flags_route():
    return get_feature_flags()
