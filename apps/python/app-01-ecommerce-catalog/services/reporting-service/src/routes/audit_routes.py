"""Audit log routes for the reporting service."""

from flask import Blueprint

from ..controllers.audit_controller import query_audit

audit_bp = Blueprint("audit", __name__, url_prefix="/v1/reports")


@audit_bp.route("/audit", methods=["GET"])
def audit():
    return query_audit()
