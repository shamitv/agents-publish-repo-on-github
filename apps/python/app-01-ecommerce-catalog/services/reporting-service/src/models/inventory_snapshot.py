"""Inventory snapshot data model for the reporting service."""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class InventorySnapshot:
    """Periodic stock level snapshot per product."""
    product_id: int = 0
    supplier_id: str = ""
    sku: str = ""
    product_name: str = ""
    category: str = ""
    stock_level: int = 0
    reorder_point: int = 0
    snapshot_date: str = ""


# Seed data: 25 inventory snapshots across suppliers
SNAPSHOTS: list[InventorySnapshot] = [
    InventorySnapshot(product_id=1, supplier_id="supplier-001", sku="SKU-CB-001", product_name="Neural Uplink Core v4", category="Hardware", stock_level=25, reorder_point=10, snapshot_date="2025-01-15"),
    InventorySnapshot(product_id=2, supplier_id="supplier-001", sku="SKU-CB-002", product_name="Holographic Cyber-Visor", category="Wearables", stock_level=40, reorder_point=15, snapshot_date="2025-01-15"),
    InventorySnapshot(product_id=3, supplier_id="supplier-001", sku="SKU-CB-003", product_name="Subdermal Armor Plating", category="Cyberware", stock_level=15, reorder_point=5, snapshot_date="2025-01-15"),
    InventorySnapshot(product_id=4, supplier_id="supplier-002", sku="SKU-CB-004", product_name="Monofilament Laser-Whip", category="Tactical", stock_level=10, reorder_point=8, snapshot_date="2025-01-15"),
    InventorySnapshot(product_id=5, supplier_id="supplier-002", sku="SKU-CB-005", product_name="Neon Mesh Trenchcoat", category="Apparel", stock_level=50, reorder_point=20, snapshot_date="2025-01-15"),
    InventorySnapshot(product_id=6, supplier_id="supplier-002", sku="SKU-CB-006", product_name="Decrypted Netrunner Deck", category="Hardware", stock_level=8, reorder_point=5, snapshot_date="2025-01-15"),
    InventorySnapshot(product_id=7, supplier_id="supplier-003", sku="SKU-CB-007", product_name="Glitch-Art Decal Sticker Pack", category="Apparel", stock_level=100, reorder_point=30, snapshot_date="2025-01-15"),
    InventorySnapshot(product_id=8, supplier_id="supplier-003", sku="SKU-CB-008", product_name="Portable Ice-Pick Exploit", category="Tactical", stock_level=12, reorder_point=6, snapshot_date="2025-01-15"),
    # Low stock scenarios
    InventorySnapshot(product_id=1, supplier_id="supplier-001", sku="SKU-CB-001", product_name="Neural Uplink Core v4", category="Hardware", stock_level=3, reorder_point=10, snapshot_date="2025-02-01"),
    InventorySnapshot(product_id=3, supplier_id="supplier-001", sku="SKU-CB-003", product_name="Subdermal Armor Plating", category="Cyberware", stock_level=2, reorder_point=5, snapshot_date="2025-02-01"),
    InventorySnapshot(product_id=4, supplier_id="supplier-002", sku="SKU-CB-004", product_name="Monofilament Laser-Whip", category="Tactical", stock_level=1, reorder_point=8, snapshot_date="2025-02-01"),
    InventorySnapshot(product_id=6, supplier_id="supplier-002", sku="SKU-CB-006", product_name="Decrypted Netrunner Deck", category="Hardware", stock_level=0, reorder_point=5, snapshot_date="2025-02-01"),
    # Out of stock scenarios
    InventorySnapshot(product_id=4, supplier_id="supplier-002", sku="SKU-CB-004", product_name="Monofilament Laser-Whip", category="Tactical", stock_level=0, reorder_point=8, snapshot_date="2025-02-15"),
    InventorySnapshot(product_id=8, supplier_id="supplier-003", sku="SKU-CB-008", product_name="Portable Ice-Pick Exploit", category="Tactical", stock_level=0, reorder_point=6, snapshot_date="2025-02-15"),
    # Restocked
    InventorySnapshot(product_id=1, supplier_id="supplier-001", sku="SKU-CB-001", product_name="Neural Uplink Core v4", category="Hardware", stock_level=20, reorder_point=10, snapshot_date="2025-03-01"),
    InventorySnapshot(product_id=3, supplier_id="supplier-001", sku="SKU-CB-003", product_name="Subdermal Armor Plating", category="Cyberware", stock_level=12, reorder_point=5, snapshot_date="2025-03-01"),
    InventorySnapshot(product_id=5, supplier_id="supplier-002", sku="SKU-CB-005", product_name="Neon Mesh Trenchcoat", category="Apparel", stock_level=35, reorder_point=20, snapshot_date="2025-03-01"),
    InventorySnapshot(product_id=7, supplier_id="supplier-003", sku="SKU-CB-007", product_name="Glitch-Art Decal Sticker Pack", category="Apparel", stock_level=80, reorder_point=30, snapshot_date="2025-03-01"),
    # Additional snapshots for variety
    InventorySnapshot(product_id=2, supplier_id="supplier-001", sku="SKU-CB-002", product_name="Holographic Cyber-Visor", category="Wearables", stock_level=28, reorder_point=15, snapshot_date="2025-03-15"),
    InventorySnapshot(product_id=6, supplier_id="supplier-002", sku="SKU-CB-006", product_name="Decrypted Netrunner Deck", category="Hardware", stock_level=5, reorder_point=5, snapshot_date="2025-03-15"),
    InventorySnapshot(product_id=8, supplier_id="supplier-003", sku="SKU-CB-008", product_name="Portable Ice-Pick Exploit", category="Tactical", stock_level=7, reorder_point=6, snapshot_date="2025-03-15"),
    InventorySnapshot(product_id=2, supplier_id="supplier-001", sku="SKU-CB-002", product_name="Holographic Cyber-Visor", category="Wearables", stock_level=5, reorder_point=15, snapshot_date="2025-04-01"),
    InventorySnapshot(product_id=5, supplier_id="supplier-002", sku="SKU-CB-005", product_name="Neon Mesh Trenchcoat", category="Apparel", stock_level=10, reorder_point=20, snapshot_date="2025-04-01"),
    InventorySnapshot(product_id=7, supplier_id="supplier-003", sku="SKU-CB-007", product_name="Glitch-Art Decal Sticker Pack", category="Apparel", stock_level=60, reorder_point=30, snapshot_date="2025-04-01"),
    InventorySnapshot(product_id=3, supplier_id="supplier-001", sku="SKU-CB-003", product_name="Subdermal Armor Plating", category="Cyberware", stock_level=8, reorder_point=5, snapshot_date="2025-04-01"),
]


def get_snapshots(supplier_id: Optional[str] = None) -> list[InventorySnapshot]:
    if supplier_id:
        return [s for s in SNAPSHOTS if s.supplier_id == supplier_id]
    return SNAPSHOTS
