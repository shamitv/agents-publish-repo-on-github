# Security Report: app-47 — Smart Home Device Manager

**Language:** Python (Fastapi)
**Directory:** `apps/python/app-47-smart-home`

---

## Application Information
- **App ID:** app-47
- **Name:** Smart Home Device Manager
- **Language:** Python
- **Framework:** Fastapi

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A05 | Security Misconfiguration | High | app.py | CWE-200 |
| V2 | A08 | Software and Data Integrity Failures | High | app.py | CWE-494 |
| V3 | A10 | Server-Side Request Forgery | Medium | app.py | CWE-918 |

---

## Standalone Vulnerabilities

### VULN-01: A05 — Security Misconfiguration

- **Severity:** High
- **Location:** `app.py`:110-118 (method: `debug_devices`)
- **CWE:** [CWE-200](https://cwe.mitre.org/data/definitions/200.html)

#### Description
An unauthenticated debug endpoint (/api/debug/devices) is exposed, leaking details of all registered devices along with their private access API tokens.

### VULN-02: A08 — Software and Data Integrity Failures

- **Severity:** High
- **Location:** `app.py`:132-163 (method: `update_firmware`)
- **CWE:** [CWE-494](https://cwe.mitre.org/data/definitions/494.html)

#### Description
The firmware update endpoint accepts any URL and downloads the firmware binary without checking signatures, hashes, or origin authority.

### VULN-03: A10 — Server-Side Request Forgery

- **Severity:** Medium
- **Location:** `app.py`:120-130 (method: `fetch_sensor_data`)
- **CWE:** [CWE-918](https://cwe.mitre.org/data/definitions/918.html)

#### Description
The sensor data proxy endpoint processes user-provided URLs without validating if they point to private network addresses or internal hosts, allowing SSRF.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Debug Token Leak → SSRF Internal Recon → Unsigned Firmware Injection

- **Combined Impact:** `lateral_movement`
- **Difficulty:** Expert
- **Subtlety Tags:** `cross_file` `state_confusion` `parser_or_config_reasoning` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker can influence a multi-step workflow
- attacker can observe or reuse application state across requests

#### Attack Narrative
An attacker queries the public /api/debug/devices debug endpoint to leak private device tokens. They then use the SSRF vulnerability in the sensor proxy endpoint to scan internal port ranges and locate private network hosts. Finally, the attacker uses the firmware update endpoint to point a device to a malicious unsigned binary stored on an internal host, achieving persistent compromise of the smart device.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Debug endpoint leaks device tokens. | Medium | A05 | CWE-200 | app.py | `debug_devices` |
| 2 | SSRF in sensor data proxy allows internal service scanning. | Medium | A10 | CWE-918 | app.py | `fetch_sensor_data` |
| 3 | Firmware update accepts arbitrary unsigned firmware binaries. | Medium | A08 | CWE-494 | app.py | `update_firmware` |

### CHAIN-02: Subtle Ssrf Pivot To Auth Session

- **Combined Impact:** `lateral_movement`
- **Difficulty:** Expert
- **Subtlety Tags:** `cross_file` `state_confusion` `parser_or_config_reasoning` `implicit_trust` `realistic_decoy` `secondary_chain`

#### Prerequisites
- attacker can influence a multi-step workflow
- attacker can observe or reuse application state across requests

#### Attack Narrative
Attacker combines a low-visibility entry point with stored or derived application state, then pivots to a higher-impact sink that is reachable only after following the cross-file flow.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | The sensor data proxy endpoint processes user-provided URLs without validating if they point to private network addresses or internal hosts, allowing SSRF. | Medium | A10 | CWE-918 | app.py | `fetch_sensor_data` |
| 2 | The firmware update endpoint accepts any URL and downloads the firmware binary without checking signatures, hashes, or origin authority. | High | A08 | CWE-494 | app.py | `update_firmware` |
| 3 | An unauthenticated debug endpoint (/api/debug/devices) is exposed, leaking details of all registered devices along with their private access API tokens. | High | A05 | CWE-200 | app.py | `debug_devices` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| app.py | Proper validation of the X-Device-Token header against registered device tokens in /api/devices/{device_id}/command, preventing command injection or spoofing. |
| app.py | Rate-limited status polling on /api/devices/{device_id}/status using an in-memory timestamp store to enforce a request cooldown period. |
