# Security Report: app-23 — Government Permit Application Portal

**Language:** Python (Django)
**Directory:** `apps/python/app-23-govt-permits`

---

## Application Information
- **App ID:** app-23
- **Name:** Government Permit Application Portal
- **Language:** Python
- **Framework:** Django

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | permits/views.py | CWE-639 |
| V2 | A05 | Security Misconfiguration | Medium | govt_permits/settings.py | CWE-16 |
| V3 | A08 | Software and Data Integrity Failures | High | permits/views.py | CWE-434 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** Medium
- **Location:** `permits/views.py`:56-82 (method: `permit_detail`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Permit detail endpoint fails to verify if the requesting user is the applicant or has reviewer privileges, allowing any authenticated user to view other citizens' permit applications.

### VULN-02: A05 — Security Misconfiguration

- **Severity:** Medium
- **Location:** `govt_permits/settings.py`:6-10 (method: `settings`)
- **CWE:** [CWE-16](https://cwe.mitre.org/data/definitions/16.html)

#### Description
The application runs with DEBUG=True, wildcard ALLOWED_HOSTS, and a hardcoded SECRET_KEY, disclosing system details on error pages and exposing session signatures.

### VULN-03: A08 — Software and Data Integrity Failures

- **Severity:** High
- **Location:** `permits/views.py`:84-115 (method: `upload_document`)
- **CWE:** [CWE-434](https://cwe.mitre.org/data/definitions/434.html)

#### Description
The permit document upload endpoint does not validate file extensions or MIME types, permitting users to upload arbitrary scripts (e.g. Python scripts) that can then be executed by direct request because of the static files handler running in DEBUG mode.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Debug Page Info Leak → Unrestricted Upload → RCE

- **Combined Impact:** `lateral_movement`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
The attacker triggers an error page on the application. Because DEBUG=True is active, the error page leaks internal paths, system configurations, and settings. Using this information, the attacker uploads a malicious script through the permit document upload feature. Knowing the internal media paths leaked via the debug page, the attacker invokes the script directly to execute arbitrary code.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | DEBUG=True is enabled, exposing settings and path structures via error pages. | Low | A05 | CWE-16 | govt_permits/settings.py | `settings` |
| 2 | Unrestricted file upload accepts arbitrary executable scripts and saves them in a predictable web-accessible directory. | Medium | A08 | CWE-434 | permits/views.py | `upload_document` |

### CHAIN-02: Subtle Path Traversal Pivot To Idor

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
| 1 | The permit document upload endpoint does not validate file extensions or MIME types, permitting users to upload arbitrary scripts (e.g. Python scripts) that can then be executed by direct request because of the static files handler running in DEBUG mode. | High | A08 | CWE-434 | permits/views.py | `upload_document` |
| 2 | The application runs with DEBUG=True, wildcard ALLOWED_HOSTS, and a hardcoded SECRET_KEY, disclosing system details on error pages and exposing session signatures. | Medium | A05 | CWE-16 | govt_permits/settings.py | `settings` |
| 3 | Permit detail endpoint fails to verify if the requesting user is the applicant or has reviewer privileges, allowing any authenticated user to view other citizens' permit applications. | Medium | A01 | CWE-639 | permits/views.py | `permit_detail` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| govt_permits/settings.py | CsrfViewMiddleware is included in the MIDDLEWARE configuration, ensuring CSRF tokens are validated for all state-changing requests. |
| permits/views.py | Proper permission check in /api/permits/approve enforcing that only staff users can approve or reject permits. |
| permits/views.py | Proper scoped database filter in /api/permits preventing regular citizens from listing other users' permit applications. |
