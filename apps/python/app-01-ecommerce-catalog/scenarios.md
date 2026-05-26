# Chained Vulnerability Scenarios — E-Commerce Product Catalog API

## Chain: "User Enumeration → Session Forge → Admin Takeover"

An attacker combines three individually low/medium-severity issues to achieve full administrative control without knowing any credentials.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `GET /api/users/exists` returns 200/404 per username — confirms valid accounts without authentication | Low | A01 | `app.py` → `user_exists()` |
| 2 | Flask `secret_key` is a hardcoded, publicly-visible string `'cyberpunk_secret_key_glow_neon_quantum_core'` in source — allows anyone with repo access to forge signed session cookies | Medium | A05 | `app.py` line 6 |
| 3 | No CSRF protection on any state-changing endpoint — forged session can invoke admin actions directly | Low | A05 | all POST endpoints |

**Attack narrative**: The attacker probes `/api/users/exists?username=admin` to confirm the admin account exists. Using the hardcoded `secret_key` (visible in source), they craft a valid Flask session cookie containing `{"user_id": 3, "username": "admin", "role": "ADMIN"}` with the `itsdangerous` library — no password needed. They then call `POST /api/products` (admin-only) to manipulate the product catalog, and dump all orders via `GET /api/orders`.

**Combined Impact**: Full admin account takeover and catalog data modification.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._