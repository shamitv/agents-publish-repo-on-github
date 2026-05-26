# Security Report: app-01 — E-Commerce Product Catalog API

**Language:** Python (Flask)
**Directory:** `apps/python/app-01-ecommerce-catalog`

---

## Application Information
- **App ID:** app-01
- **Name:** E-Commerce Product Catalog API
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
- **Location:** `app.py`:150-165 (method: `get_order_details`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Order retrieval endpoint returns order data solely based on the order_id path variable, performing no owner validation checks between the authenticated user and the requested order's client

### VULN-02: A03 — Injection

- **Severity:** High
- **Location:** `app.py`:110-125 (method: `list_products`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
Product search query parameter is concatenated directly into a raw SQLite SELECT statement without parameterization, permitting SQL injection bypasses

### VULN-03: A09 — Security Logging & Monitoring Failures

- **Severity:** Medium
- **Location:** `app.py`:180-200 (method: `create_order`)
- **CWE:** [CWE-778](https://cwe.mitre.org/data/definitions/778.html)

#### Description
High-value and sensitive financial activities, including order checkouts, payment state mappings, and catalog stock alterations, are executed without producing any structured audit logs or trace monitoring records


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: User Enumeration → Session Forge → Admin Takeover

- **Combined Impact:** `account_takeover`
- **Difficulty:** Medium
- **Subtlety Tags:** `cross_file` `direct_data_flow` `realistic_decoy`

#### Prerequisites
- attacker can reach the public request path
- attacker can control one request parameter or body field

#### Attack Narrative
Attacker confirms admin username via unauthenticated existence endpoint, then forges a Flask session cookie using the hardcoded secret_key visible in source code, gaining admin-level access without any credentials.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | GET /api/users/exists returns 200/404 per username, confirming valid accounts without authentication | Low | A01 | CWE-204 | app.py | `user_exists` |
| 2 | Flask secret_key is a hardcoded string in source code, allowing any party with source access to forge valid signed session cookies for any user or role | Medium | A05 | CWE-798 | app.py | `app_config` |
| 3 | No CSRF tokens on any state-changing endpoint — the forged session cookie is sufficient to invoke admin-only mutations | Low | A05 | CWE-352 | app.py | `all_post_endpoints` |

### CHAIN-02: Subtle State Confusion Pivot To Idor

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
| 1 | High-value and sensitive financial activities, including order checkouts, payment state mappings, and catalog stock alterations, are executed without producing any structured audit logs or trace monitoring records | Medium | A09 | CWE-778 | app.py | `create_order` |
| 2 | Product search query parameter is concatenated directly into a raw SQLite SELECT statement without parameterization, permitting SQL injection bypasses | High | A03 | CWE-89 | app.py | `list_products` |
| 3 | Order retrieval endpoint returns order data solely based on the order_id path variable, performing no owner validation checks between the authenticated user and the requested order's client | High | A01 | CWE-639 | app.py | `get_order_details` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| app.py | Safe, parameterized user retrieval query during auth logins — secure SQL decoy |
| app.py | Flask session cookies are cryptographically signed with high-entropy key — secure cookie decoy |
