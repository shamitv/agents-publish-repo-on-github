# Security Report: app-40 — Pet Adoption Portal

**Language:** Javascript (Express)
**Directory:** `apps/javascript/app-40-pet-adoption`

---

## Application Information
- **App ID:** app-40
- **Name:** Pet Adoption Portal
- **Language:** Javascript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A03 | Injection | High | src/index.js | CWE-89 |
| V2 | A05 | Security Misconfiguration | Medium | src/index.js | CWE-209 |
| V3 | A08 | Software and Data Integrity Failures | High | src/index.js | CWE-502 |

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection

- **Severity:** High
- **Location:** `src/index.js`:151-163 (method: `GET /api/pets/search`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
User search query input is directly concatenated into a raw SQL statement, leading to SQL injection.

### VULN-02: A05 — Security Misconfiguration

- **Severity:** Medium
- **Location:** `src/index.js`:184-198 (method: `GET /api/system/diagnostics`)
- **CWE:** [CWE-209](https://cwe.mitre.org/data/definitions/209.html)

#### Description
An open diagnostics route leaks server settings and a hardcoded administrative recovery API token when query parameters activate debug mode.

### VULN-03: A08 — Software and Data Integrity Failures

- **Severity:** High
- **Location:** `src/index.js`:166-181 (method: `POST /api/pets/layout`)
- **CWE:** [CWE-502](https://cwe.mitre.org/data/definitions/502.html)

#### Description
Layout configurations submitted by users are parsed using the insecure eval() constructor, enabling remote code execution on the server host.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Diagnostics Configuration Disclosure → Remote Code Execution via Insecure Deserialization

- **Combined Impact:** `account_takeover`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
An attacker invokes `/api/system/diagnostics?debug=true` to obtain the layout configuration token `PET-PORTAL-DEV-LAYOUT-KEY-2026`. Utilizing this token in the header `x-layout-token` to bypass authentication, they POST a layout configuration payload to `/api/pets/layout` containing a system command execution string evaluated via eval().

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | System diagnostics endpoint leaks layout customization token key. | Medium | A05 | CWE-209 | src/index.js | `GET /api/system/diagnostics` |
| 2 | Layout update route executes custom strings using eval() without checks. | Medium | A08 | CWE-502 | src/index.js | `POST /api/pets/layout` |

### CHAIN-02: Subtle Deserialization Pivot To Injection

- **Combined Impact:** `account_takeover`
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
| 1 | Layout configurations submitted by users are parsed using the insecure eval() constructor, enabling remote code execution on the server host. | High | A08 | CWE-502 | src/index.js | `POST /api/pets/layout` |
| 2 | An open diagnostics route leaks server settings and a hardcoded administrative recovery API token when query parameters activate debug mode. | Medium | A05 | CWE-209 | src/index.js | `GET /api/system/diagnostics` |
| 3 | User search query input is directly concatenated into a raw SQL statement, leading to SQL injection. | High | A03 | CWE-89 | src/index.js | `GET /api/pets/search` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.js | Proper parameterized query logic in POST /api/applications/apply to record application entries safely. |
| src/index.js | Proper Bcrypt hashing for password storage and validation. |
