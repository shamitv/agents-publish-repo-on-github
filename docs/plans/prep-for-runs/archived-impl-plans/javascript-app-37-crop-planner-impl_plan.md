# Implementation Plan - Agricultural Crop Planner (App 37)

This application has been implemented as a JavaScript Express microservice with an in-memory SQLite database.

## Planted Vulnerabilities
1. **A05: Security Misconfiguration**:
   - Location: `src/index.js` → `GET /api/system/config`
   - Vulnerable code: Displays database settings and a hardcoded weather integration API token (`CROP-DEV-WEATHER-API-TOKEN-2026`) if requested with `debug=true`.
2. **A06: Vulnerable and Outdated Components (Zip Slip)**:
   - Location: `src/index.js` → `POST /api/crop-plan/import-layout`
   - Vulnerable code: Extracts uploaded crop layouts in a ZIP using raw entry names concatenated via `path.join()`, allowing directory traversal (`../`) and arbitrary file write/overwrite.
3. **A10: Server-Side Request Forgery (SSRF)**:
   - Location: `src/index.js` → `GET /api/weather/proxy`
   - Vulnerable code: Refreshes weather telemetry from a user-supplied URL parameter without validation or IP blocking.

## Chained Attack
- **Chain-01**: Diagnostics Configuration Exposure (A05) → SSRF Crop Analytics Pivoting (A10)
- The attacker queries `/api/system/config?debug=true` to obtain the weather service API key, and calls the weather lookup proxy `/api/weather/proxy?weatherUrl=...` to access the internal telemetry logs.

## Decoys
- Scoped crop database views limit basic farmers to their own data rows.
- Parameterized SQLite query for individual crop detail lookups.
