# Chained Vulnerability Scenarios — Online Learning Management System

## Chain: "Config Leak -> Session Forgery -> Quiz Submission Exfiltration"

An attacker combines a debug configuration leak, forgeable session trust, and an IDOR to read quiz submissions belonging to other students.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Debug endpoint exposes the Flask signing secret and environment without authentication | Low | A05 | `src/services/debug_service.py` -> `collect()` |
| 2 | Session role values are trusted after cookie verification | Medium | A02 | `src/services/auth_service.py` -> `current_user()` |
| 3 | Submission lookup returns records by ID without ownership checks | Medium | A01 | `src/services/submission_service.py` -> `get_submission()` |

**Attack narrative**: The attacker sends `GET /api/debug/config`, reads the Flask signing secret, forges an instructor/admin session cookie, and then requests `/api/submissions/{id}` values belonging to other students.

**Combined Impact**: Bulk exfiltration of student quiz submissions and grades.

---

_This file is supplemental internal narrative. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
