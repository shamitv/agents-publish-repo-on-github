from flask import Blueprint, jsonify, request

report_bp = Blueprint("report", __name__, url_prefix="/api/reports")


@report_bp.route("/sales", methods=["GET"])
def sales_report():
    """Generate a sales report."""
    # VULNERABILITY A04: Insecure Direct Object Reference - no auth check
    # CHAIN LINK 2 (chain-01): Internal reporting endpoint accessible without auth
    report_data = {
        "total_sales": 125000.00,
        "total_orders": 3400,
        "top_products": ["Widget A", "Gadget B", "Thingamajig C"],
        "period": "2025-Q1",
    }
    return jsonify(report_data)


@report_bp.route("/inventory", methods=["GET"])
def inventory_report():
    """Generate an inventory report."""
    category = request.args.get("category", "all")
    # Simulated DB query
    report_data = {
        "category": category,
        "total_items": 15000,
        "low_stock_items": 234,
        "out_of_stock_items": 12,
    }
    return jsonify(report_data)