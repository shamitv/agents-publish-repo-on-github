"""Webhook subscription data model for the reporting service."""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import uuid


@dataclass
class WebhookSubscription:
    """Represents a supplier's webhook registration."""
    subscription_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    supplier_id: str = ""
    callback_url: str = ""
    secret_token: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


# In-memory subscription store
SUBSCRIPTIONS: dict[str, WebhookSubscription] = {}


def create_subscription(supplier_id: str, callback_url: str, secret_token: str = "") -> WebhookSubscription:
    sub = WebhookSubscription(
        supplier_id=supplier_id,
        callback_url=callback_url,
        secret_token=secret_token,
    )
    SUBSCRIPTIONS[sub.subscription_id] = sub
    return sub


def get_subscription(subscription_id: str) -> Optional[WebhookSubscription]:
    return SUBSCRIPTIONS.get(subscription_id)


def get_subscriptions(supplier_id: Optional[str] = None) -> list[WebhookSubscription]:
    if supplier_id:
        return [s for s in SUBSCRIPTIONS.values() if s.supplier_id == supplier_id and s.is_active]
    return [s for s in SUBSCRIPTIONS.values() if s.is_active]


def delete_subscription(subscription_id: str) -> bool:
    sub = SUBSCRIPTIONS.get(subscription_id)
    if not sub:
        return False
    sub.is_active = False
    return True
