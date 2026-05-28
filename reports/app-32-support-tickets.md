# Security Report: app-32 — Customer Support Ticket System

**Language:** Typescript (Express)
**Directory:** `apps/typescript/app-32-support-tickets`

---

## Application Information
- **App ID:** app-32
- **Name:** Customer Support Ticket System
- **Language:** Typescript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | src/index.ts | CWE-639 |
| V2 | A03 | Injection | High | src/index.ts | CWE-89 |
| V3 | A05 | Security Misconfiguration | Medium | src/index.ts | CWE-209 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** Medium
- **Location:** `src/index.ts`:180-201 (method: `GET /api/tickets/:id`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
The ticket detail retrieval endpoint fails to verify if the requesting user owns the ticket or possesses admin permissions, allowing authenticated users to access arbitrary tickets.

### VULN-02: A03 — Injection

- **Severity:** High
- **Location:** `src/index.ts`:165-177 (method: `GET /api/tickets/search`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
The search query parameter is directly concatenated into a raw SQL query statement, leading to SQL injection.

### VULN-03: A05 — Security Misconfiguration

- **Severity:** Medium
- **Location:** `src/index.ts`:204-224 (method: `GET /api/system/health`)
- **CWE:** [CWE-209](https://cwe.mitre.org/data/definitions/209.html)

#### Description
An endpoint exposes diagnostic info and verbose environment variables (including administrative recovery token and cookie secret) when requesting the system health status with diagnostic mode.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Verbose Diagnostics Exposure → Administrative Ticket Export Bypass

- **Combined Impact:** `db_exfiltration`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
An attacker queries the health diagnostics endpoint `/api/system/health?diagnostics=true` to leak the system configuration containing the hardcoded recovery key `SUPPORT-ADMIN-DEV-RECOVERY-KEY-2026`. The attacker then invokes the endpoint `/api/admin/export` passing this key in the `x-admin-token` header, enabling them to bulk export all tickets and users from the database.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | System diagnostics endpoint leaks secret admin recovery token. | Medium | A05 | CWE-209 | src/index.ts | `GET /api/system/health` |
| 2 | Admin export endpoint allows data exfiltration by verifying only the leaked recovery key. | Medium | A01 | CWE-306 | src/index.ts | `POST /api/admin/export` |

### CHAIN-02: Subtle Auth Session Pivot To Idor

- **Combined Impact:** `db_exfiltration`
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
| 1 | An endpoint exposes diagnostic info and verbose environment variables (including administrative recovery token and cookie secret) when requesting the system health status with diagnostic mode. | Medium | A05 | CWE-209 | src/index.ts | `GET /api/system/health` |
| 2 | The search query parameter is directly concatenated into a raw SQL query statement, leading to SQL injection. | High | A03 | CWE-89 | src/index.ts | `GET /api/tickets/search` |
| 3 | The ticket detail retrieval endpoint fails to verify if the requesting user owns the ticket or possesses admin permissions, allowing authenticated users to access arbitrary tickets. | Medium | A01 | CWE-639 | src/index.ts | `GET /api/tickets/:id` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.ts | Proper Bcrypt hashing for password storage and credentials validation during user login. |
| src/index.ts | Proper parameterized query logic in POST /api/tickets to insert new tickets safely. |
| src/index.ts | Proper authentication and authorization check in GET /api/users/profile to ensure users only access their own profile details. |
