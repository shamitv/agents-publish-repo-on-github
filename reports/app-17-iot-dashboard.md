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
| V1 | A02 | Cryptographic Failures | Medium | src/index.js | CWE-312 |
| V2 | A05 | Security Misconfiguration | Medium | src/index.js | CWE-209 |
| V3 | A10 | Server-Side Request Forgery (SSRF) | High | src/index.js | CWE-918 |

---

## Standalone Vulnerabilities

### VULN-01: A02 — Cryptographic Failures

- **Severity:** Medium
- **Location:** `src/index.js`:47-56 (method: `initDb`)
- **CWE:** [CWE-312](https://cwe.mitre.org/data/definitions/312.html)

#### Description
Device secret access keys are stored in plaintext in the database instead of being hashed or encrypted.

### VULN-02: A05 — Security Misconfiguration

- **Severity:** Medium
- **Location:** `src/index.js`:131-163 (method: `POST /api/devices/command`)
- **CWE:** [CWE-209](https://cwe.mitre.org/data/definitions/209.html)

#### Description
Detailed configuration details (such as API secret keys) and stack traces are returned to the user on execution failure.

### VULN-03: A10 — Server-Side Request Forgery (SSRF)

- **Severity:** High
- **Location:** `src/index.js`:166-182 (method: `POST /api/devices/refresh`)
- **CWE:** [CWE-918](https://cwe.mitre.org/data/definitions/918.html)

#### Description
The device status refresh handler calls external URLs using axios without validating if the IP is internal, allowing SSRF.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Diagnostic Trace Leak → SSRF Internal Network Pivoting

- **Combined Impact:** `lateral_movement`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
An attacker sends a TRIGGER-ERROR command to `/api/devices/command` to force a server exception, which leaks the telemetry API credentials: `INTERNAL-SECRET-TELEMETRY-TOKEN-2026`. The attacker then makes a POST request to `/api/devices/refresh` with `statusUrl: 'http://localhost:8017/api/internal/telemetry?token=INTERNAL-SECRET-TELEMETRY-TOKEN-2026'`, leveraging the SSRF vulnerability to bypass authentication and exfiltrate internal system telemetry.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Verbose stack trace leaks internal telemetry server token. | Medium | A05 | CWE-209 | src/index.js | `POST /api/devices/command` |
| 2 | Status update proxy fetches internal endpoints without IP filtering. | Medium | A10 | CWE-918 | src/index.js | `POST /api/devices/refresh` |

### CHAIN-02: Subtle Ssrf Pivot To Crypto

- **Combined Impact:** `lateral_movement`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy` `secondary_chain`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
Attacker combines a low-visibility entry point with stored or derived application state, then pivots to a higher-impact sink that is reachable only after following the cross-file flow.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | The device status refresh handler calls external URLs using axios without validating if the IP is internal, allowing SSRF. | High | A10 | CWE-918 | src/index.js | `POST /api/devices/refresh` |
| 2 | Detailed configuration details (such as API secret keys) and stack traces are returned to the user on execution failure. | Medium | A05 | CWE-209 | src/index.js | `POST /api/devices/command` |
| 3 | Device secret access keys are stored in plaintext in the database instead of being hashed or encrypted. | Medium | A02 | CWE-312 | src/index.js | `initDb` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.js | Proper input validation on device command payload sizes in POST /api/devices/command. |
| src/index.js | Proper parameterized query logic in GET /api/devices/:id to fetch device details safely. |
