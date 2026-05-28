# Security Report: app-03 — Banking Transaction Service

**Language:** Python (Fastapi)
**Directory:** `apps/python/app-03-banking-service`

---

## Application Information
- **App ID:** app-03
- **Name:** Banking Transaction Service
- **Language:** Python
- **Framework:** Fastapi

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A02 | Cryptographic Failures | High | app.py | CWE-798 |
| V2 | A03 | Injection | High | app.py | CWE-943 |
| V3 | A04 | Insecure Design | Medium | app.py | CWE-307 |

---

## Standalone Vulnerabilities

### VULN-01: A02 — Cryptographic Failures

- **Severity:** High
- **Location:** `app.py`:20-35 (method: `API_KEYS_CONFIG`)
- **CWE:** [CWE-798](https://cwe.mitre.org/data/definitions/798.html)

#### Description
Sensitive payment gateway API keys (GATEWAY_API_KEY) are hardcoded directly into the backend source code file rather than being loaded securely from external, encrypted environment variables

### VULN-02: A03 — Injection

- **Severity:** High
- **Location:** `app.py`:115-135 (method: `list_transactions`)
- **CWE:** [CWE-943](https://cwe.mitre.org/data/definitions/943.html)

#### Description
Transaction filter endpoint parses raw, unvalidated JSON input from the user and supplies it directly to the PyMongo/mongomock find() engine, allowing arbitrary NoSQL operator injection ($ne, $gt) to leak private wire accounts

### VULN-03: A04 — Insecure Design

- **Severity:** Medium
- **Location:** `app.py`:150-180 (method: `dispatch_transfer`)
- **CWE:** [CWE-307](https://cwe.mitre.org/data/definitions/307.html)

#### Description
wire transfer dispatch endpoint contains no rate-limiting, request throttling, or checkout limits, allowing malicious bots or automated scripts to trigger infinite consecutive transfers and drain accounts


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Unauthenticated Account Harvest → Cookie Interception → Unlimited Fund Drain

- **Combined Impact:** `data_modification`
- **Difficulty:** Medium
- **Subtlety Tags:** `cross_file` `direct_data_flow` `realistic_decoy`

#### Prerequisites
- attacker can reach the public request path
- attacker can control one request parameter or body field

#### Attack Narrative
Attacker calls the unauthenticated /api/admin/users endpoint to harvest account numbers, intercepts a victim session cookie that travels without the Secure flag over plain HTTP, then uses that cookie to drain the victim's balance via the rate-limit-free transfer endpoint.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | GET /api/admin/users endpoint is publicly accessible without authentication, returning all users' account and routing numbers | Medium | A01 | CWE-284 | app.py | `admin_list_users` |
| 2 | Session cookie is set with httponly=True but without secure=True, allowing it to be transmitted over plain HTTP and intercepted by a network attacker | Low | A05 | CWE-614 | app.py | `login` |
| 3 | Transfer endpoint applies no rate limiting, per-request amount cap, or daily transaction ceiling, allowing a stolen session to drain the full balance instantly | High | A04 | CWE-799 | app.py | `dispatch_transfer` |

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
| 1 | wire transfer dispatch endpoint contains no rate-limiting, request throttling, or checkout limits, allowing malicious bots or automated scripts to trigger infinite consecutive transfers and drain accounts | Medium | A04 | CWE-307 | app.py | `dispatch_transfer` |
| 2 | Transaction filter endpoint parses raw, unvalidated JSON input from the user and supplies it directly to the PyMongo/mongomock find() engine, allowing arbitrary NoSQL operator injection ($ne, $gt) to leak private wire accounts | High | A03 | CWE-943 | app.py | `list_transactions` |
| 3 | Sensitive payment gateway API keys (GATEWAY_API_KEY) are hardcoded directly into the backend source code file rather than being loaded securely from external, encrypted environment variables | High | A02 | CWE-798 | app.py | `API_KEYS_CONFIG` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| app.py | Safe, cryptographically signed HTTP cookies for session auth handshakes — secure auth decoy |
| app.py | Safe, parameterized username lookup on login — secure query decoy |
