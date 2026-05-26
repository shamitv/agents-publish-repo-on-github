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
| V1 | A01 | Broken Access Control | High | src/services/submission_service.py | CWE-639 |
| V2 | A05 | Security Misconfiguration | Medium | src/services/debug_service.py | CWE-200 |
| V3 | A08 | Software and Data Integrity Failures | Critical | src/workers/import_listener.py | CWE-502 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** High
- **Location:** `src/services/submission_service.py`:N/A (method: `get_submission`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Quiz submission retrieval returns any submission by ID without verifying that the requesting user owns the submission.

### VULN-02: A05 — Security Misconfiguration

- **Severity:** Medium
- **Location:** `src/services/debug_service.py`:N/A (method: `collect`)
- **CWE:** [CWE-200](https://cwe.mitre.org/data/definitions/200.html)

#### Description
Unauthenticated debug endpoint exposes the Flask secret key, environment variables, and runtime details.

### VULN-03: A08 — Software and Data Integrity Failures

- **Severity:** Critical
- **Location:** `src/workers/import_listener.py`:N/A (method: `load_course`)
- **CWE:** [CWE-502](https://cwe.mitre.org/data/definitions/502.html)

#### Description
Course import worker deserializes untrusted pickle bytes without class restrictions.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Config Leak -> Session Forgery -> Quiz Submission Exfiltration

- **Combined Impact:** `db_exfiltration`
- **Difficulty:** Medium
- **Subtlety Tags:** 

#### Prerequisites
- None specified

#### Attack Narrative
An attacker reads the unauthenticated debug configuration response to recover the Flask signing secret, forges an instructor or admin session accepted by the session trust helper, and then uses the quiz submission IDOR to read other students' submissions.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Debug endpoint exposes secrets and environment values without authentication. | Low | A05 | CWE-200 | src/services/debug_service.py | `collect` |
| 2 | Session trust logic accepts forged role values once the signing secret is known. | Medium | A02 | CWE-347 | src/services/auth_service.py | `current_user` |
| 3 | Submission lookup returns records by ID without student ownership checks. | Medium | A01 | CWE-639 | src/services/submission_service.py | `get_submission` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/repositories/user_repository.py | Login uses parameterized SQL despite nearby intentionally vulnerable flows. |
| src/controllers/course_controller.py | Course creation requires INSTRUCTOR or ADMIN role before writing records. |
| src/repositories/enrollment_repository.py | Enrollment listing scopes rows to the current session's user ID. |
