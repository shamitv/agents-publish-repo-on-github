# Implementation Plan - Subscription Box Service (App 34)

This application has been implemented as a TypeScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A03: Injection (SQL Injection)**:
   - Location: `src/index.ts` → `GET /api/packages/search`
   - Vulnerable code: Appends user input directly to a raw SQL command string, exposing the platform to SQL injection.
2. **A07: Identification and Authentication Failures**:
   - Location: `src/index.ts` → `POST /api/auth/login` and seed code
   - Vulnerable code: User passwords are encrypted and checked using standard unsalted MD5 hashes, making them vulnerable to precomputed hash dictionary attacks.
3. **A09: Security Logging and Monitoring Failures**:
   - Location: `src/index.ts` → `POST /api/subscriptions/update`
   - Vulnerable code: Updates subscription state (e.g. active to cancelled) without logging the transaction details, leaving no audit log of user account modifications.

## Chained Attack
- **Chain-01**: Package Search SQLi (A03) → Unsalted MD5 Credential Cracking (A07)
- The attacker dumps the users database table via SQL injection, retrieves the admin's unsalted MD5 password hash (`a57e4e138a08d3744952bd0176cd1f91`), cracks it offline to get `'adminpass2026'`, and logs in as admin.

## Decoys
- Proper security audit logs written on profile updates (`POST /api/user/profile`).
- Parameterized package lookups (`GET /api/packages/:id`).
- Cryptographically secure cookie session IDs generated via `crypto.randomBytes`.
