from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProductSchema:
    id: Optional[int] = None
    sku: str = ""
    name: str = ""
    description: str = ""
    category: str = ""
    price: float = 0.0
    quantity: int = 0
