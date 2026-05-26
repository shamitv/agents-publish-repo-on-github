# Chained Vulnerability Scenarios — Social Analytics

Supplemental notes only. Ground truth vulnerability data is maintained in [.vulns](.vulns), and the required human-readable chain is in [README.md](README.md).

## Chain: "Debug Config Leak → HTTP SSRF → Internal Search Pivot"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `GET /api/debug/config` exposes internal service URL and token | Medium | A05 | `DebugController.ts` → `getConfig()` |
| 2 | `POST /api/preview` fetches arbitrary URLs server-side | Medium | A10 | `PreviewService.ts` → `fetchPreview()` |
| 3 | Internal search admin trusts the leaked token and returns topology | Low | A01 | `InternalSearchService.ts` → `adminSearch()` |

**Attack narrative**: The attacker reads debug configuration, constructs the internal search admin URL with the leaked token, then submits it to the preview endpoint so the server reaches an internal service on the attacker's behalf.

**Combined Impact**: Lateral movement into internal search/service metadata.
