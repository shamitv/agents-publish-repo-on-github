from dataclasses import dataclass, field
from typing import Optional


@dataclass
class OrderItemSchema:
    name: str = ""
    sku: str = ""
    quantity: int = 0
    price: float = 0.0


@dataclass
class OrderSummarySchema:
    id: Optional[int] = None
    order_number: str = ""
    total_amount: float = 0.0
    status: str = ""
    created_at: str = ""
    username: str = ""


@dataclass
class OrderDetailSchema(OrderSummarySchema):
    items: list = field(default_factory=list)
