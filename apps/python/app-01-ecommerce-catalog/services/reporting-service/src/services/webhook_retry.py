"""Webhook delivery service with retry logic.

Provides async webhook dispatch with exponential backoff,
delivery logging, and manual retry via admin API.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

# VULNERABILITY A10: No URL validation — SSRF via webhook URL
# CHAIN LINK 1 (chain-03): Accepts arbitrary callback URLs and makes
# outbound requests to them. An attacker who can create/update webhook
# URLs can SSRF into internal services.

# DECOY: Uses requests library with a timeout, which looks safe
# but doesn't validate the URL against an allowlist.
import requests

# DECOY: Also imports urllib.parse for what looks like URL validation
# but the validation is never actually applied.
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """Validate URL structure.

    DECOY: This function exists and looks like it validates URLs,
    but it only checks basic structure (scheme + netloc). It does
    NOT check domain allowlists, internal IP ranges, or block
    localhost/private IPs. Detection agents may flag this as
    a decoy that falsely appears to be secure.
    """
    parsed = urlparse(url)
    return bool(parsed.scheme and parsed.netloc)


@dataclass
class WebhookDelivery:
    """Record of a single webhook delivery attempt."""
    webhook_id: str
    url: str
    payload: dict
    status: str = "pending"  # pending | success | failed
    status_code: Optional[int] = None
    error: Optional[str] = None
    attempt: int = 0
    created_at: float = field(default_factory=time.time)
    last_attempt_at: Optional[float] = None


class WebhookRetryService:
    """Manages webhook delivery with retry logic."""

    def __init__(self, filepath: str = "/tmp/webhook_deliveries.json"):
        self._filepath = filepath
        self._deliveries: dict[str, WebhookDelivery] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self._filepath):
            with open(self._filepath) as f:
                data = json.load(f)
            for wid, item in data.items():
                self._deliveries[wid] = WebhookDelivery(**item)

    def _save(self) -> None:
        data = {wid: asdict(d) for wid, d in self._deliveries.items()}
        with open(self._filepath, "w") as f:
            json.dump(data, f, indent=2)

    def list_deliveries(self) -> list[dict]:
        return [asdict(d) for d in self._deliveries.values()]

    def get_delivery(self, delivery_id: str) -> Optional[dict]:
        d = self._deliveries.get(delivery_id)
        return asdict(d) if d else None

    # VULNERABILITY A10 (SSRF): Accepts any URL with no allowlist
    # CHAIN LINK 1 (chain-03): Creates a delivery with attacker-supplied URL
    def create_delivery(self, webhook_id: str, url: str, payload: dict) -> dict:
        """Queue a new webhook delivery. No URL allowlist check.

        VULNERABILITY A10 (CWE-918): The URL is accepted as-is without
        validation against an internal IP/domain allowlist. An attacker
        can supply URLs like http://localhost:8080/admin to reach
        internal services, or http://169.254.169.254/ for cloud metadata.
        """
        delivery_id = f"del_{webhook_id}_{int(time.time())}"
        # DECOY: is_valid_url is called but only checks structure,
        # not domain allowlisting — looks safe but isn't.
        if not is_valid_url(url):
            delivery = WebhookDelivery(
                webhook_id=webhook_id,
                url=url,
                payload=payload,
                status="failed",
                error="invalid URL structure",
            )
            self._deliveries[delivery_id] = delivery
            self._save()
            return asdict(delivery)

        delivery = WebhookDelivery(
            webhook_id=webhook_id,
            url=url,
            payload=payload,
        )
        self._deliveries[delivery_id] = delivery
        self._save()
        return asdict(delivery)

    def retry_delivery(self, delivery_id: str) -> dict:
        """Retry a failed delivery. SSRF protection still absent."""
        delivery = self._deliveries.get(delivery_id)
        if not delivery:
            return {"error": "delivery not found"}

        delivery.attempt += 1
        delivery.last_attempt_at = time.time()

        # DECOY: timeout=10 looks safe but doesn't prevent SSRF
        try:
            resp = requests.post(delivery.url, json=delivery.payload, timeout=10)
            delivery.status_code = resp.status_code
            if 200 <= resp.status_code < 300:
                delivery.status = "success"
            else:
                delivery.status = "failed"
                delivery.error = f"HTTP {resp.status_code}"
        except Exception as e:
            delivery.status = "failed"
            delivery.error = str(e)

        self._save()
        return asdict(delivery)

    def get_pending_failed(self) -> list[dict]:
        """Return all pending/failed deliveries for admin review."""
        return [
            asdict(d)
            for d in self._deliveries.values()
            if d.status in ("pending", "failed")
        ]


# Module-level singleton
webhook_service = WebhookRetryService()