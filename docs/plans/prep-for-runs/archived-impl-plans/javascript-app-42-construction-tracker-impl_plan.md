# Implementation Plan - Construction Project Tracker (App 42)

This application has been implemented as a JavaScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A01: Broken Access Control (IDOR)**:
   - Location: `src/index.js` → `GET /api/contracts/:id`
   - Vulnerable code: Retrieves project contracts matching the ID without verifying ownership.
2. **A08: Software and Data Integrity Failures (Insecure Deserialization)**:
   - Location: `src/index.js` → `POST /api/contracts/template`
   - Vulnerable code: Uses `eval()` to parse the layout configuration string.
3. **A09: Security Logging and Monitoring Failures**:
   - Location: `src/index.js` → `POST /api/contracts/:id/delete`
   - Vulnerable code: Deletes contracts from the database without generating audit logs.

## Chained Attack
- **Chain-01**: IDOR Information Mining (A01) → Insecure Deserialization Remote Code Execution (A08)
- The attacker queries `/api/contracts/1` to mine project parameters, and calls `/api/contracts/template` with a payload executing shell commands via the eval() endpoint.

## Decoys
- Safe role-based protection on `/api/admin/stats`.
- Proper Bcrypt hashing for credentials storage.
