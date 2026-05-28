"""Dashboard aggregation service for the supplier portal."""

from ..services.report_generation_service import (
    generate_sales_report,
    generate_inventory_health_report,
    generate_data_quality_report,
)


def get_kpi_summary(supplier_id: str) -> dict:
    sales = generate_sales_report(supplier_id)
    inventory = generate_inventory_health_report(supplier_id)
    quality = generate_data_quality_report(supplier_id)

    return {
        "supplier_id": supplier_id,
        "total_sales": sales.get("total_sales", 0),
        "total_orders": sales.get("total_orders", 0),
        "low_stock_items": inventory.get("low_stock_items", 0),
        "out_of_stock_items": inventory.get("out_of_stock_items", 0),
        "data_quality_score": quality.get("completeness_score", 0),
        "top_products": sales.get("top_products", [])[:3],
    }


def get_supplier_report_list(supplier_id: str) -> list[dict]:
    from ..models.report_definition import get_reports_by_supplier

    definitions = get_reports_by_supplier(supplier_id)
    return [
        {
            "report_id": d.report_id,
            "name": d.name,
            "report_type": d.report_type,
            "description": d.description,
        }
        for d in definitions
    ]
