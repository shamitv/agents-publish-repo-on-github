# Chained Vulnerability Scenarios — IoT Dashboard

Supplemental notes only. Ground truth vulnerability data is maintained in [.vulns](.vulns), and the required human-readable chain is in [README.md](README.md).

## Chain: "Debug Config Leak → HTTP SSRF → Plaintext Device Token Exposure"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Command error response leaks telemetry URL and token | Medium | A05 | `DeviceService.js` → `commandError()` |
| 2 | Status refresh fetches arbitrary URLs server-side | Medium | A10 | `RefreshService.js` → `refreshStatus()` |
| 3 | Internal telemetry returns plaintext device tokens | Medium | A02 | `TelemetryService.js` → `internalTelemetry()` |

**Attack narrative**: The attacker triggers `TRIGGER-ERROR`, extracts the telemetry URL and token, then sends that URL to `/api/devices/refresh` so the server reaches internal telemetry and returns device keys.

**Combined Impact**: Lateral movement into internal telemetry with plaintext device token exposure.
