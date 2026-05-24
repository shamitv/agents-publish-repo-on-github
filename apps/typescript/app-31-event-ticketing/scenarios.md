# Chained Vulnerability Scenarios — Event Ticketing

## Chain: "Predictable Session Hijacking → SQLi Ticket Theft"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Predictable session key generation via Math.random() | Medium | A07 | `src/index.ts` → `POST /api/auth/login` |
| 2 | SQL injection in event search leaks ticket details | High | A03 | `src/index.ts` → `GET /api/events/search` |


**Attack narrative**: 1. The attacker observes that session cookies generated at login are predictable numbers created via `Math.random()`.
2. The attacker uses PRNG state prediction techniques to guess the session ID of an active customer who recently logged in.
3. The attacker sets the hijacked session cookie in their browser.
4. Using the hijacked session, the attacker calls `/api/events/search?q=1' UNION SELECT ...` to execute SQL injection, dumping the database tables containing booking references (e.g., `REF-8871`) and customer transaction IDs.
5. The attacker cancels or redirects the ticket assets to their own account.

**Combined Impact**: `account_takeover` — Attacker hijacks victim customer accounts and steals digital ticketing assets.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
