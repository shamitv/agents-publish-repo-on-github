"""Sales metric snapshot data model for the reporting service."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SalesMetricSnapshot:
    """Periodic sales metric aggregation."""
    supplier_id: str = ""
    date: str = ""
    total_revenue: float = 0.0
    units_sold: int = 0
    avg_price: float = 0.0
    top_category: str = ""


# Seed data: 55 sales metric snapshots across 3 suppliers over Q1 2025
WEEKS = [f"2025-W{str(w).zfill(2)}" for w in range(1, 14)]
_DAILY = [f"2025-01-{str(d).zfill(2)}" for d in range(1, 32)] + \
         [f"2025-02-{str(d).zfill(2)}" for d in range(1, 29)] + \
         [f"2025-03-{str(d).zfill(2)}" for d in range(1, 32)]

SNAPSHOTS: list[SalesMetricSnapshot] = [
    # Supplier-001 weekly sales
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-01-07", total_revenue=28500.0, units_sold=42, avg_price=678.0, top_category="Hardware"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-01-14", total_revenue=32000.0, units_sold=48, avg_price=666.0, top_category="Cyberware"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-01-21", total_revenue=29800.0, units_sold=45, avg_price=662.0, top_category="Hardware"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-01-28", total_revenue=35200.0, units_sold=51, avg_price=690.0, top_category="Wearables"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-02-04", total_revenue=27500.0, units_sold=38, avg_price=723.0, top_category="Cyberware"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-02-11", total_revenue=31000.0, units_sold=44, avg_price=704.0, top_category="Hardware"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-02-18", total_revenue=33800.0, units_sold=49, avg_price=689.0, top_category="Wearables"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-02-25", total_revenue=29100.0, units_sold=41, avg_price=709.0, top_category="Cyberware"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-03-04", total_revenue=36500.0, units_sold=53, avg_price=688.0, top_category="Hardware"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-03-11", total_revenue=34200.0, units_sold=50, avg_price=684.0, top_category="Hardware"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-03-18", total_revenue=38800.0, units_sold=56, avg_price=692.0, top_category="Wearables"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-03-25", total_revenue=29800.0, units_sold=43, avg_price=693.0, top_category="Cyberware"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-04-01", total_revenue=6500.0, units_sold=9, avg_price=722.0, top_category="Hardware"),
    # Supplier-002 weekly sales
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-01-07", total_revenue=18500.0, units_sold=95, avg_price=194.0, top_category="Apparel"),
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-01-14", total_revenue=21000.0, units_sold=108, avg_price=194.0, top_category="Tactical"),
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-01-21", total_revenue=19800.0, units_sold=102, avg_price=194.0, top_category="Apparel"),
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-01-28", total_revenue=22400.0, units_sold=115, avg_price=194.0, top_category="Tactical"),
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-02-04", total_revenue=19200.0, units_sold=98, avg_price=195.0, top_category="Apparel"),
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-02-11", total_revenue=21500.0, units_sold=110, avg_price=195.0, top_category="Hardware"),
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-02-18", total_revenue=23100.0, units_sold=118, avg_price=195.0, top_category="Apparel"),
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-02-25", total_revenue=20500.0, units_sold=105, avg_price=195.0, top_category="Tactical"),
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-03-04", total_revenue=24200.0, units_sold=124, avg_price=195.0, top_category="Apparel"),
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-03-11", total_revenue=22800.0, units_sold=117, avg_price=194.0, top_category="Tactical"),
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-03-18", total_revenue=25500.0, units_sold=130, avg_price=196.0, top_category="Hardware"),
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-03-25", total_revenue=21800.0, units_sold=112, avg_price=194.0, top_category="Apparel"),
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-04-01", total_revenue=4200.0, units_sold=21, avg_price=200.0, top_category="Tactical"),
    # Supplier-003 weekly sales
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-01-07", total_revenue=45000.0, units_sold=180, avg_price=250.0, top_category="Apparel"),
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-01-14", total_revenue=52000.0, units_sold=210, avg_price=247.0, top_category="Tactical"),
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-01-21", total_revenue=48500.0, units_sold=195, avg_price=248.0, top_category="Apparel"),
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-01-28", total_revenue=51000.0, units_sold=205, avg_price=248.0, top_category="Tactical"),
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-02-04", total_revenue=47000.0, units_sold=188, avg_price=250.0, top_category="Apparel"),
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-02-11", total_revenue=53500.0, units_sold=215, avg_price=248.0, top_category="Tactical"),
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-02-18", total_revenue=49800.0, units_sold=200, avg_price=249.0, top_category="Apparel"),
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-02-25", total_revenue=46200.0, units_sold=185, avg_price=249.0, top_category="Hardware"),
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-03-04", total_revenue=54800.0, units_sold=220, avg_price=249.0, top_category="Tactical"),
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-03-11", total_revenue=51500.0, units_sold=208, avg_price=247.0, top_category="Apparel"),
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-03-18", total_revenue=56200.0, units_sold=225, avg_price=249.0, top_category="Tactical"),
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-03-25", total_revenue=48900.0, units_sold=198, avg_price=246.0, top_category="Apparel"),
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-04-01", total_revenue=9800.0, units_sold=39, avg_price=251.0, top_category="Tactical"),
    # Daily details for supplier-001 (more granular)
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-01-05", total_revenue=4200.0, units_sold=6, avg_price=700.0, top_category="Hardware"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-01-06", total_revenue=3800.0, units_sold=5, avg_price=760.0, top_category="Cyberware"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-01-12", total_revenue=5100.0, units_sold=7, avg_price=728.0, top_category="Hardware"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-01-13", total_revenue=4500.0, units_sold=6, avg_price=750.0, top_category="Wearables"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-01-19", total_revenue=4900.0, units_sold=7, avg_price=700.0, top_category="Cyberware"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-01-20", total_revenue=5200.0, units_sold=8, avg_price=650.0, top_category="Hardware"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-01-26", total_revenue=4800.0, units_sold=6, avg_price=800.0, top_category="Wearables"),
    SalesMetricSnapshot(supplier_id="supplier-001", date="2025-01-27", total_revenue=5500.0, units_sold=8, avg_price=687.0, top_category="Hardware"),
    # Daily for supplier-002
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-01-05", total_revenue=2800.0, units_sold=14, avg_price=200.0, top_category="Apparel"),
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-01-06", total_revenue=3200.0, units_sold=16, avg_price=200.0, top_category="Tactical"),
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-01-12", total_revenue=3000.0, units_sold=15, avg_price=200.0, top_category="Apparel"),
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-01-13", total_revenue=3500.0, units_sold=18, avg_price=194.0, top_category="Tactical"),
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-01-19", total_revenue=2900.0, units_sold=14, avg_price=207.0, top_category="Apparel"),
    SalesMetricSnapshot(supplier_id="supplier-002", date="2025-01-26", total_revenue=3400.0, units_sold=17, avg_price=200.0, top_category="Hardware"),
    # Daily for supplier-003
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-01-05", total_revenue=6800.0, units_sold=27, avg_price=251.0, top_category="Tactical"),
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-01-06", total_revenue=7200.0, units_sold=29, avg_price=248.0, top_category="Apparel"),
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-01-12", total_revenue=7500.0, units_sold=30, avg_price=250.0, top_category="Tactical"),
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-01-19", total_revenue=6900.0, units_sold=28, avg_price=246.0, top_category="Apparel"),
    SalesMetricSnapshot(supplier_id="supplier-003", date="2025-01-26", total_revenue=8100.0, units_sold=32, avg_price=253.0, top_category="Hardware"),
]


def get_snapshots(supplier_id: Optional[str] = None) -> list[SalesMetricSnapshot]:
    if supplier_id:
        return [s for s in SNAPSHOTS if s.supplier_id == supplier_id]
    return SNAPSHOTS
