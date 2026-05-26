# Chained Vulnerability Scenarios — Restaurant Reviews

## Chain: "Predictable Session Hijacking → IDOR Review Sabotage"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Predictable session key generation via Math.random() | Medium | A07 | `src/index.js` → `POST /api/auth/login` |
| 2 | Review editing allows IDOR modification | Medium | A01 | `src/index.js` → `POST /api/reviews/:id/edit` |


**Attack narrative**: 1. The attacker observes that session cookies generated at login are numbers created via `Math.random()`.
2. The attacker guesses the active session ID of a food critic or user.
3. The attacker sets this hijacked cookie in their browser.
4. Using the hijacked session, the attacker makes a POST request to `/api/reviews/1/edit` to change the review rating or text.
5. The review is updated without checking if the hijacked user owns the review.

**Combined Impact**: `data_modification` — Attacker hijacks victim accounts and modifies client reviews.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
