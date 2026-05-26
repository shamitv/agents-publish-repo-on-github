# Security Report: app-36-parking-mgmt

## Application Information

- **App ID**: app-36
- **App Name**: Parking Management System
- **Language**: JavaScript
- **Framework**: Express
- **Source**: `apps/javascript/app-36-parking-mgmt/`

---

## Vulnerability Summary

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A03 | Injection | High | `src/index.js` → `GET /api/spots/search` (lines 131-143) | CWE-89 |
| V2 | A04 | Insecure Design | Medium | `src/index.js` → `POST /api/bookings/book` (lines 156-177) | CWE-20 |
| V3 | A09 | Security Logging and Monitoring Failures | Low | `src/index.js` → `POST /api/bookings/:id/cancel` (lines 180-204) | CWE-778 |

### V1: SQL Injection on Parking Spot Search

**OWASP Category**: A03 — Injection

**Description**: User search filters are concatenated directly into a raw SQL query, allowing SQL injection.

**Endpoint**: `GET /api/spots/search`

**CWE**: CWE-89 (SQL Injection)

**Impact**: High — An attacker can extract arbitrary data from the database including user credentials, spot pricing, and booking records via crafted SQL UNION payloads.

**Detection**: Search for raw string concatenation with user-supplied `q` parameter inside `db.all()` or `db.query()` calls.

---

### V2: Client-Controlled Total Cost on Booking

**OWASP Category**: A04 — Insecure Design

**Description**: The booking endpoint accepts the `total_cost` value directly from the user request payload without validation or backend recalculation, permitting free parking booking.

**Endpoint**: `POST /api/bookings/book`

**CWE**: CWE-20 (Improper Input Validation)

**Impact**: Medium — An attacker can set `total_cost` to 0.0 or a negative value, booking premium parking slots for free.

**Detection**: Look for the booking handler reading `total_cost` from `req.body` and using it directly without server-side price calculation.

---

### V3: Missing Audit Log on Booking Cancellation

**OWASP Category**: A09 — Security Logging and Monitoring Failures

**Description**: Critical operations such as booking cancellations are performed without logging the action, leaving no audit history.

**Endpoint**: `POST /api/bookings/:id/cancel`

**CWE**: CWE-778 (Insufficient Logging)

**Impact**: Low — Malicious cancellations cannot be traced back to an actor or investigated post-incident.

**Detection**: Check the cancel handler for any logging or audit trail insertion before/after updating the booking status.

---

## Chained Attack Scenario

### Chain: "SQL Injection Data Mining → Zero-Fee Booking Exploitation"

**Impact**: `data_modification`

**Overview**: An attacker uses SQL injection on the search endpoint to extract spot IDs, then exploits the client-controlled cost field to book premium spots for free.

**Components**:

| Step | Issue | Severity | OWASP | CWE | Location |
|---|---|---|---|---|---|
| 1 | SQL injection reveals spots and pricing schema | Medium | A03 | CWE-89 | `GET /api/spots/search` |
| 2 | Booking submission allows passing cost parameters directly without server verification | Medium | A04 | CWE-20 | `POST /api/bookings/book` |

**Attack Narrative**:
1. The attacker sends `GET /api/spots/search?q=Standard' UNION SELECT 1,id,spot_number,price_rate FROM spots --` to extract spot list IDs and their pricing using SQL injection.
2. The attacker then sends `POST /api/bookings/book` with a JSON body containing `total_cost: 0.0`, booking premium parking slots for free.
3. The attacker cancels previous orders via `GET /api/bookings/1/cancel` undetected because cancellations produce no security logs.

**Combined Impact**: Data modification — An attacker can book any parking spot at zero cost and cancel legitimate reservations without detection.

---

## Decoys (False-Positive Candidates)

| Location | Description |
|---|---|
| `src/index.js` | Proper security auditing logs printed during spot registrations in `POST /api/admin/spots` |
| `src/index.js` | Proper parameterized query logic in `GET /api/spots/:id` to fetch parking spot details safely |

---

## Detection Commands

```bash
# Find SQL injection vulnerable pattern
grep -n "SELECT.*\+.*req\.query" apps/javascript/app-36-parking-mgmt/src/index.js

# Find client-controlled cost acceptance
grep -n "total_cost.*req\.body" apps/javascript/app-36-parking-mgmt/src/index.js

# Find missing audit logs on cancellation
grep -n "cancel\|log\|audit" apps/javascript/app-36-parking-mgmt/src/index.js
```

---

*Report generated from `.vulns` manifest for app-36-parking-mgmt*