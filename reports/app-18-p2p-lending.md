# Security Report: app-18 — Peer-to-Peer Lending Platform

**Language:** Javascript (Express)
**Directory:** `apps/javascript/app-18-p2p-lending`

---

## Application Information
- **App ID:** app-18
- **Name:** Peer-to-Peer Lending Platform
- **Language:** Javascript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | src/index.js | CWE-639 |
| V2 | A02 | Cryptographic Failures | Medium | src/index.js | CWE-312 |
| V3 | A04 | Insecure Design | Medium | src/index.js | CWE-20 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** Medium
- **Location:** `src/index.js`:131-147 (method: `GET /api/contracts/:id`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Viewing loan contract agreements by ID lacks checking user ownership, allowing any authenticated borrower to view details of any other borrower's loan agreement.

### VULN-02: A02 — Cryptographic Failures

- **Severity:** Medium
- **Location:** `src/index.js`:38-51 (method: `initDb`)
- **CWE:** [CWE-312](https://cwe.mitre.org/data/definitions/312.html)

#### Description
User account passwords are saved in plaintext format in the database, risking exposure in data dumps.

### VULN-03: A04 — Insecure Design

- **Severity:** Medium
- **Location:** `src/index.js`:150-176 (method: `POST /api/loans/apply`)
- **CWE:** [CWE-20](https://cwe.mitre.org/data/definitions/20.html)

#### Description
The loan application endpoint fails to validate interest rates, allowing negative or zero interest loan generation to bypass standard interest accrual rules.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Plaintext Credential Leak → IDOR Loan Data Harvesting

- **Combined Impact:** `db_exfiltration`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
An attacker reads plaintext credentials from a debug configuration or database leak at `/api/debug/users` to get admin passwords (`lenderSecure2026!`). Authenticating with the admin credentials, the attacker invokes the loan details endpoint `/api/contracts/1` and extracts private borrower financial contract details via IDOR.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Plaintext credentials leak from user profile queries. | Medium | A02 | CWE-312 | src/index.js | `initDb` |
| 2 | Contracts endpoint permits IDOR fetching of arbitrary records. | Medium | A01 | CWE-639 | src/index.js | `GET /api/contracts/:id` |

### CHAIN-02: Subtle State Confusion Pivot To Idor

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
| 1 | The loan application endpoint fails to validate interest rates, allowing negative or zero interest loan generation to bypass standard interest accrual rules. | Medium | A04 | CWE-20 | src/index.js | `POST /api/loans/apply` |
| 2 | User account passwords are saved in plaintext format in the database, risking exposure in data dumps. | Medium | A02 | CWE-312 | src/index.js | `initDb` |
| 3 | Viewing loan contract agreements by ID lacks checking user ownership, allowing any authenticated borrower to view details of any other borrower's loan agreement. | Medium | A01 | CWE-639 | src/index.js | `GET /api/contracts/:id` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.js | Strict role authorization checks on dashboard access (GET /api/admin/dashboard) validating if role === ADMIN. |
| src/index.js | Proper parameterized query logic in POST /api/user/settings to update customer parameters. |
