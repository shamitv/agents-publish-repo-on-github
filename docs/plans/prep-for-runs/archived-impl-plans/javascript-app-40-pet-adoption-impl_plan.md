# Implementation Plan - Pet Adoption Portal (App 40)

This application has been implemented as a JavaScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A03: Injection (SQL Injection)**:
   - Location: `src/index.js` → `GET /api/pets/search`
   - Vulnerable code: User query parameter is directly concatenated into the SQL search statement.
2. **A05: Security Misconfiguration**:
   - Location: `src/index.js` → `GET /api/system/diagnostics`
   - Vulnerable code: Displays database settings and a hardcoded administrative recovery token (`PET-PORTAL-DEV-LAYOUT-KEY-2026`) if requested with `debug=true`.
3. **A08: Software and Data Integrity Failures (Insecure Deserialization)**:
   - Location: `src/index.js` → `POST /api/pets/layout`
   - Vulnerable code: Uses `eval()` to parse the layout configuration string.

## Chained Attack
- **Chain-01**: Diagnostics Configuration Disclosure (A05) → Remote Code Execution (A08)
- The attacker queries `/api/system/diagnostics?debug=true` to obtain the layout key, and calls `/api/pets/layout` passing the token to execute arbitrary JS payload via the eval() route.

## Decoys
- Parameterized SQLite query for individual pet detail lookups.
- Parameterized INSERT query on `/api/applications/apply`.
- Proper Bcrypt hashing for credentials storage.
