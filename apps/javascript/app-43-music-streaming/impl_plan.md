# Implementation Plan - Music Streaming Playlist Service (App 43)

This application has been implemented as a JavaScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A01: Broken Access Control (IDOR)**:
   - Location: `src/index.js` → `GET /api/playlists/:id`
   - Vulnerable code: Retrieves private playlist details matching the ID without verifying ownership.
2. **A05: Security Misconfiguration**:
   - Location: `src/index.js` → `GET /api/system/status`
   - Vulnerable code: Displays database settings and a hardcoded metrics integration API token (`INTERNAL-METRICS-API-SECRET-2026`) if requested with `debug=true`.
3. **A10: Server-Side Request Forgery (SSRF)**:
   - Location: `src/index.js` → `GET /api/cover`
   - Vulnerable code: Refreshes cover art from a user-supplied URL parameter without validation or IP blocking.

## Chained Attack
- **Chain-01**: Diagnostics Configuration Exposure (A05) → SSRF Playlist Analytics Pivoting (A10)
- The attacker queries `/api/system/status?debug=true` to obtain the metrics API key, and calls the cover proxy `/api/cover?url=...` to access the internal analytics logs.

## Decoys
- Scoped playlist database views limit basic listeners to their own data rows.
- Parameterized SQLite query for adding tracks to playlists safely.
