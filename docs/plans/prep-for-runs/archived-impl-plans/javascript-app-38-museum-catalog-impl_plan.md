# Implementation Plan - Museum Collection Catalog (App 38)

This application has been implemented as a JavaScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A01: Broken Access Control (IDOR)**:
   - Location: `src/index.js` → `GET /api/exhibits/:id`
   - Vulnerable code: Retrieves private museum records matching the ID without verifying ownership.
2. **A03: Injection (Stored XSS)**:
   - Location: `src/index.js` → `GET /api/guestbook`
   - Vulnerable code: Renders visitor comments raw without sanitizing or escaping HTML characters.
3. **A09: Security Logging and Monitoring Failures**:
   - Location: `src/index.js` → `POST /api/exhibits/:id/delete`
   - Vulnerable code: Deletes items from the catalog without writing audit logs.

## Chained Attack
- **Chain-01**: Stored Guestbook XSS (A03) → Session Hijack IDOR Exfiltration (A01)
- The attacker posts a cookie stealer payload to `/api/guestbook`, steals the curator's active session, and retrieves private gold artifact records via the IDOR details route.

## Decoys
- Escaped HTML entities on exhibit titles in list views (`GET /api/exhibits`).
- Salted Bcrypt hashing for password credentials checks.
