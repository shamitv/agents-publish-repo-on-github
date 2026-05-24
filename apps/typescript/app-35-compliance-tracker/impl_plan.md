# Implementation Plan - Compliance Document Tracker (App 35)

This application has been implemented as a TypeScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A01: Broken Access Control (IDOR)**:
   - Location: `src/index.ts` → `GET /api/documents/:id`
   - Vulnerable code: Retrieves compliance documents from the database matching the user-supplied ID without verifying ownership or checking admin status.
2. **A05: Security Misconfiguration**:
   - Location: `src/index.ts` → `GET /api/admin/debug`
   - Vulnerable code: Displays developer configurations, database paths, and a hardcoded administration key `ADMIN-DEV-TOKEN-KEY-8871` if requested with `dev=true`.
3. **A08: Software and Data Integrity Failures (Insecure Deserialization)**:
   - Location: `src/index.ts` → `POST /api/documents`
   - Vulnerable code: Deserializes the metadata parameter using `eval()`, exposing the server to Remote Code Execution (RCE).

## Chained Attack
- **Chain-01**: Dev Mode Config Leak (A05) → Admin Document Retrieval Bypass (A01)
- The attacker queries `/api/admin/debug?dev=true` to obtain the admin token, then passes it in the `x-admin-token` header to access `/api/documents/:id`, retrieving private customer records.

## Decoys
- Proper Bcrypt hashing for password storage and validation.
- User profile retrieval `/api/users/me` uses strict authorization rules.
- Safe JSON metadata parsing `/api/documents/safe` uses standard `JSON.parse`.
