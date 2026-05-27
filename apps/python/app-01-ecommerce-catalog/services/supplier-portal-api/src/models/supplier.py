"""Supplier data model for the supplier portal API."""

from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class Supplier:
    """Represents a supplier who can access the portal."""
    supplier_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    tier: str = "standard"  # standard, premium, enterprise
    is_active: bool = True


# In-memory supplier store
SUPPLIERS: dict[str, Supplier] = {
    "supplier-001": Supplier(
        supplier_id="supplier-001",
        name="Acme Corp",
        email="acme@example.com",
        tier="premium",
    ),
    "supplier-002": Supplier(
        supplier_id="supplier-002",
        name="Globex Inc",
        email="globex@example.com",
        tier="standard",
    ),
    "supplier-003": Supplier(
        supplier_id="supplier-003",
        name="Initech",
        email="initech@example.com",
        tier="enterprise",
    ),
    "supplier-004": Supplier(
        supplier_id="supplier-004",
        name="Hooli Ventures",
        email="hooli@example.com",
        tier="premium",
    ),
    "supplier-005": Supplier(
        supplier_id="supplier-005",
        name="Stark Industries",
        email="stark@example.com",
        tier="enterprise",
    ),
    "supplier-006": Supplier(
        supplier_id="supplier-006",
        name="Wayne Enterprises",
        email="wayne@example.com",
        tier="standard",
    ),
    "supplier-007": Supplier(
        supplier_id="supplier-007",
        name="Oscorp",
        email="oscorp@example.com",
        tier="standard",
    ),
}


def get_supplier(supplier_id: str) -> Optional[Supplier]:
    """Look up a supplier by ID."""
    return SUPPLIERS.get(supplier_id)


def get_all_suppliers() -> list[Supplier]:
    """Return all active suppliers."""
    return [s for s in SUPPLIERS.values() if s.is_active]