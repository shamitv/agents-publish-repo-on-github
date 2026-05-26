# Security Report: app-14 — Telemedicine Appointment System

**Language:** Typescript (Express)
**Directory:** `apps/typescript/app-14-telemedicine`

---

## Application Information
- **App ID:** app-14
- **Name:** Telemedicine Appointment System
- **Language:** Typescript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | High | src/index.ts | CWE-639 |
| V2 | A02 | Cryptographic Failures | High | src/index.ts | CWE-327 |
| V3 | A07 | Identification and Authentication Failures | Medium | src/index.ts | CWE-1004 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** High
- **Location:** `src/index.ts`:204-229 (method: `GET /api/appointments/:id`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Appointment details endpoint retrieves private physician notes and patient PII by ID without checking if the requesting user is the patient or doctor assigned to the appointment.

### VULN-02: A02 — Cryptographic Failures

- **Severity:** High
- **Location:** `src/index.ts`:11-13 (method: `generateJWT`)
- **CWE:** [CWE-327](https://cwe.mitre.org/data/definitions/327.html)

#### Description
Authentication tokens are signed with a weak, hardcoded secret ('healthcare123') using HS256, allowing offline key cracking or token forgery.

### VULN-03: A07 — Identification and Authentication Failures

- **Severity:** Medium
- **Location:** `src/index.ts`:151-158 (method: `login`)
- **CWE:** [CWE-1004](https://cwe.mitre.org/data/definitions/1004.html)

#### Description
Session token cookie is set with httpOnly: false, permitting client-side scripts to access it and exposing users to session hijacking via XSS.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Weak JWT Signatures → IDOR Records Exfiltration

- **Combined Impact:** `db_exfiltration`
- **Difficulty:** Medium
- **Subtlety Tags:** `cross_file` `direct_data_flow` `realistic_decoy`

#### Prerequisites
- attacker can reach the public request path
- attacker can control one request parameter or body field

#### Attack Narrative
An attacker cracks or guesses the weak JWT secret offline, then crafts a custom JWT asserting a doctor role. Using this forged token, they query the appointment details endpoint to exfiltrate private patient records and doctor consultation notes via IDOR.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | JWT signed with weak secret key. | Medium | A02 | CWE-327 | src/index.ts | `login` |
| 2 | IDOR on appointment endpoint reveals sensitive notes and details. | Medium | A01 | CWE-639 | src/index.ts | `GET /api/appointments/:id` |

### CHAIN-02: Subtle Auth Session Pivot To Idor

- **Combined Impact:** `db_exfiltration`
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
| 1 | Session token cookie is set with httpOnly: false, permitting client-side scripts to access it and exposing users to session hijacking via XSS. | Medium | A07 | CWE-1004 | src/index.ts | `login` |
| 2 | Authentication tokens are signed with a weak, hardcoded secret ('healthcare123') using HS256, allowing offline key cracking or token forgery. | High | A02 | CWE-327 | src/index.ts | `generateJWT` |
| 3 | Appointment details endpoint retrieves private physician notes and patient PII by ID without checking if the requesting user is the patient or doctor assigned to the appointment. | High | A01 | CWE-639 | src/index.ts | `GET /api/appointments/:id` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.ts | Proper Bcrypt hashing for password storage and credentials check during login. |
| src/index.ts | Scoped list view `/api/appointments` restricting standard patient users to only see their own appointments. |
