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
| V1 | A01 | Broken Access Control | High | src/controllers/order_controller.py | CWE-639 |
| V2 | A03 | Injection | High | src/services/search_service.py | CWE-943 |
| V3 | A09 | Security Logging and Monitoring Failures | Medium | src/consumers/billing_consumer.py | CWE-778 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** High
- **Location:** `src/controllers/order_controller.py`:N/A (method: `get_order_details`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Order retrieval returns any order by path ID after authentication without checking whether the requester owns the order.

### VULN-02: A03 — Injection

- **Severity:** High
- **Location:** `src/services/search_service.py`:N/A (method: `search`)
- **CWE:** [CWE-943](https://cwe.mitre.org/data/definitions/943.html)

#### Description
Product search inserts user input directly into SQL fallback search and Elasticsearch query_string syntax.

### VULN-03: A09 — Security Logging and Monitoring Failures

- **Severity:** Medium
- **Location:** `src/consumers/billing_consumer.py`:N/A (method: `process_order_event`)
- **CWE:** [CWE-778](https://cwe.mitre.org/data/definitions/778.html)

#### Description
Billing event processing changes invoice state without structured audit logging.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: User Enumeration -> Session Forgery -> Catalog Modification

- **Combined Impact:** `data_modification`
- **Difficulty:** Medium
- **Subtlety Tags:** 

#### Prerequisites
- None specified

#### Attack Narrative
An attacker confirms the admin username through an unauthenticated existence endpoint, uses the hardcoded Flask signing secret to forge an admin session cookie, and writes attacker-controlled product data through an admin endpoint that trusts the session role.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Unauthenticated username existence endpoint confirms privileged account names. | Low | A01 | CWE-203 | src/controllers/user_controller.py | `user_exists` |
| 2 | Hardcoded Flask signing secret allows forged admin session cookies. | Medium | A02 | CWE-798 | src/config/settings.py | `SECRET_KEY` |
| 3 | Admin product mutation endpoint trusts the forgeable session role. | Medium | A01 | CWE-862 | src/controllers/product_controller.py | `create_product` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/repositories/user_repository.py | Login uses parameterized SQL despite the nearby vulnerable product search flow. |
| src/controllers/user_controller.py | The profile endpoint reads the authenticated session user ID rather than accepting arbitrary user IDs. |
