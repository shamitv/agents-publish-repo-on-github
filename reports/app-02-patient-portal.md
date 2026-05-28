# Security Report: app-02 — Healthcare Patient Portal

**Language:** Python (Django)
**Directory:** `apps/python/app-02-patient-portal`

---

## Application Information
- **App ID:** app-02
- **Name:** Healthcare Patient Portal
- **Language:** Python
- **Framework:** Django

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | High | portal/views.py | CWE-639 |
| V2 | A02 | Cryptographic Failures | High | portal/models.py | CWE-916 |
| V3 | A07 | Identification & Authentication Failures | Medium | portal/views.py | CWE-307 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** High
- **Location:** `portal/views.py`:110-125 (method: `get_patient_records`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Patient records detail view retrieves and returns sensitive medical histories based purely on the patient_id path parameter, with no validation verifying if the authenticated user's profile ID matches the requested parameter

### VULN-02: A02 — Cryptographic Failures

- **Severity:** High
- **Location:** `portal/models.py`:35-50 (method: `set_password_md5`)
- **CWE:** [CWE-916](https://cwe.mitre.org/data/definitions/916.html)

#### Description
User profiles database utilizes insecure, weak MD5 hashing algorithms to store patient credentials instead of standard PBKDF2/Argon2 algorithms, exposing credentials to simple dictionary attacks

### VULN-03: A07 — Identification & Authentication Failures

- **Severity:** Medium
- **Location:** `portal/views.py`:70-90 (method: `login_view`)
- **CWE:** [CWE-307](https://cwe.mitre.org/data/definitions/307.html)

#### Description
System access authentication handles arbitrary sequential log-in retries without implementing account lockouts, rate limiting, or connection throttling rules, facilitating dictionary and brute force attacks


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: User Enumeration → Offline MD5 Crack → Medical Records Exfiltration

- **Combined Impact:** `db_exfiltration`
- **Difficulty:** Medium
- **Subtlety Tags:** `cross_file` `direct_data_flow` `realistic_decoy`

#### Prerequisites
- attacker can reach the public request path
- attacker can control one request parameter or body field

#### Attack Narrative
Attacker enumerates valid patient usernames via distinct login error messages, cracks the unsalted MD5 password hash offline, authenticates, uses the patient search endpoint to collect all patient IDs, then dumps every patient's medical records via the IDOR endpoint.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Login endpoint returns distinct error messages for unknown username vs wrong password, enabling username enumeration | Low | A07 | CWE-204 | portal/views.py | `login_view` |
| 2 | Passwords stored as unsalted MD5 hashes, crackable offline via rainbow tables or GPU brute force | High | A02 | CWE-916 | portal/models.py | `set_password_md5` |
| 3 | Patient search endpoint returns IDs for all patients regardless of the authenticated user's own identity, enabling mass IDOR enumeration | Low | A01 | CWE-639 | portal/views.py | `search_patients` |

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
| 1 | System access authentication handles arbitrary sequential log-in retries without implementing account lockouts, rate limiting, or connection throttling rules, facilitating dictionary and brute force attacks | Medium | A07 | CWE-307 | portal/views.py | `login_view` |
| 2 | User profiles database utilizes insecure, weak MD5 hashing algorithms to store patient credentials instead of standard PBKDF2/Argon2 algorithms, exposing credentials to simple dictionary attacks | High | A02 | CWE-916 | portal/models.py | `set_password_md5` |
| 3 | Patient records detail view retrieves and returns sensitive medical histories based purely on the patient_id path parameter, with no validation verifying if the authenticated user's profile ID matches the requested parameter | High | A01 | CWE-639 | portal/views.py | `get_patient_records` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| patient_portal/settings.py | Django secure session cookie flags (SESSION_COOKIE_HTTPONLY=True, SECURE_BROWSER_XSS_FILTER=True) properly enabled — secure auth decoy |
| portal/views.py | Safe, CSRF exempt and parameterized input sanitization during appointment booking checks — secure input decoy |
