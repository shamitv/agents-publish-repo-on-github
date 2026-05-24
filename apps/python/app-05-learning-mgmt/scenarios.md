# Chained Vulnerability Scenarios — Learning Mgmt

## Chain: "Config Leak → Session Forgery → Pickle RCE → Data Exfiltration"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Debug config endpoint exposes Flask secret_key | Low | A05 | `app.py` → `debug_config()` |
| 2 | Course import deserializes untrusted pickle payload | Medium | A08 | `app.py` → `import_course()` |


**Attack narrative**: The attacker sends `GET /api/debug/config` without authentication and reads the Flask `secret_key` from the JSON response. Using this key, they craft a signed session cookie with `role=ADMIN` and `user_id=4`. With the forged admin session, they send `POST /api/courses/import` with a base64-encoded malicious pickle payload that executes `os.system()` to dump the SQLite database contents to an attacker-controlled endpoint.

**Combined Impact**: Full database exfiltration including all user credentials, student grades, and course data.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
