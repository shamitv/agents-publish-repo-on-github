# Security Report: app-24 — Veterinary Clinic Management

**Language:** Python (Fastapi)
**Directory:** `apps/python/app-24-vet-clinic`

---

## Application Information
- **App ID:** app-24
- **Name:** Veterinary Clinic Management
- **Language:** Python
- **Framework:** Fastapi

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A02 | Cryptographic Failures | High | app.py | CWE-327 |
| V2 | A03 | Injection | High | app.py | CWE-89 |
| V3 | A09 | Security Logging & Monitoring Failures | Medium | app.py | CWE-778 |

---

## Standalone Vulnerabilities

### VULN-01: A02 — Cryptographic Failures

- **Severity:** High
- **Location:** `app.py`:16-19 (method: `generate_token`)
- **CWE:** [CWE-327](https://cwe.mitre.org/data/definitions/327.html)

#### Description
JWT authentication tokens are signed with a weak, hardcoded secret ('secret123') using HS256, allowing an attacker to forge arbitrary tokens (such as possessing a VET or ADMIN role).

### VULN-02: A03 — Injection

- **Severity:** High
- **Location:** `app.py`:174-191 (method: `search_pets`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
The pet search endpoint concatenates user input directly into a raw SQL query, allowing SQL injection to bypass role checks or leak DB records.

### VULN-03: A09 — Security Logging & Monitoring Failures

- **Severity:** Medium
- **Location:** `app.py`:206-226 (method: `update_prescription`)
- **CWE:** [CWE-778](https://cwe.mitre.org/data/definitions/778.html)

#### Description
Modifications to drug prescriptions (such as controlled substances like Ketamine) produce no audit logs or monitoring warnings, permitting undetected dosage alteration.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Weak JWT → SQL Injection → Prescription Tampering

- **Combined Impact:** `data_modification`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
An attacker cracks or guesses the weak JWT secret, forging a Veterinarian ('VET') session token. They then use the SQL injection vulnerability on the pet search endpoint to enumerate pet IDs and find targeted records. Finally, they call the prescription update endpoint to alter controlled substance prescriptions undetected due to the absence of logging.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | JWT signed with easily guessable hardcoded secret key. | Medium | A02 | CWE-327 | app.py | `generate_token` |
| 2 | SQL injection in pet search allows database exploration. | Medium | A03 | CWE-89 | app.py | `search_pets` |
| 3 | Prescription updating produces no audit logs. | Low | A09 | CWE-778 | app.py | `update_prescription` |

### CHAIN-02: Subtle State Confusion Pivot To Auth Session

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
| 1 | Modifications to drug prescriptions (such as controlled substances like Ketamine) produce no audit logs or monitoring warnings, permitting undetected dosage alteration. | Medium | A09 | CWE-778 | app.py | `update_prescription` |
| 2 | The pet search endpoint concatenates user input directly into a raw SQL query, allowing SQL injection to bypass role checks or leak DB records. | High | A03 | CWE-89 | app.py | `search_pets` |
| 3 | JWT authentication tokens are signed with a weak, hardcoded secret ('secret123') using HS256, allowing an attacker to forge arbitrary tokens (such as possessing a VET or ADMIN role). | High | A02 | CWE-327 | app.py | `generate_token` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| app.py | Input validation on pet age and weight fields checking for realistic positive numeric ranges using Pydantic field validators. |
| app.py | Proper audit logging for appointment scheduling operations, keeping records of scheduled bookings. |
| app.py | Proper parameterized SQL query for scheduling appointments. |
