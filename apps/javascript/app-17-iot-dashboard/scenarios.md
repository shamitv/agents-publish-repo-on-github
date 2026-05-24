# Chained Vulnerability Scenarios — Iot Dashboard

## Chain: "Diagnostic Trace Leak → SSRF Internal Network Pivoting"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Stack trace leaks telemetry token key | Medium | A05 | `src/index.js` → `POST /api/devices/command` |
| 2 | Status fetch is vulnerable to SSRF | High | A10 | `src/index.js` → `POST /api/devices/refresh` |


**Attack narrative**: 1. The attacker triggers a command error by submitting `TRIGGER-ERROR`.
2. The server responds with an error trace containing: `telemetry_access_key: INTERNAL-SECRET-TELEMETRY-TOKEN-2026`.
3. The attacker calls `/api/devices/refresh` with `statusUrl: 'http://localhost:8017/api/internal/telemetry?token=INTERNAL-SECRET-TELEMETRY-TOKEN-2026'`.
4. The server makes the internal HTTP call, bypasses authentication checks using the token, and dumps the device keys database, achieving lateral movement.

**Combined Impact**: `lateral_movement` — Attacker gains access to sensitive internal telemetry configurations.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
