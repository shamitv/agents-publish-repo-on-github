"""Report generation routes for supplier portal API."""

from flask import Blueprint

from ..controllers.report_controller import generate_report, generate_report_safe

report_bp = Blueprint("supplier_reports", __name__)


@report_bp.route("/api/supplier/reports/<report_id>", methods=["GET"])
def get_report(report_id: str):
    """GET /api/supplier/reports/<report_id> — generate a report."""
    return generate_report(report_id)


@report_bp.route("/api/supplier/reports/<report_id>/safe", methods=["GET"])
def get_report_safe(report_id: str):
    """GET /api/supplier/reports/<report_id>/safe — scoped version (decoy)."""
    return generate_report_safe(report_id)