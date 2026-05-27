"""Sync report generation service for supplier portal."""

from typing import Any
from datetime import datetime


def generate_sales_report(supplier_id: str, period: str = "2025-Q1") -> dict[str, Any]:
    """Generate a sales report for a given supplier and period.

    VULNERABILITY A04: No authorization check — any supplier ID can be passed.
    CHAIN LINK 2 (chain-01): Internal report data accessible without proper auth.
    """
    mock_sales_data = {
        "supplier-001": {
            "total_sales": 125000.00,
            "total_orders": 3400,
            "top_products": ["Widget A", "Gadget B", "Thingamajig C"],
        },
        "supplier-002": {
            "total_sales": 87000.00,
            "total_orders": 2100,
            "top_products": ["Doodad X", "Gizmo Y"],
        },
        "supplier-003": {
            "total_sales": 210000.00,
            "total_orders": 5600,
            "top_products": ["Contraption Z", "Widget A", "Gadget B"],
        },
    }
    data = mock_sales_data.get(supplier_id, mock_sales_data["supplier-001"])
    return {
        "supplier_id": supplier_id,
        "period": period,
        **data,
        "generated_at": datetime.utcnow().isoformat(),
    }


def generate_inventory_health_report(supplier_id: str) -> dict[str, Any]:
    """Generate an inventory health report."""
    mock_inventory_data = {
        "supplier-001": {
            "total_items": 15000,
            "low_stock_items": 234,
            "out_of_stock_items": 12,
            "reorder_recommendations": ["Widget A", "Gadget B"],
        },
        "supplier-002": {
            "total_items": 8200,
            "low_stock_items": 98,
            "out_of_stock_items": 5,
            "reorder_recommendations": ["Doodad X"],
        },
        "supplier-003": {
            "total_items": 45000,
            "low_stock_items": 512,
            "out_of_stock_items": 28,
            "reorder_recommendations": ["Contraption Z", "Widget A"],
        },
    }
    data = mock_inventory_data.get(supplier_id, mock_inventory_data["supplier-001"])
    return {
        "supplier_id": supplier_id,
        **data,
        "generated_at": datetime.utcnow().isoformat(),
    }


def generate_data_quality_report(supplier_id: str) -> dict[str, Any]:
    """Generate a data quality scorecard."""
    mock_dq_data = {
        "supplier-001": {
            "completeness_score": 94.2,
            "accuracy_score": 97.8,
            "fields_with_issues": ["description", "specifications"],
        },
        "supplier-002": {
            "completeness_score": 88.5,
            "accuracy_score": 91.3,
            "fields_with_issues": ["description", "price", "images"],
        },
        "supplier-003": {
            "completeness_score": 99.1,
            "accuracy_score": 98.9,
            "fields_with_issues": [],
        },
    }
    data = mock_dq_data.get(supplier_id, mock_dq_data["supplier-001"])
    return {
        "supplier_id": supplier_id,
        **data,
        "generated_at": datetime.utcnow().isoformat(),
    }


# Decoy safe pattern: proper auth-checked version that verifies supplier identity
def generate_sales_report_safe(supplier_id: str, auth_supplier_id: str, period: str = "2025-Q1") -> dict[str, Any]:
    """Safe version with authorization check — decoy for precision testing."""
    if supplier_id != auth_supplier_id:
        return {"error": "Unauthorized", "status": 403}
    return generate_sales_report(supplier_id, period)