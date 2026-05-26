# Chained Vulnerability Scenarios — Banking Service

## Chain: "Unauthenticated Account Harvest → Cookie Interception → Unlimited Fund Drain"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `GET /api/admin/users` requires no authentication — exposes every user's account number and routing number | Medium | A01 | `app.py` → `admin_list_users()` |
| 2 | Session cookie set without `Secure` flag — the cookie is transmitted in plain HTTP requests, allowing network interception | Low | A05 | `app.py` → `login()` cookie config |
| 3 | `POST /api/transfers` has no rate limit, cooldown, or transaction ceiling — an attacker can drain a full balance in seconds | High | A04 | `app.py` → `dispatch_transfer()` |


**Attack narrative**: The attacker calls `GET /api/admin/users` (no credentials needed) and collects account numbers for all users. After intercepting a session cookie over plain HTTP (no `Secure` flag means cookies travel on non-TLS connections), they use that cookie to call `POST /api/transfers` in a tight loop, transferring funds to a mule account in many small increments with zero throttle stopping them.

**Combined Impact**: Complete fund exfiltration from any compromised account.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
