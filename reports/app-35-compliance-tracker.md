# Security Report: app-35 — Compliance Document Tracker

**Language:** Typescript (Express)
**Directory:** `apps/typescript/app-35-compliance-tracker`

---

## Application Information
- **App ID:** app-35
- **Name:** Compliance Document Tracker
- **Language:** Typescript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | src/index.ts | CWE-639 |
| V2 | A05 | Security Misconfiguration | Medium | src/index.ts | CWE-209 |
| V3 | A08 | Software and Data Integrity Failures | High | src/index.ts | CWE-502 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** Medium
- **Location:** `src/index.ts`:153-166 (method: `GET /api/documents/:id`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Retrieving document details by ID from the database fails to verify if the requesting user owns the document or possesses administrative permissions, allowing unauthorized access to arbitrary documents.

### VULN-02: A05 — Security Misconfiguration

- **Severity:** Medium
- **Location:** `src/index.ts`:216-230 (method: `GET /api/admin/debug`)
- **CWE:** [CWE-209](https://cwe.mitre.org/data/definitions/209.html)

#### Description
The debug endpoint leaks process environment details and a hardcoded administrative recovery API token when dev parameter is supplied.

### VULN-03: A08 — Software and Data Integrity Failures

- **Severity:** High
- **Location:** `src/index.ts`:169-193 (method: `POST /api/documents`)
- **CWE:** [CWE-502](https://cwe.mitre.org/data/definitions/502.html)

#### Description
Document metadata is deserialized using the insecure eval() function, allowing execution of arbitrary system code via malicious metadata input.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Dev Mode Config Leak → Admin Document Retrieval Bypass

- **Combined Impact:** `account_takeover`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
An attacker sends a request to the debug endpoint `/api/admin/debug?dev=true` to leak the developer administration token `ADMIN-DEV-TOKEN-KEY-8871`. Using this token in the `x-admin-token` header, the attacker authenticates as admin and accesses `/api/documents/1` to view sensitive customer compliance documents.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Development debug settings leak administration API key. | Medium | A05 | CWE-209 | src/index.ts | `GET /api/admin/debug` |
| 2 | Documents details retrieval allows the attacker authenticated with the leaked API key to fetch arbitrary documents. | Medium | A01 | CWE-639 | src/index.ts | `GET /api/documents/:id` |

### CHAIN-02: Subtle Deserialization Pivot To Idor

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
| 1 | Document metadata is deserialized using the insecure eval() function, allowing execution of arbitrary system code via malicious metadata input. | High | A08 | CWE-502 | src/index.ts | `POST /api/documents` |
| 2 | The debug endpoint leaks process environment details and a hardcoded administrative recovery API token when dev parameter is supplied. | Medium | A05 | CWE-209 | src/index.ts | `GET /api/admin/debug` |
| 3 | Retrieving document details by ID from the database fails to verify if the requesting user owns the document or possesses administrative permissions, allowing unauthorized access to arbitrary documents. | Medium | A01 | CWE-639 | src/index.ts | `GET /api/documents/:id` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.ts | Proper Bcrypt hashing for password storage and credentials verification during login. |
| src/index.ts | Proper authorization check in GET /api/users/me strictly validating caller profile limits. |
| src/index.ts | Safe JSON deserialization logic using JSON.parse in POST /api/documents/safe. |
