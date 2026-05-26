# Security Report: app-04 — Real Estate Listing Platform

**Language:** Python (Flask)
**Directory:** `apps/python/app-04-real-estate`

---

## Application Information
- **App ID:** app-04
- **Name:** Real Estate Listing Platform
- **Language:** Python
- **Framework:** Flask

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A03 | Injection | High | app.py | CWE-78 |
| V2 | A05 | Security Misconfiguration | Medium | app.py | CWE-1188 |
| V3 | A10 | Server-Side Request Forgery | High | app.py | CWE-918 |

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection

- **Severity:** High
- **Location:** `app.py`:130-155 (method: `process_image_metadata`)
- **CWE:** [CWE-78](https://cwe.mitre.org/data/definitions/78.html)

#### Description
OS Command Injection. The image analyzer tool uses subprocess.Popen with shell=True to execute a command containing an unvalidated property file path or image metadata name, permitting arbitrary shell execution

### VULN-02: A05 — Security Misconfiguration

- **Severity:** Medium
- **Location:** `app.py`:12-25 (method: `app_config`)
- **CWE:** [CWE-1188](https://cwe.mitre.org/data/definitions/1188.html)

#### Description
Security Misconfiguration. Flask debug mode is explicitly set to True in production run configs, and it utilizes a default widely known secret key (secret_key=dev), permitting session tampering and remote debugger access

### VULN-03: A10 — Server-Side Request Forgery

- **Severity:** High
- **Location:** `app.py`:165-190 (method: `import_external_image`)
- **CWE:** [CWE-918](https://cwe.mitre.org/data/definitions/918.html)

#### Description
Server-Side Request Forgery (SSRF). The remote image import endpoint fetches image resources from user-provided URLs using requests.get without validating, restricting, or sanitizing internal local network IPs


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Debug Environment Exposure → SSRF Internal Recon → OS Command Injection RCE

- **Combined Impact:** `lateral_movement`
- **Difficulty:** Medium
- **Subtlety Tags:** `cross_file` `direct_data_flow` `realistic_decoy`

#### Prerequisites
- attacker can reach the public request path
- attacker can control one request parameter or body field

#### Attack Narrative
Attacker reads internal environment variables via the exposed debug endpoint to discover service topology, then uses SSRF to probe internal endpoints and gather further context, then injects shell commands into the analyze endpoint to achieve RCE and exfiltrate data.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | GET /api/debug/env returns full process environment variables and working directory without authentication | Low | A05 | CWE-215 | app.py | `debug_env` |
| 2 | SSRF endpoint fetches arbitrary URLs with no IP-space restriction, enabling internal network mapping | High | A10 | CWE-918 | app.py | `import_external_image` |
| 3 | OS command injection via shell=True subprocess with user-controlled filename — executes arbitrary system commands | High | A03 | CWE-78 | app.py | `analyze_listing` |

### CHAIN-02: Subtle Ssrf Pivot To Injection

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
| 1 | Server-Side Request Forgery (SSRF). The remote image import endpoint fetches image resources from user-provided URLs using requests.get without validating, restricting, or sanitizing internal local network IPs | High | A10 | CWE-918 | app.py | `import_external_image` |
| 2 | Security Misconfiguration. Flask debug mode is explicitly set to True in production run configs, and it utilizes a default widely known secret key (secret_key=dev), permitting session tampering and remote debugger access | Medium | A05 | CWE-1188 | app.py | `app_config` |
| 3 | OS Command Injection. The image analyzer tool uses subprocess.Popen with shell=True to execute a command containing an unvalidated property file path or image metadata name, permitting arbitrary shell execution | High | A03 | CWE-78 | app.py | `process_image_metadata` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| app.py | Standard session authorization check before uploading property directories — secure auth decoy |
| app.py | Decoy secure parameterized SQL queries for standard listing searches — secure search decoy |
