# Security Report: app-17 — IoT Device Dashboard

**Language:** Javascript (Express)
**Directory:** `apps/javascript/app-17-iot-dashboard`

---

## Application Information
- **App ID:** app-17
- **Name:** IoT Device Dashboard
- **Language:** Javascript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A05 | Security Misconfiguration | Medium | src/services/DeviceService.js | CWE-209 |
| V2 | A10 | Server-Side Request Forgery | High | src/services/RefreshService.js | CWE-918 |
| V3 | A02 | Cryptographic Failures | Medium | src/db/InMemoryStore.js | CWE-312 |
| V4 | A02 | Cryptographic Failures | Medium | src/services/TelemetryService.js | CWE-312 |

---

## Standalone Vulnerabilities

### VULN-01: A05 — Security Misconfiguration

- **Severity:** Medium
- **Location:** `src/services/DeviceService.js`:25-36 (method: `commandError`)
- **CWE:** [CWE-209](https://cwe.mitre.org/data/definitions/209.html)

#### Description
Verbose command errors return stack traces plus internal telemetry URL and access token.

### VULN-02: A10 — Server-Side Request Forgery

- **Severity:** High
- **Location:** `src/services/RefreshService.js`:4-8 (method: `refreshStatus`)
- **CWE:** [CWE-918](https://cwe.mitre.org/data/definitions/918.html)

#### Description
Device refresh fetches caller-controlled status URLs with axios and no internal network restrictions.

### VULN-03: A02 — Cryptographic Failures

- **Severity:** Medium
- **Location:** `src/db/InMemoryStore.js`:10-14 (method: `constructor`)
- **CWE:** [CWE-312](https://cwe.mitre.org/data/definitions/312.html)

#### Description
Device access tokens are stored as plaintext fields.

### VULN-04: A02 — Cryptographic Failures

- **Severity:** Medium
- **Location:** `src/services/TelemetryService.js`:7-17 (method: `internalTelemetry`)
- **CWE:** [CWE-312](https://cwe.mitre.org/data/definitions/312.html)

#### Description
Internal telemetry returns plaintext device tokens once the leaked telemetry token is supplied.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Debug Config Leak → HTTP SSRF → Plaintext Device Token Exposure → Lateral Movement

- **Combined Impact:** `lateral_movement`
- **Difficulty:** Medium
- **Subtlety Tags:** 

#### Prerequisites
- None specified

#### Attack Narrative
An authenticated user triggers a command error that leaks the internal telemetry URL and token, then uses the refresh SSRF endpoint to call telemetry and retrieve plaintext device tokens.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Command failure response leaks internal telemetry URL and access token. | Medium | A05 | CWE-209 | src/services/DeviceService.js | `commandError` |
| 2 | Device refresh fetches the attacker-supplied internal telemetry URL server-side. | Medium | A10 | CWE-918 | src/services/RefreshService.js | `refreshStatus` |
| 3 | Internal telemetry returns device records with plaintext device tokens. | Medium | A02 | CWE-312 | src/services/TelemetryService.js | `internalTelemetry` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/controllers/DeviceController.js | Device command payload validates command type and length before execution. |
| src/services/DeviceService.js | Public device detail response omits the deviceSecret field. |
| src/referenceGuards.js | Reference callback allowlist guard demonstrates safe URL validation. |
