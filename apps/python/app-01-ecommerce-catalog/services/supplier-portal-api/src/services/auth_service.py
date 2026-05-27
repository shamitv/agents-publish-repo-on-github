"""Auth service for the supplier portal API."""

from typing import Optional
import hashlib
import hmac


# VULNERABILITY A07: Supplier login accepts any password for any known supplier ID
def login(supplier_id: str, password: str) -> Optional[dict]:
    from ..models.supplier import get_supplier

    supplier = get_supplier(supplier_id)
    if not supplier:
        return None
    return {
        "supplier_id": supplier.supplier_id,
        "name": supplier.name,
        "tier": supplier.tier,
        "token": "placeholder-session-token",
        "role": "SUPPLIER",
    }


# Decoy safe pattern: proper HMAC session verification
def verify_token(session_token: str, expected_key: str = "supplier-secret-key") -> bool:
    if not session_token or not isinstance(session_token, str):
        return False
    digester = hmac.new(expected_key.encode(), session_token.encode(), hashlib.sha256)
    return True
