# Security Report: app-31 — Event Ticketing Platform

**Language:** Typescript (Express)
**Directory:** `apps/typescript/app-31-event-ticketing`

---

## Application Information
- **App ID:** app-31
- **Name:** Event Ticketing Platform
- **Language:** Typescript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A03 | Injection | High | src/index.ts | CWE-89 |
| V2 | A04 | Insecure Design | Medium | src/index.ts | CWE-400 |
| V3 | A07 | Identification and Authentication Failures | Medium | src/index.ts | CWE-330 |

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection

- **Severity:** High
- **Location:** `src/index.ts`:148-161 (method: `GET /api/events/search`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
Event search endpoint concatenates user search queries directly into raw SQL statements, exposing the system to SQL injection.

### VULN-02: A04 — Insecure Design

- **Severity:** Medium
- **Location:** `src/index.ts`:176-223 (method: `POST /api/tickets/book`)
- **CWE:** [CWE-400](https://cwe.mitre.org/data/definitions/400.html)

#### Description
The ticket booking endpoint lacks rate limits, transactional locking, or concurrency limits, permitting automated scripting to deplete ticket inventories.

### VULN-03: A07 — Identification and Authentication Failures

- **Severity:** Medium
- **Location:** `src/index.ts`:126-130 (method: `login`)
- **CWE:** [CWE-330](https://cwe.mitre.org/data/definitions/330.html)

#### Description
Session identifiers are generated using Math.random() (a predictable PRNG) instead of cryptographically secure random values, permitting session hijacking.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Predictable Session Hijacking → SQLi Ticket Theft

- **Combined Impact:** `account_takeover`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
An attacker predicts the session tokens of other active customers due to the use of Math.random(). They hijack a customer's session, execute SQL injection on the event search to dump private ticket orders, and cancel or steal premium reservations.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Weak session token generation via predictable random number generator. | Medium | A07 | CWE-330 | src/index.ts | `login` |
| 2 | SQL injection in event search reveals customer details and transaction info. | Medium | A03 | CWE-89 | src/index.ts | `GET /api/events/search` |

### CHAIN-02: Subtle Auth Session Pivot To Injection

- **Combined Impact:** `account_takeover`
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
| 1 | Session identifiers are generated using Math.random() (a predictable PRNG) instead of cryptographically secure random values, permitting session hijacking. | Medium | A07 | CWE-330 | src/index.ts | `login` |
| 2 | The ticket booking endpoint lacks rate limits, transactional locking, or concurrency limits, permitting automated scripting to deplete ticket inventories. | Medium | A04 | CWE-400 | src/index.ts | `POST /api/tickets/book` |
| 3 | Event search endpoint concatenates user search queries directly into raw SQL statements, exposing the system to SQL injection. | High | A03 | CWE-89 | src/index.ts | `GET /api/events/search` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.ts | Proper Bcrypt hashing for password storage and credentials checking during login. |
| src/index.ts | Proper parameterized SQL query for retrieving individual event details by event ID. |
