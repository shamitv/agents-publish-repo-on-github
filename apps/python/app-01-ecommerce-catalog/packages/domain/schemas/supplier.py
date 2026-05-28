from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SupplierSchema:
    id: Optional[int] = None
    name: str = ""
    org_code: str = ""
    status: str = "active"
    contact_email: str = ""
