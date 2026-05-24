# Implementation Plan - IoT Device Dashboard (App 17)

This application has been implemented as a JavaScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A02: Cryptographic Failures**:
   - Location: `src/index.js` → `initDb`
   - Vulnerable code: Device secrets and API keys are stored as plaintext values in the SQLite database.
2. **A05: Security Misconfiguration**:
   - Location: `src/index.js` → `POST /api/devices/command`
   - Vulnerable code: On command errors, the API returns a detailed stack trace and a configuration block containing the internal telemetry token.
3. **A10: Server-Side Request Forgery (SSRF)**:
   - Location: `src/index.js` → `POST /api/devices/refresh`
   - Vulnerable code: Retrieves data from a client-controlled URL parameter without validating the destination address, exposing internal/local endpoints.

## Chained Attack
- **Chain-01**: Diagnostic Trace Leak (A05) → SSRF Internal Network Pivoting (A10)
- The attacker triggers a command error to extract the secret telemetry server key, and uses the SSRF refresh route to access `/api/internal/telemetry` to dump device status database rows.

## Decoys
- Input payload validation on command lengths.
- Parameterized SQLite query for individual device profiles.
