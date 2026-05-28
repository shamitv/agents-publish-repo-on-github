"""Report controller for the reporting service."""

from flask import jsonify, request

from ..services.aggregation_service import (
    get_sales_report,
    get_inventory_health,
    get_data_quality_report,
)


REPORT_DEFINITIONS = [
    {"id": "sales", "name": "Sales Report", "description": "Top products by revenue, volume, and margin", "endpoint": "/v1/reports/sales"},
    {"id": "inventory", "name": "Inventory Health", "description": "Stock levels, low-stock alerts, and turnover rates", "endpoint": "/v1/reports/inventory-health"},
    {"id": "data-quality", "name": "Data Quality Score", "description": "Completeness and accuracy metrics per product", "endpoint": "/v1/reports/data-quality"},
]


def list_definitions():
    return jsonify({"definitions": REPORT_DEFINITIONS})


def sales_report():
    filters = {
        "supplier_id": request.args.get("supplier_id"),
        "period": request.args.get("period", "2025-Q1"),
    }
    # VULNERABILITY A04: no auth check — any supplier_id accepted
    data = get_sales_report(filters)
    return jsonify(data)


def inventory_health():
    filters = {
        "supplier_id": request.args.get("supplier_id"),
    }
    data = get_inventory_health(filters)
    return jsonify(data)


def data_quality():
    filters = {
        "supplier_id": request.args.get("supplier_id"),
    }
    data = get_data_quality_report(filters)
    return jsonify(data)
