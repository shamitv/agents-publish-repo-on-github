# Security Report: app-21 — Insurance Claims Processor

**Language:** Python (Flask)
**Directory:** `apps/python/app-21-insurance-claims`

---

## Application Information
- **App ID:** app-21
- **Name:** Insurance Claims Processor
- **Language:** Python
- **Framework:** Flask

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | High | app.py | CWE-639 |
| V2 | A03 | Injection | High | app.py | CWE-89 |
| V3 | A09 | Security Logging & Monitoring Failures | Medium | app.py | CWE-778 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** High
- **Location:** `app.py`:215-240 (method: `get_claim`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Claim detail endpoint returns any claim by ID without verifying the requesting user is the claimant, exposing other customers' PII, payout amounts, and policy details.

### VULN-02: A03 — Injection

- **Severity:** High
- **Location:** `app.py`:173-212 (method: `search_claims`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
Claim search endpoint concatenates user input directly into a raw SQL WHERE clause without parameterization, permitting SQL injection to extract arbitrary data from the database.

### VULN-03: A09 — Security Logging & Monitoring Failures

- **Severity:** Medium
- **Location:** `app.py`:268-296 (method: `approve_claim`)
- **CWE:** [CWE-778](https://cwe.mitre.org/data/definitions/778.html)

#### Description
High-value claim approvals and automatic payout dispatches produce no audit logs, making it impossible to detect fraudulent approvals or trace who authorized payouts.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: SQL Injection → IDOR Claim Access → Silent Payout Fraud

- **Combined Impact:** `data_modification`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
Attacker uses SQL injection in the claim search endpoint to discover internal claim IDs and amounts. They then exploit the IDOR vulnerability on the claim detail endpoint to view and understand claim data. Finally, they leverage the lack of audit logging on the approval endpoint to approve fraudulent claims and trigger payouts without any trace.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | SQL injection in claim search reveals internal claim IDs, amounts, and status values that are not normally visible to the attacker's role. | Medium | A03 | CWE-89 | app.py | `search_claims` |
| 2 | IDOR on claim detail endpoint allows viewing any claim's full details including claimant PII, policy information, and payout history. | Medium | A01 | CWE-639 | app.py | `get_claim` |
| 3 | Claim approval endpoint writes no audit logs, enabling an attacker with adjuster access to approve fraudulent claims and trigger payouts silently. | Low | A09 | CWE-778 | app.py | `approve_claim` |

### CHAIN-02: Subtle Auth Session Pivot To Idor

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
| 1 | High-value claim approvals and automatic payout dispatches produce no audit logs, making it impossible to detect fraudulent approvals or trace who authorized payouts. | Medium | A09 | CWE-778 | app.py | `approve_claim` |
| 2 | Claim search endpoint concatenates user input directly into a raw SQL WHERE clause without parameterization, permitting SQL injection to extract arbitrary data from the database. | High | A03 | CWE-89 | app.py | `search_claims` |
| 3 | Claim detail endpoint returns any claim by ID without verifying the requesting user is the claimant, exposing other customers' PII, payout amounts, and policy details. | High | A01 | CWE-639 | app.py | `get_claim` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| app.py | Safe parameterized SQL query for user login — secure SQL decoy |
| app.py | Proper authorization check on /api/admin/stats requiring ADMIN role — secure access control decoy |
| app.py | Policy listing correctly scoped to current user for CUSTOMER role — secure data-scoping decoy |
