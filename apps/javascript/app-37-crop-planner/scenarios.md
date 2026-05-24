# Chained Vulnerability Scenarios — Crop Planner

## Chain: "Diagnostics Configuration Exposure → SSRF Crop Analytics Pivoting"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Diagnostics config leaks weather secret token key | Medium | A05 | `src/index.js` → `GET /api/system/config` |
| 2 | Weather proxy is vulnerable to SSRF | High | A10 | `src/index.js` → `GET /api/weather/proxy` |


**Attack narrative**: 1. The attacker queries `/api/system/config?debug=true` to obtain the API key: `CROP-DEV-WEATHER-API-TOKEN-2026`.
2. The attacker calls `/api/weather/proxy?weatherUrl=http://localhost:8037/api/internal/telemetry?token=CROP-DEV-WEATHER-API-TOKEN-2026`.
3. The server makes the HTTP request, bypassing internal database controls using the leaked token, and returns all crop database entries, achieving lateral movement.

**Combined Impact**: `lateral_movement` — Attacker bypasses firewall filters to retrieve internal crops logs.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
