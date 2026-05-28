# Security Report: app-22 — Food Delivery Order System

**Language:** Python (Fastapi)
**Directory:** `apps/python/app-22-food-delivery`

---

## Application Information
- **App ID:** app-22
- **Name:** Food Delivery Order System
- **Language:** Python
- **Framework:** Fastapi

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A02 | Cryptographic Failures | Medium | app.py | CWE-798 |
| V2 | A04 | Insecure Design | Medium | app.py | CWE-307 |
| V3 | A07 | Identification and Authentication Failures | Medium | app.py | CWE-1004 |

---

## Standalone Vulnerabilities

### VULN-01: A02 — Cryptographic Failures

- **Severity:** Medium
- **Location:** `app.py`:9-11 (method: `PAYMENT_SECRET`)
- **CWE:** [CWE-798](https://cwe.mitre.org/data/definitions/798.html)

#### Description
Payment processing API key is hardcoded as a module-level constant in the source code.

### VULN-02: A04 — Insecure Design

- **Severity:** Medium
- **Location:** `app.py`:136-160 (method: `place_order`)
- **CWE:** [CWE-307](https://cwe.mitre.org/data/definitions/307.html)

#### Description
No rate limiting or idempotency checks on order placement, allowing clients to send infinite duplicate order requests, leading to resource exhaustion or denial of service.

### VULN-03: A07 — Identification and Authentication Failures

- **Severity:** Medium
- **Location:** `app.py`:122-127 (method: `login`)
- **CWE:** [CWE-1004](https://cwe.mitre.org/data/definitions/1004.html)

#### Description
Session cookie is set without the HttpOnly or Secure flags, making it vulnerable to extraction via Cross-Site Scripting (XSS).


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Hardcoded Secret Key → Webhook Forgery → Free Orders

- **Combined Impact:** `data_modification`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
An attacker extracts the hardcoded PAYMENT_SECRET from the source code. They then call the payment webhook endpoint directly, providing this secret as the auth token, to mark their pending orders as paid without completing actual payment.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Payment secret is hardcoded in the source code. | Medium | A02 | CWE-798 | app.py | `PAYMENT_SECRET` |
| 2 | Payment webhook verifies authority by checking the hardcoded PAYMENT_SECRET without checking signature or request origin. | Medium | A04 | CWE-347 | app.py | `payment_webhook` |

### CHAIN-02: Subtle Auth Session Pivot To Injection

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
| 1 | Session cookie is set without the HttpOnly or Secure flags, making it vulnerable to extraction via Cross-Site Scripting (XSS). | Medium | A07 | CWE-1004 | app.py | `login` |
| 2 | No rate limiting or idempotency checks on order placement, allowing clients to send infinite duplicate order requests, leading to resource exhaustion or denial of service. | Medium | A04 | CWE-307 | app.py | `place_order` |
| 3 | Payment processing API key is hardcoded as a module-level constant in the source code. | Medium | A02 | CWE-798 | app.py | `PAYMENT_SECRET` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| app.py | Proper Bcrypt hashing for password storage during registration and verification during login. |
| app.py | Proper parameterized SQL query for listing menu items by category. |
