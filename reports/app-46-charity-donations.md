# Security Report: app-46 — Charity Donation Platform

**Language:** Python (Flask)
**Directory:** `apps/python/app-46-charity-donations`

---

## Application Information
- **App ID:** app-46
- **Name:** Charity Donation Platform
- **Language:** Python
- **Framework:** Flask

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A02 | Cryptographic Failures | High | app.py | CWE-798 |
| V2 | A03 | Injection | High | app.py | CWE-89 |
| V3 | A09 | Security Logging & Monitoring Failures | Medium | app.py | CWE-778 |

---

## Standalone Vulnerabilities

### VULN-01: A02 — Cryptographic Failures

- **Severity:** High
- **Location:** `app.py`:9-11 (method: `STRIPE_KEY`)
- **CWE:** [CWE-798](https://cwe.mitre.org/data/definitions/798.html)

#### Description
Stripe payment gateway API key is hardcoded directly in the application source code.

### VULN-02: A03 — Injection

- **Severity:** High
- **Location:** `app.py`:128-150 (method: `search_donations`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
User search query is concatenated directly into a raw SQL query inside search_donations(), causing SQL injection.

### VULN-03: A09 — Security Logging & Monitoring Failures

- **Severity:** Medium
- **Location:** `app.py`:152-187 (method: `process_refund`)
- **CWE:** [CWE-778](https://cwe.mitre.org/data/definitions/778.html)

#### Description
High-value financial refund operations are performed silently without producing any audit log records.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: API Key Exposure → SQLi Donor Dump → Silent Refund Fraud

- **Combined Impact:** `db_exfiltration`
- **Difficulty:** Expert
- **Subtlety Tags:** `cross_file` `state_confusion` `parser_or_config_reasoning` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker can influence a multi-step workflow
- attacker can observe or reuse application state across requests

#### Attack Narrative
An attacker reads the hardcoded Stripe key from the source code. They then use the SQL injection vulnerability on the search donation endpoint to extract transaction IDs and donor information. Lastly, using the leaked Stripe credentials and transaction details, they trigger a refund to themselves silently due to missing audit logs.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Stripe API key hardcoded in source. | Medium | A02 | CWE-798 | app.py | `STRIPE_KEY` |
| 2 | SQL injection in search donation query reveals private database records. | Medium | A03 | CWE-89 | app.py | `search_donations` |
| 3 | Refunding donation generates no audit logs. | Low | A09 | CWE-778 | app.py | `process_refund` |

### CHAIN-02: Subtle State Confusion Pivot To Injection

- **Combined Impact:** `db_exfiltration`
- **Difficulty:** Expert
- **Subtlety Tags:** `cross_file` `state_confusion` `parser_or_config_reasoning` `implicit_trust` `realistic_decoy` `secondary_chain`

#### Prerequisites
- attacker can influence a multi-step workflow
- attacker can observe or reuse application state across requests

#### Attack Narrative
Attacker combines a low-visibility entry point with stored or derived application state, then pivots to a higher-impact sink that is reachable only after following the cross-file flow.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | High-value financial refund operations are performed silently without producing any audit log records. | Medium | A09 | CWE-778 | app.py | `process_refund` |
| 2 | User search query is concatenated directly into a raw SQL query inside search_donations(), causing SQL injection. | High | A03 | CWE-89 | app.py | `search_donations` |
| 3 | Stripe payment gateway API key is hardcoded directly in the application source code. | High | A02 | CWE-798 | app.py | `STRIPE_KEY` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| app.py | CSRF validation check on /api/donations ensuring requests include a valid X-CSRF-Token matching the user's session. |
| app.py | Proper parameterized SQL queries for retrieving campaigns by title/description. |
