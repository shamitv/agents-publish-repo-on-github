# Implementation Plan - Customer Support Ticket System (App 32)

This application has been implemented as a TypeScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A01: Broken Access Control (IDOR)**:
   - Location: `src/index.ts` → `GET /api/tickets/:id`
   - Vulnerable code: Retrieves ticket details matching user-provided ID parameter without checking if the authenticated user owns the ticket or is an administrator.
2. **A03: Injection (SQL Injection)**:
   - Location: `src/index.ts` → `GET /api/tickets/search`
   - Vulnerable code: User-supplied query input is directly interpolated into a raw SQL query.
3. **A05: Security Misconfiguration**:
   - Location: `src/index.ts` → `GET /api/system/health`
   - Vulnerable code: If the diagnostic flag is provided, the system returns internal database config and a hardcoded recovery key `SUPPORT-ADMIN-DEV-RECOVERY-KEY-2026`.

## Chained Attack
- **Chain-01**: Verbose Diagnostics Exposure (A05) → Administrative Ticket Export Bypass (A01)
- The attacker queries `/api/system/health?diagnostics=true` to obtain the admin recovery token, and passes it to `/api/admin/export` to extract all support tickets and users in bulk.

## Decoys
- Proper Bcrypt hashing for password storage and credentials validation during user login.
- Parameterized SQLite query logic in `POST /api/tickets` to create tickets safely.
- Proper access ownership check in `/api/users/profile` to prevent IDOR on profile records.
