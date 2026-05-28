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
| V1 | A07 | Identification and Authentication Failures | High | src/services/TokenService.ts | CWE-347 |
| V2 | A01 | Broken Access Control | High | src/services/AppointmentService.ts | CWE-639 |
| V3 | A02 | Cryptographic Failures | Medium | src/config/appConfig.ts | CWE-321 |
| V4 | A07 | Identification and Authentication Failures | Medium | src/controllers/AuthController.ts | CWE-1004 |

---

## Standalone Vulnerabilities

### VULN-01: A07 — Identification and Authentication Failures

- **Severity:** High
- **Location:** `src/services/TokenService.ts`:12-18 (method: `verify`)
- **CWE:** [CWE-347](https://cwe.mitre.org/data/definitions/347.html)

#### Description
JWT validation decodes token payloads without verifying signatures, allowing forged claims.

### VULN-02: A01 — Broken Access Control

- **Severity:** High
- **Location:** `src/services/AppointmentService.ts`:25-39 (method: `getAppointmentDetail`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Appointment detail lookup returns physician notes by ID without patient or doctor ownership checks.

### VULN-03: A02 — Cryptographic Failures

- **Severity:** Medium
- **Location:** `src/config/appConfig.ts`:10-17 (method: `appConfig`)
- **CWE:** [CWE-321](https://cwe.mitre.org/data/definitions/321.html)

#### Description
JWT signing secret defaults to a weak hardcoded value.

### VULN-04: A07 — Identification and Authentication Failures

- **Severity:** Medium
- **Location:** `src/controllers/AuthController.ts`:23-29 (method: `login`)
- **CWE:** [CWE-1004](https://cwe.mitre.org/data/definitions/1004.html)

#### Description
Session token cookie is set without httpOnly or secure flags.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Weak JWT Validation → Patient Notes IDOR → DB Exfiltration

- **Combined Impact:** `db_exfiltration`
- **Difficulty:** Medium
- **Subtlety Tags:** 

#### Prerequisites
- None specified

#### Attack Narrative
An attacker forges a JWT payload because the server decodes tokens without signature validation, then enumerates appointment IDs to retrieve confidential physician notes.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | TokenService.verify decodes JWT payloads without validating the signature. | Medium | A07 | CWE-347 | src/services/TokenService.ts | `verify` |
| 2 | Appointment details are loaded by ID and include physician notes without ownership checks. | Medium | A01 | CWE-639 | src/services/AppointmentService.ts | `getAppointmentDetail` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/repositories/UserRepository.ts | Registered patient passwords are hashed with BCrypt before storage. |
| src/services/AppointmentService.ts | Appointment list view removes doctorNotes for patient and doctor summaries. |
| src/referenceGuards.ts | Reference ownership and callback guards demonstrate safe comparison and allowlist patterns. |
