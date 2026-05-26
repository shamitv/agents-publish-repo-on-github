# Security Report: app-05 — Online Learning Management System

**Language:** Python (Flask)
**Directory:** `apps/python/app-05-learning-mgmt`

---

## Application Information
- **App ID:** app-05
- **Name:** Online Learning Management System
- **Language:** Python
- **Framework:** Flask

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | High | app.py | CWE-639 |
| V2 | A05 | Security Misconfiguration | Medium | app.py | CWE-215 |
| V3 | A08 | Software and Data Integrity Failures | Critical | app.py | CWE-502 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** High
- **Location:** `app.py`:197-224 (method: `get_submission`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Quiz submission retrieval endpoint returns any submission by ID without verifying the requesting user is the submission owner, allowing any authenticated student to view other students' answers and scores.

### VULN-02: A05 — Security Misconfiguration

- **Severity:** Medium
- **Location:** `app.py`:249-263 (method: `debug_config`)
- **CWE:** [CWE-215](https://cwe.mitre.org/data/definitions/215.html)

#### Description
Unauthenticated debug endpoint at /api/debug/config exposes the Flask secret_key, database path, full environment variables, and server working directory to any caller.

### VULN-03: A08 — Software and Data Integrity Failures

- **Severity:** Critical
- **Location:** `app.py`:267-299 (method: `import_course`)
- **CWE:** [CWE-502](https://cwe.mitre.org/data/definitions/502.html)

#### Description
Course import endpoint deserializes untrusted base64-encoded pickle data from user input using pickle.loads(), allowing arbitrary remote code execution.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Config Leak → Session Forgery → Pickle RCE → Data Exfiltration

- **Combined Impact:** `db_exfiltration`
- **Difficulty:** Medium
- **Subtlety Tags:** `cross_file` `direct_data_flow` `realistic_decoy`

#### Prerequisites
- attacker can reach the public request path
- attacker can control one request parameter or body field

#### Attack Narrative
Attacker calls the unauthenticated /api/debug/config endpoint to read the Flask secret_key. Using this key, they forge a session cookie with admin/instructor role. With the forged admin session, they upload a malicious pickle payload via /api/courses/import to execute arbitrary code on the server and dump the entire database.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | GET /api/debug/config returns the Flask secret_key and full server environment without authentication, enabling session cookie forgery. | Low | A05 | CWE-215 | app.py | `debug_config` |
| 2 | POST /api/courses/import deserializes user-supplied pickle data with pickle.loads(), allowing arbitrary code execution once an admin session is forged. | Medium | A08 | CWE-502 | app.py | `import_course` |

### CHAIN-02: Subtle Deserialization Pivot To Idor

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
| 1 | Course import endpoint deserializes untrusted base64-encoded pickle data from user input using pickle.loads(), allowing arbitrary remote code execution. | Critical | A08 | CWE-502 | app.py | `import_course` |
| 2 | Unauthenticated debug endpoint at /api/debug/config exposes the Flask secret_key, database path, full environment variables, and server working directory to any caller. | Medium | A05 | CWE-215 | app.py | `debug_config` |
| 3 | Quiz submission retrieval endpoint returns any submission by ID without verifying the requesting user is the submission owner, allowing any authenticated student to view other students' answers and scores. | High | A01 | CWE-639 | app.py | `get_submission` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| app.py | Safe parameterized SQL query for user login authentication — secure SQL decoy |
| app.py | Proper INSTRUCTOR/ADMIN role check on course creation endpoint — secure access control decoy |
| app.py | Enrollment listing correctly scoped to current user's session — secure data-scoping decoy |
