# Security Report: app-15 — Digital Asset Management

**Language:** Typescript (Express)
**Directory:** `apps/typescript/app-15-digital-assets`

---

## Application Information
- **App ID:** app-15
- **Name:** Digital Asset Management
- **Language:** Typescript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | High | src/index.ts | CWE-639 |
| V2 | A08 | Software and Data Integrity Failures | High | src/index.ts | CWE-434 |
| V3 | A10 | Server-Side Request Forgery | Medium | src/index.ts | CWE-918 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** High
- **Location:** `src/index.ts`:135-156 (method: `GET /api/assets/:id`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Asset detail endpoint returns private files and download URLs by ID without checking if the requesting user owns the asset.

### VULN-02: A08 — Software and Data Integrity Failures

- **Severity:** High
- **Location:** `src/index.ts`:158-182 (method: `POST /api/assets/upload`)
- **CWE:** [CWE-434](https://cwe.mitre.org/data/definitions/434.html)

#### Description
Upload endpoint uses Multer disk storage and accepts any file extension with no validation, writing files directly into the web-accessible directory.

### VULN-03: A10 — Server-Side Request Forgery

- **Severity:** Medium
- **Location:** `src/index.ts`:184-228 (method: `POST /api/assets/import`)
- **CWE:** [CWE-918](https://cwe.mitre.org/data/definitions/918.html)

#### Description
Import endpoint fetches file content from user-specified URLs using the global fetch API without restricting requests to loopback or private IP ranges.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: SSRF File Fetch → Predictable Path RCE

- **Combined Impact:** `lateral_movement`
- **Difficulty:** Medium
- **Subtlety Tags:** `cross_file` `direct_data_flow` `realistic_decoy`

#### Prerequisites
- attacker can reach the public request path
- attacker can control one request parameter or body field

#### Attack Narrative
An attacker uses the SSRF vulnerability on the import endpoint to fetch a script from an internal service or external host. The file is saved directly into the public web directory (`/uploads/`) with its original filename due to unvalidated upload logic, allowing the attacker to execute it via direct HTTP request.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | SSRF in asset import fetches arbitrary network URLs. | Medium | A10 | CWE-918 | src/index.ts | `POST /api/assets/import` |
| 2 | Unrestricted file writing places fetched script inside web public uploads directory, enabling RCE. | Medium | A08 | CWE-434 | src/index.ts | `POST /api/assets/import` |

### CHAIN-02: Subtle Ssrf Pivot To Ssrf

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
| 1 | Import endpoint fetches file content from user-specified URLs using the global fetch API without restricting requests to loopback or private IP ranges. | Medium | A10 | CWE-918 | src/index.ts | `POST /api/assets/import` |
| 2 | Upload endpoint uses Multer disk storage and accepts any file extension with no validation, writing files directly into the web-accessible directory. | High | A08 | CWE-434 | src/index.ts | `POST /api/assets/upload` |
| 3 | Asset detail endpoint returns private files and download URLs by ID without checking if the requesting user owns the asset. | High | A01 | CWE-639 | src/index.ts | `GET /api/assets/:id` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.ts | Input validation guardrail on tags endpoint check, ensuring tag content is strictly alphanumeric via regex. |
| src/index.ts | Secure Bearer Authorization token checking requirement on the administrative statistics stats endpoint. |
