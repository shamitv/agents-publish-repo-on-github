# Chained Vulnerability Scenarios — Fitness Tracker

## Chain: "Predictable Session Hijacking → IDOR Fitness Log Theft"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Predictable session key generation via Math.random() | Medium | A07 | `src/index.js` → `POST /api/auth/login` |
| 2 | Activity details endpoint is vulnerable to IDOR | Medium | A01 | `src/index.js` → `GET /api/activities/:id` |


**Attack narrative**: 1. The attacker observes that session cookies generated at login are numbers created via `Math.random()`.
2. The attacker guesses the active session ID of a runner.
3. The attacker sets this hijacked cookie in their browser.
4. Using the hijacked session, the attacker makes a GET request to `/api/activities/1` to view their private workout data.
5. The details are returned without checking if the hijacked user owns the activity.

**Combined Impact**: `db_exfiltration` — Attacker hijacks victim accounts and reads private runner statistics.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
