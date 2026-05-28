"""Report definition data model for the supplier portal."""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import uuid


@dataclass
class ReportDefinition:
    """Defines a report type that can be generated."""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    report_type: str = ""  # sales, inventory_health, data_quality
    description: str = ""
    supplier_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


# In-memory report definition store
REPORT_DEFINITIONS: dict[str, ReportDefinition] = {
    "rpt-sales-001": ReportDefinition(
        report_id="rpt-sales-001",
        name="Monthly Sales Summary",
        report_type="sales",
        description="Aggregated sales data for the current month",
        supplier_id="supplier-001",
    ),
    "rpt-inv-001": ReportDefinition(
        report_id="rpt-inv-001",
        name="Inventory Health Report",
        report_type="inventory_health",
        description="Stock levels, low stock alerts, and reorder recommendations",
        supplier_id="supplier-001",
    ),
    "rpt-dq-001": ReportDefinition(
        report_id="rpt-dq-001",
        name="Data Quality Scorecard",
        report_type="data_quality",
        description="Completeness and accuracy metrics for product data",
        supplier_id="supplier-002",
    ),
}


def get_report_definition(report_id: str) -> Optional[ReportDefinition]:
    """Look up a report definition by ID."""
    return REPORT_DEFINITIONS.get(report_id)


def get_reports_by_supplier(supplier_id: str) -> list[ReportDefinition]:
    """Return active report definitions for a given supplier."""
    return [
        r for r in REPORT_DEFINITIONS.values()
        if r.supplier_id == supplier_id and r.is_active
    ]


def get_all_report_definitions() -> list[ReportDefinition]:
    """Return all active report definitions."""
    return [r for r in REPORT_DEFINITIONS.values() if r.is_active]