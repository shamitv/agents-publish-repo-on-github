# Security Report: app-42 — Construction Project Tracker

**Language:** Javascript (Express)
**Directory:** `apps/javascript/app-42-construction-tracker`

---

## Application Information
- **App ID:** app-42
- **Name:** Construction Project Tracker
- **Language:** Javascript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | src/index.js | CWE-639 |
| V2 | A08 | Software and Data Integrity Failures | High | src/index.js | CWE-502 |
| V3 | A09 | Security Logging and Monitoring Failures | Low | src/index.js | CWE-778 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** Medium
- **Location:** `src/index.js`:136-152 (method: `GET /api/contracts/:id`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Viewing project contracts by ID lacks verification of user ownership, allowing any authenticated user to retrieve details of another manager's contracts.

### VULN-02: A08 — Software and Data Integrity Failures

- **Severity:** High
- **Location:** `src/index.js`:155-170 (method: `POST /api/contracts/template`)
- **CWE:** [CWE-502](https://cwe.mitre.org/data/definitions/502.html)

#### Description
Template layout parameters are deserialized using the insecure eval() constructor, enabling remote code execution on the hosting server.

### VULN-03: A09 — Security Logging and Monitoring Failures

- **Severity:** Low
- **Location:** `src/index.js`:184-206 (method: `POST /api/contracts/:id/delete`)
- **CWE:** [CWE-778](https://cwe.mitre.org/data/definitions/778.html)

#### Description
Deleting sensitive construction contracts from the system tracker produces no audit logs, blindfolding administrators to data removal.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: IDOR Information Mining → Insecure Deserialization Remote Code Execution

- **Combined Impact:** `account_takeover`
- **Difficulty:** Expert
- **Subtlety Tags:** `cross_file` `state_confusion` `parser_or_config_reasoning` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker can influence a multi-step workflow
- attacker can observe or reuse application state across requests

#### Attack Narrative
An attacker logs in, retrieves construction contract details by calling `/api/contracts/1` (IDOR), and copies details. They then POST a template config to `/api/contracts/template` containing a system command execution payload (such as `require('child_process').execSync(...)`) evaluated unsafely via eval(), achieving Remote Code Execution.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Contracts endpoint permits IDOR details mining. | Medium | A01 | CWE-639 | src/index.js | `GET /api/contracts/:id` |
| 2 | Template processing executes user-submitted custom layouts via eval(). | Medium | A08 | CWE-502 | src/index.js | `POST /api/contracts/template` |

### CHAIN-02: Subtle State Confusion Pivot To Idor

- **Combined Impact:** `account_takeover`
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
| 1 | Deleting sensitive construction contracts from the system tracker produces no audit logs, blindfolding administrators to data removal. | Low | A09 | CWE-778 | src/index.js | `POST /api/contracts/:id/delete` |
| 2 | Template layout parameters are deserialized using the insecure eval() constructor, enabling remote code execution on the hosting server. | High | A08 | CWE-502 | src/index.js | `POST /api/contracts/template` |
| 3 | Viewing project contracts by ID lacks verification of user ownership, allowing any authenticated user to retrieve details of another manager's contracts. | Medium | A01 | CWE-639 | src/index.js | `GET /api/contracts/:id` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.js | Proper Bcrypt hashing for password storage and validation. |
| src/index.js | Proper role restriction on GET /api/admin/stats checking for ADMIN role. |
