# Security Report: app-33 — Recruitment ATS Platform

**Language:** Typescript (Express)
**Directory:** `apps/typescript/app-33-recruitment-ats`

---

## Application Information
- **App ID:** app-33
- **Name:** Recruitment ATS Platform
- **Language:** Typescript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | src/index.ts | CWE-639 |
| V2 | A02 | Cryptographic Failures | Medium | src/index.ts | CWE-328 |
| V3 | A06 | Vulnerable and Outdated Components | High | src/index.ts | CWE-22 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** Medium
- **Location:** `src/index.ts`:180-192 (method: `GET /api/applications/:id`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Retrieving a job application by ID lacks ownership or role checks, allowing any authenticated user to view other candidates' application details.

### VULN-02: A02 — Cryptographic Failures

- **Severity:** Medium
- **Location:** `src/index.ts`:172-177 (method: `POST /api/auth/api-key`)
- **CWE:** [CWE-328](https://cwe.mitre.org/data/definitions/328.html)

#### Description
Developer API tokens are generated using the insecure MD5 hashing algorithm on the user's sequential integer ID, making the keys highly predictable.

### VULN-03: A06 — Vulnerable and Outdated Components

- **Severity:** High
- **Location:** `src/index.ts`:195-238 (method: `POST /api/applications/upload-portfolio`)
- **CWE:** [CWE-22](https://cwe.mitre.org/data/definitions/22.html)

#### Description
The zip file upload handler extracts contents directly using relative file entry names without checking for directory traversal, exposing the system to Zip Slip path traversal file overwrite.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Predictable API Key Derivation → Zip Slip Arbitrary File Write

- **Combined Impact:** `data_modification`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
An attacker targets a recruiter account (user ID 3) and computes their MD5-based API key: md5('3') = 'eccbc87e4b5ce2fe28308fd9f2a7baf3'. Authenticating with this admin key, they call the `/api/applications/upload-portfolio` endpoint and upload a ZIP archive containing a file entry named `../../package.json` to overwrite the application root files.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | User API tokens are derived predictably from the user ID via MD5. | Medium | A02 | CWE-328 | src/index.ts | `POST /api/auth/api-key` |
| 2 | Admin endpoint extracts ZIP archives without validating target paths, enabling file overwrite. | Medium | A06 | CWE-22 | src/index.ts | `POST /api/applications/upload-portfolio` |

### CHAIN-02: Subtle Path Traversal Pivot To Idor

- **Combined Impact:** `data_modification`
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
| 1 | The zip file upload handler extracts contents directly using relative file entry names without checking for directory traversal, exposing the system to Zip Slip path traversal file overwrite. | High | A06 | CWE-22 | src/index.ts | `POST /api/applications/upload-portfolio` |
| 2 | Developer API tokens are generated using the insecure MD5 hashing algorithm on the user's sequential integer ID, making the keys highly predictable. | Medium | A02 | CWE-328 | src/index.ts | `POST /api/auth/api-key` |
| 3 | Retrieving a job application by ID lacks ownership or role checks, allowing any authenticated user to view other candidates' application details. | Medium | A01 | CWE-639 | src/index.ts | `GET /api/applications/:id` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.ts | Proper Bcrypt hashing for password storage and credentials verification during login. |
| src/index.ts | Proper application access control limits in GET /api/recruiter/dashboard checking for RECRUITER role. |
| src/index.ts | Proper ownership filtering in GET /api/applications/my ensuring candidates only read their own applications. |
