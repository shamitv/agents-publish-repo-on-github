# Chained Vulnerability Scenarios — Parking Mgmt

## Chain: "SQL Injection Data Mining → Zero-Fee Booking Exploitation"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | SQL injection on spot search | High | A03 | `src/index.js` → `GET /api/spots/search` |
| 2 | Cost rates trusted directly from client parameters | Medium | A04 | `src/index.js` → `POST /api/bookings/book` |


**Attack narrative**: 1. The attacker searches spots via `/api/spots/search?q=Standard' UNION SELECT 1,id,spot_number,price_rate FROM spots --`.
2. The server processes the query and returns the list of premium spot IDs.
3. The attacker requests a booking to `/api/bookings/book` submitting a payload with `total_cost: 0.0`.
4. The server records the transaction as successful, granting free access.
5. The attacker cancels past reservations at `/api/bookings/1/cancel` without leaving an audit log trail.

**Combined Impact**: `data_modification` — Attacker bypasses payment gates to book reservation assets.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
