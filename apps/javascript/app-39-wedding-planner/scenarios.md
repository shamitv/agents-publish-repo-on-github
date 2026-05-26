# Chained Vulnerability Scenarios — Wedding Planner

## Chain: "Predictable Session Hijacking → IDOR Guest List Harvesting"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Predictable session key generation via Math.random() | Medium | A07 | `src/index.js` → `POST /api/auth/login` |
| 2 | Guest list is vulnerable to IDOR | Medium | A01 | `src/index.js` → `GET /api/events/:id/guests` |


**Attack narrative**: 1. The attacker observes that session cookies generated at login are numbers created via `Math.random()`.
2. The attacker guesses the active session ID of a wedding coordinator.
3. The attacker sets this hijacked cookie in their browser.
4. Using the hijacked session, the attacker makes a GET request to `/api/events/2/guests` to retrieve guest list records.
5. The guest lists are returned without checking if the hijacked user owns the event.

**Combined Impact**: `db_exfiltration` — Attacker hijacks victim accounts and harvests client guest databases.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
