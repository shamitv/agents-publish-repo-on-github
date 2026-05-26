# Implementation Plan - Recruitment ATS Platform (App 33)

This application has been implemented as a TypeScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A01: Broken Access Control (IDOR)**:
   - Location: `src/index.ts` → `GET /api/applications/:id`
   - Vulnerable code: Retrieves job applications matching the user-provided ID without validating candidate ownership or ensuring the caller holds a recruiter/admin role.
2. **A02: Cryptographic Failures**:
   - Location: `src/index.ts` → `POST /api/auth/api-key`
   - Vulnerable code: Generates user API keys using the MD5 hashing algorithm over the user's sequential integer ID, enabling trivial API key prediction.
3. **A06: Vulnerable and Outdated Components (Zip Slip)**:
   - Location: `src/index.ts` → `POST /api/applications/upload-portfolio`
   - Vulnerable code: Extracts uploaded portfolio ZIP files using raw entry names concatenated via `path.join()`, allowing directory traversal (`../`) and arbitrary file write/overwrite.

## Chained Attack
- **Chain-01**: Predictable API Key Derivation (A02) → Zip Slip Arbitrary File Write (A06)
- The attacker calculates the recruiter API key (`md5('3')` for user ID 3), authenticates to `/api/applications/upload-portfolio` using the key, and uploads a ZIP with traversal paths to overwrite server files.

## Decoys
- Proper Bcrypt hashing for password storage and credentials verification during user login.
- Strictly protected recruiter dashboard endpoint checks candidate roles.
- Ownership-limited query in `/api/applications/my` prevents IDOR when listing applicant histories.
