"""Controller for report generation endpoints."""

from flask import jsonify, request

from ..services.report_generation_service import (
    generate_sales_report,
    generate_inventory_health_report,
    generate_data_quality_report,
)
from ..models.report_definition import get_report_definition


def generate_report(report_id: str):
    """Generate a report by its definition ID.

    VULNERABILITY A04: No authorization check — any report can be generated
    for any supplier by passing arbitrary supplier_id in query params.
    CHAIN LINK 2 (chain-01): Report generation lacks supplier scoping.
    """
    report_def = get_report_definition(report_id)
    if not report_def:
        return jsonify({"error": "Report definition not found"}), 404

    supplier_id = request.args.get("supplier_id", report_def.supplier_id)

    if report_def.report_type == "sales":
        period = request.args.get("period", "2025-Q1")
        data = generate_sales_report(supplier_id, period)
    elif report_def.report_type == "inventory_health":
        data = generate_inventory_health_report(supplier_id)
    elif report_def.report_type == "data_quality":
        data = generate_data_quality_report(supplier_id)
    else:
        return jsonify({"error": "Unknown report type"}), 400

    return jsonify({
        "report_id": report_id,
        "report_name": report_def.name,
        "report_type": report_def.report_type,
        **data,
    })


# Decoy safe pattern: proper scoped report retrieval
def generate_report_safe(report_id: str):
    """Safe version that enforces supplier scoping — decoy for precision testing."""
    report_def = get_report_definition(report_id)
    if not report_def:
        return jsonify({"error": "Report definition not found"}), 404

    auth_supplier_id = request.headers.get("X-Supplier-ID", "")
    supplier_id = request.args.get("supplier_id", report_def.supplier_id)

    if supplier_id != auth_supplier_id:
        return jsonify({"error": "Unauthorized", "status": 403}), 403

    if report_def.report_type == "sales":
        period = request.args.get("period", "2025-Q1")
        data = generate_sales_report(supplier_id, period)
    elif report_def.report_type == "inventory_health":
        data = generate_inventory_health_report(supplier_id)
    elif report_def.report_type == "data_quality":
        data = generate_data_quality_report(supplier_id)
    else:
        return jsonify({"error": "Unknown report type"}), 400

    return jsonify({
        "report_id": report_id,
        "report_name": report_def.name,
        "report_type": report_def.report_type,
        **data,
    })