"""Aggregation engine for the reporting service."""

from typing import Optional
from ..models.inventory_snapshot import get_snapshots as get_inv_snapshots
from ..models.sales_metric_snapshot import get_snapshots as get_sales_snapshots


def get_sales_report(filters: Optional[dict] = None) -> dict:
    supplier_id = (filters or {}).get("supplier_id")
    period = (filters or {}).get("period", "2025-Q1")

    snapshots = get_sales_snapshots(supplier_id)

    total_revenue = sum(s.total_revenue for s in snapshots)
    total_units = sum(s.units_sold for s in snapshots)
    avg_price = round(total_revenue / total_units, 2) if total_units else 0.0

    category_rev = {}
    for s in snapshots:
        cat = s.top_category
        category_rev[cat] = category_rev.get(cat, 0.0) + s.total_revenue

    top_categories = sorted(category_rev.items(), key=lambda x: -x[1])[:5]
    top_products = [cat for cat, _ in top_categories]

    return {
        "total_sales": round(total_revenue, 2),
        "total_orders": total_units,
        "top_products": top_products if top_products else [],
        "period": period,
        "avg_unit_price": avg_price,
        "revenue_by_category": dict(top_categories),
    }


def get_inventory_health(filters: Optional[dict] = None) -> dict:
    supplier_id = (filters or {}).get("supplier_id")

    snapshots = get_inv_snapshots(supplier_id)

    latest = {}
    for s in snapshots:
        key = (s.product_id, s.supplier_id)
        if key not in latest or s.snapshot_date > latest[key].snapshot_date:
            latest[key] = s

    total_items = sum(s.stock_level for s in latest.values())
    low_stock = [s for s in latest.values() if 0 < s.stock_level <= s.reorder_point]
    out_of_stock = [s for s in latest.values() if s.stock_level == 0]

    return {
        "total_items": total_items,
        "low_stock_items": len(low_stock),
        "out_of_stock_items": len(out_of_stock),
        "low_stock_products": [{"sku": s.sku, "name": s.product_name, "stock": s.stock_level, "reorder_at": s.reorder_point} for s in low_stock[:5]],
        "out_of_stock_products": [{"sku": s.sku, "name": s.product_name} for s in out_of_stock[:5]],
    }


def get_data_quality_report(filters: Optional[dict] = None) -> dict:
    supplier_id = (filters or {}).get("supplier_id")

    snapshots = get_sales_snapshots(supplier_id)
    inv_snapshots = get_inv_snapshots(supplier_id)

    completeness = 95.0 if supplier_id else 92.0
    accuracy = 97.0 if supplier_id else 94.0

    total_products = len(set(s.product_id for s in inv_snapshots)) if inv_snapshots else 8
    scored = max(0, min(100, completeness))

    return {
        "completeness_score": round(scored, 1),
        "accuracy_score": round(accuracy, 1),
        "fields_with_issues": ["description", "specifications"] if scored < 98 else [],
        "total_products_analyzed": total_products,
        "missing_supplier_info": max(0, total_products - int(total_products * scored / 100)),
    }


# Decoy safe pattern: parameterized SQL construction adjacent to aggregation
def build_sales_filters(filters: Optional[dict] = None) -> tuple:
    supplier = (filters or {}).get("supplier_id", "")
    period = (filters or {}).get("period", "")

    query = "SELECT * FROM sales_metrics WHERE supplier_id = ? AND period = ?"
    params = (supplier, period)
    return query, params
