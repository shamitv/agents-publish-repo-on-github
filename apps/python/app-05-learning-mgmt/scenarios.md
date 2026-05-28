# Chained Vulnerability Scenarios — Online Learning Management System

## Chain 1: "Config Leak -> Session Forgery -> Quiz Submission Exfiltration"

An attacker combines a debug configuration leak, forgeable session trust, and an IDOR to read quiz submissions belonging to other students.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Debug endpoint exposes the Flask signing secret and environment without authentication | Low | A05 | `src/services/debug_service.py` -> `collect()` |
| 2 | Session role values are trusted after cookie verification | Medium | A02 | `src/services/auth_service.py` -> `current_user()` |
| 3 | Submission lookup returns records by ID without ownership checks | Medium | A01 | `src/services/submission_service.py` -> `get_submission()` |

**Attack narrative**: The attacker sends `GET /api/debug/config`, reads the Flask signing secret, forges an instructor/admin session cookie, and then requests `/api/submissions/{id}` values belonging to other students.

**Combined Impact**: Bulk exfiltration of student quiz submissions and grades.

---

## Chain 2: "Enrollment Role Escalation -> Missing Audit -> Undetected Grade Tampering"

An attacker exploits weak enrollment validation (A04) to escalate their role to INSTRUCTOR, then overrides student grades. The grading pipeline writes no audit log (A09), leaving the tampering undetectable.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Enrollment trusts client-supplied role, enabling privilege escalation to instructor access | Low | A04 | `src/controllers/enrollment_controller.py` -> `enroll()` |
| 2 | Grade override writes scores without course-ownership check and without audit log entries | Low | A09 | `src/workers/grading_listener.py` -> `process_submission()` |

**Attack narrative**: The attacker enrolls with `{"course_id": 99, "role": "INSTRUCTOR"}`. The A04 vulnerability accepts the client-supplied elevated role. Now authenticated with instructor privileges, the attacker calls `POST /api/instructor/grades/override` targeting any student's submission. The override endpoint writes the change to the `grades` table without an `audit_log` entry. No trace remains of who changed the grade, when, or from what prior value.

**Combined Impact**: Undetected modification of student grades (`data_modification`).

---

## Chain 3: "Debug Config Leak -> SSRF Internal Pivot"

An attacker combines the debug configuration leak (A05) with an SSRF vulnerability in the course import feature (A10) to pivot to an internal-only metrics endpoint.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Debug endpoint leaks internal service hostnames and internal endpoint paths, enabling SSRF targeting | Low | A05 | `src/services/debug_service.py` -> `collect()` |
| 2 | SSRF in fetch_content() enables internal network pivot to /admin/internal/metrics using leaked debug topology | Medium | A10 | `src/services/import_service.py` -> `fetch_content()` |

**Attack narrative**: The attacker calls `GET /api/debug/config`, obtaining internal Docker service hostnames and the `/admin/internal/metrics` path from leaked environment variables. The attacker then sends `POST /api/courses/import` with `{"url": "http://localhost:8085/admin/internal/metrics"}`. The `fetch_content()` method fetches the URL without hostname validation, reaching the internal metrics endpoint that has no Docker port mapping and is normally unreachable from outside the container.

**Combined Impact**: Lateral movement — attacker exfiltrates internal-only operational data (`lateral_movement`).

---

_This file is supplemental internal narrative. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
