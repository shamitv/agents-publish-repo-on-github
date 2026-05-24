# Chained Vulnerability Scenarios — Music Streaming

## Chain: "Diagnostics Configuration Exposure → SSRF Playlist Analytics Pivoting"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Diagnostics status leaks metrics secret token key | Medium | A05 | `src/index.js` → `GET /api/system/status` |
| 2 | Cover art proxy is vulnerable to SSRF | High | A10 | `src/index.js` → `GET /api/cover` |


**Attack narrative**: 1. The attacker queries `/api/system/status?debug=true` to obtain the API key: `INTERNAL-METRICS-API-SECRET-2026`.
2. The attacker calls `/api/cover?url=http://localhost:8043/api/internal/analytics?token=INTERNAL-METRICS-API-SECRET-2026`.
3. The server makes the HTTP request, bypassing internal database controls using the leaked token, and returns all playlist database entries, achieving lateral movement.

**Combined Impact**: `lateral_movement` — Attacker bypasses firewall filters to retrieve internal playlist logs.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
