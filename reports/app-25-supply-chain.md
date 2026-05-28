# Security Report: app-25 — Supply Chain Inventory Tracker

**Language:** Python (Flask)
**Directory:** `apps/python/app-25-supply-chain`

---

## Application Information
- **App ID:** app-25
- **Name:** Supply Chain Inventory Tracker
- **Language:** Python
- **Framework:** Flask

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A06 | Vulnerable and Outdated Components | High | requirements.txt | CWE-502 |
| V2 | A07 | Identification and Authentication Failures | Medium | app.py | CWE-256 |
| V3 | A10 | Server-Side Request Forgery | Medium | app.py | CWE-918 |

---

## Standalone Vulnerabilities

### VULN-01: A06 — Vulnerable and Outdated Components

- **Severity:** High
- **Location:** `requirements.txt`:3-3 (method: `PyYAML`)
- **CWE:** [CWE-502](https://cwe.mitre.org/data/definitions/502.html)

#### Description
Pins vulnerable PyYAML==5.3.1 which permits arbitrary code execution (RCE) via yaml.load() when parsing untrusted serialization inputs.

### VULN-02: A07 — Identification and Authentication Failures

- **Severity:** Medium
- **Location:** `app.py`:87-92 (method: `login`)
- **CWE:** [CWE-256](https://cwe.mitre.org/data/definitions/256.html)

#### Description
Passwords are stored in plaintext in the database and queried directly without hashing, and the session cookie lacks the Secure flag.

### VULN-03: A10 — Server-Side Request Forgery

- **Severity:** Medium
- **Location:** `app.py`:119-141 (method: `check_supplier_api`)
- **CWE:** [CWE-918](https://cwe.mitre.org/data/definitions/918.html)

#### Description
Supplier API check endpoint allows fetching user-supplied URLs without restricting requests to external public IPs, causing SSRF.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: SSRF → YAML Deserialization → Lateral Movement

- **Combined Impact:** `lateral_movement`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
An attacker uses the SSRF vulnerability in the supplier health check endpoint to fetch an internal URL. By pointing the inventory import endpoint to an internal server or using the SSRF capability to retrieve a payload, they feed a malicious YAML document to yaml.load(), triggering unsafe deserialization and arbitrary code execution.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | SSRF endpoint fetches arbitrary URL. | Medium | A10 | CWE-918 | app.py | `check_supplier_api` |
| 2 | Deserializes fetched contents with unsafe yaml.load(), executing arbitrary system commands. | Medium | A06 | CWE-502 | app.py | `import_inventory` |

### CHAIN-02: Subtle Ssrf Pivot To Deserialization

- **Combined Impact:** `lateral_movement`
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
| 1 | Supplier API check endpoint allows fetching user-supplied URLs without restricting requests to external public IPs, causing SSRF. | Medium | A10 | CWE-918 | app.py | `check_supplier_api` |
| 2 | Passwords are stored in plaintext in the database and queried directly without hashing, and the session cookie lacks the Secure flag. | Medium | A07 | CWE-256 | app.py | `login` |
| 3 | Pins vulnerable PyYAML==5.3.1 which permits arbitrary code execution (RCE) via yaml.load() when parsing untrusted serialization inputs. | High | A06 | CWE-502 | requirements.txt | `PyYAML` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| app.py | Safe loading of YAML config using yaml.safe_load() on local administrator config data. |
| app.py | Proper parameterized SQL queries for retrieving warehouse records by warehouse ID. |
