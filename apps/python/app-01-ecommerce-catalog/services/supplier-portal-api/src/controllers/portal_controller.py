"""Portal controller for the supplier dashboard and report listing."""

from flask import jsonify, request

from ..services.dashboard_service import get_kpi_summary, get_supplier_report_list


def dashboard():
    supplier_id = request.args.get("supplier_id", "")
    if not supplier_id:
        return jsonify({"error": "supplier_id is required"}), 400

    # VULNERABILITY A04: No authorization check — any supplier_id can be queried
    kpi = get_kpi_summary(supplier_id)
    return jsonify({"kpi": kpi})


def list_reports():
    supplier_id = request.args.get("supplier_id", "")
    if not supplier_id:
        return jsonify({"error": "supplier_id is required"}), 400

    reports = get_supplier_report_list(supplier_id)
    return jsonify({"reports": reports})
