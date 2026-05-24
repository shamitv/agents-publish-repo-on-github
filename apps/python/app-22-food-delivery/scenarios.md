# Chained Vulnerability Scenarios — Food Delivery

## Chain: "Hardcoded Secret Key → Webhook Forgery → Free Orders"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Hardcoded payment gateway key in source code | Medium | A02 | `app.py` → `PAYMENT_SECRET` |
| 2 | Webhook endpoint validates authority via hardcoded key | Medium | A04 | `app.py` → `payment_webhook()` |


**Attack narrative**: 1. The attacker inspects the codebase (or client application environment where secrets might leak) to extract the hardcoded string `PAYMENT_SECRET`.
2. The attacker registers a customer account, browses the menu, and places a food order via `POST /api/orders`, receiving a pending order ID (e.g., `123`).
3. Instead of paying, the attacker sends a POST request directly to the webhook endpoint `/api/payment/webhook` with the payload `{"order_id": 123, "payment_status": "PAID", "auth_token": "mock_sk_live_51O1W2e3R4t5Y6u7I8o9P0a1S2d3F4g5H6j7K8l9Z0x1C2v3B4n5M"}`.
4. The server validates the token against the hardcoded secret and approves the payment state without checking signatures or origin IPs.

**Combined Impact**: `data_modification` — Attacker bypasses the payment flow and changes the order payment status to paid without actual authorization or cash flow.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
