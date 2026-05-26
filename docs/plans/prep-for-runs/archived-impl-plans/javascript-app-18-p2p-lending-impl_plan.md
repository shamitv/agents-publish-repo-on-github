# Implementation Plan - Peer-to-Peer Lending Platform (App 18)

This application has been implemented as a JavaScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A01: Broken Access Control (IDOR)**:
   - Location: `src/index.js` → `GET /api/contracts/:id`
   - Vulnerable code: Retrieves private lending agreement details matching the ID without verifying ownership by the caller.
2. **A02: Cryptographic Failures**:
   - Location: `src/index.js` → `initDb` and credentials storage
   - Vulnerable code: Storing borrower and lender passwords as plaintext strings in the SQLite database.
3. **A04: Insecure Design**:
   - Location: `src/index.js` → `POST /api/loans/apply`
   - Vulnerable code: Does not validate that the interest rate parameter is positive, allowing users to apply for negative-interest rate loans.

## Chained Attack
- **Chain-01**: Plaintext Credential Leak (A02) → IDOR Loan Data Harvesting (A01)
- The attacker reads user/admin passwords via `/api/debug/users`, logs in as admin, and fetches arbitrary borrower contracts via the IDOR details route.

## Decoys
- Strictly protected admin dashboard endpoint verifying administrative role limits.
- Parameterized UPDATE query logic in `/api/user/settings` to update profile values.
