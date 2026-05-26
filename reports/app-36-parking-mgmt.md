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
| V1 | A03 | Injection | High | src/search/ParkingSearchClient.js | CWE-74 |
| V2 | A04 | Insecure Design | Medium | src/services/BookingService.js | CWE-20 |
| V3 | A09 | Security Logging and Monitoring Failures | Low | src/services/BookingService.js | CWE-778 |

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection

- **Severity:** High
- **Location:** `src/search/ParkingSearchClient.js`:7-31 (method: `searchByQueryString`)
- **CWE:** [CWE-74](https://cwe.mitre.org/data/definitions/74.html)

#### Description
Parking search embeds user input directly in Elasticsearch query_string syntax.

### VULN-02: A04 — Insecure Design

- **Severity:** Medium
- **Location:** `src/services/BookingService.js`:8-21 (method: `book`)
- **CWE:** [CWE-20](https://cwe.mitre.org/data/definitions/20.html)

#### Description
Booking creation accepts totalCost directly from the client without server-side recalculation.

### VULN-03: A09 — Security Logging and Monitoring Failures

- **Severity:** Low
- **Location:** `src/services/BookingService.js`:24-36 (method: `cancel`)
- **CWE:** [CWE-778](https://cwe.mitre.org/data/definitions/778.html)

#### Description
Booking cancellation persists a critical booking mutation without publishing a security audit event.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Elasticsearch Query Injection → Client-Controlled Pricing → Missing Audit Logs → Data Modification

- **Combined Impact:** `data_modification`
- **Difficulty:** Medium
- **Subtlety Tags:** 

#### Prerequisites
- None specified

#### Attack Narrative
An attacker uses Elasticsearch query_string syntax to broaden parking search results, books a premium spot with a client-controlled zero or negative total cost, and cancels bookings without an audit event.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Parking search embeds raw user input in Elasticsearch query_string syntax. | Medium | A03 | CWE-74 | src/search/ParkingSearchClient.js | `searchByQueryString` |
| 2 | Booking price is trusted from the client instead of recalculated from spot rate and duration. | Medium | A04 | CWE-20 | src/services/BookingService.js | `book` |
| 3 | Booking cancellation is persisted without a security audit event. | Low | A09 | CWE-778 | src/services/BookingService.js | `cancel` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/services/SpotService.js | Admin spot creation publishes a security audit event and logs the spot registration. |
| src/controllers/SpotController.js | Spot detail lookup uses repository findById rather than constructing a query string. |
| src/referenceGuards.js | Reference callback allowlist guard demonstrates safe URL validation. |
