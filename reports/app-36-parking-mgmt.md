# Security Report: app-36 — Parking Management System

**Language:** Javascript (Express)
**Directory:** `apps/javascript/app-36-parking-mgmt`

---

## Application Information
- **App ID:** app-36
- **Name:** Parking Management System
- **Language:** Javascript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A03 | Injection | High | src/index.js | CWE-89 |
| V2 | A04 | Insecure Design | Medium | src/index.js | CWE-20 |
| V3 | A09 | Security Logging and Monitoring Failures | Low | src/index.js | CWE-778 |

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection

- **Severity:** High
- **Location:** `src/index.js`:131-143 (method: `GET /api/spots/search`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
User search filters are concatenated directly into a raw SQL query, allowing SQL injection.

### VULN-02: A04 — Insecure Design

- **Severity:** Medium
- **Location:** `src/index.js`:156-177 (method: `POST /api/bookings/book`)
- **CWE:** [CWE-20](https://cwe.mitre.org/data/definitions/20.html)

#### Description
The booking endpoint accepts the total cost value directly from the user request payload without validation or backend recalculation, permitting free parking booking.

### VULN-03: A09 — Security Logging and Monitoring Failures

- **Severity:** Low
- **Location:** `src/index.js`:180-204 (method: `POST /api/bookings/:id/cancel`)
- **CWE:** [CWE-778](https://cwe.mitre.org/data/definitions/778.html)

#### Description
Critical operations such as booking cancellations are performed without logging the action, leaving no audit history.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: SQL Injection Data Mining → Zero-Fee Booking Exploitation

- **Combined Impact:** `data_modification`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
An attacker uses SQL Injection on the search endpoint `/api/spots/search?q=Standard' UNION SELECT 1,id,spot_number,price_rate FROM spots --` to extract spot list IDs. They then execute `/api/bookings/book` submitting a total_cost parameter set to 0.0 or negative value, booking premium parking slots for free. They cancel previous orders via `/api/bookings/1/cancel` undetected because cancellations produce no security logs.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | SQL injection reveals spots and pricing schema. | Medium | A03 | CWE-89 | src/index.js | `GET /api/spots/search` |
| 2 | Booking submission allows passing cost parameters directly without server verification. | Medium | A04 | CWE-20 | src/index.js | `POST /api/bookings/book` |

### CHAIN-02: Subtle State Confusion Pivot To Injection

- **Combined Impact:** `data_modification`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy` `secondary_chain`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
Attacker combines a low-visibility entry point with stored or derived application state, then pivots to a higher-impact sink that is reachable only after following the cross-file flow.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Critical operations such as booking cancellations are performed without logging the action, leaving no audit history. | Low | A09 | CWE-778 | src/index.js | `POST /api/bookings/:id/cancel` |
| 2 | The booking endpoint accepts the total cost value directly from the user request payload without validation or backend recalculation, permitting free parking booking. | Medium | A04 | CWE-20 | src/index.js | `POST /api/bookings/book` |
| 3 | User search filters are concatenated directly into a raw SQL query, allowing SQL injection. | High | A03 | CWE-89 | src/index.js | `GET /api/spots/search` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.js | Proper security auditing logs printed during spot registrations in POST /api/admin/spots. |
| src/index.js | Proper parameterized query logic in GET /api/spots/:id to fetch parking spot details safely. |
