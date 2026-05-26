# Security Report: app-16 — Restaurant Review Platform

**Language:** Javascript (Express)
**Directory:** `apps/javascript/app-16-restaurant-reviews`

---

## Application Information
- **App ID:** app-16
- **Name:** Restaurant Review Platform
- **Language:** Javascript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | src/index.js | CWE-639 |
| V2 | A03 | Injection | High | src/index.js | CWE-89 |
| V3 | A07 | Identification and Authentication Failures | Medium | src/index.js | CWE-330 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** Medium
- **Location:** `src/index.js`:153-176 (method: `POST /api/reviews/:id/edit`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
The review editing endpoint does not verify whether the authenticated user is the owner of the review or has admin privileges, allowing arbitrary review modification.

### VULN-02: A03 — Injection

- **Severity:** High
- **Location:** `src/index.js`:129-141 (method: `GET /api/restaurants/search`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
User input in search parameter is concatenated directly into SQL query statement, exposing the database to SQL injection.

### VULN-03: A07 — Identification and Authentication Failures

- **Severity:** Medium
- **Location:** `src/index.js`:96-112 (method: `POST /api/auth/login`)
- **CWE:** [CWE-330](https://cwe.mitre.org/data/definitions/330.html)

#### Description
Session keys are generated using non-cryptographic Math.random() function, making session IDs predictable and prone to hijacking.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Predictable Session Hijacking → IDOR Review Sabotage

- **Combined Impact:** `data_modification`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
An attacker predicts the session cookie values of an active customer or food critic generated via Math.random(). They hijack the target critic's session, call `/api/reviews/1/edit` to hijack or modify high-rating review comments to sabotage the restaurant status, achieving unauthorized data modification.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Weak session token generation via predictable random number generator. | Medium | A07 | CWE-330 | src/index.js | `POST /api/auth/login` |
| 2 | Review editing allows users authenticated with hijacked session to overwrite reviews without owner check. | Medium | A01 | CWE-639 | src/index.js | `POST /api/reviews/:id/edit` |

### CHAIN-02: Subtle Auth Session Pivot To Idor

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
| 1 | Session keys are generated using non-cryptographic Math.random() function, making session IDs predictable and prone to hijacking. | Medium | A07 | CWE-330 | src/index.js | `POST /api/auth/login` |
| 2 | User input in search parameter is concatenated directly into SQL query statement, exposing the database to SQL injection. | High | A03 | CWE-89 | src/index.js | `GET /api/restaurants/search` |
| 3 | The review editing endpoint does not verify whether the authenticated user is the owner of the review or has admin privileges, allowing arbitrary review modification. | Medium | A01 | CWE-639 | src/index.js | `POST /api/reviews/:id/edit` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.js | Proper Bcrypt hashing for password storage and credentials validation during login. |
| src/index.js | Proper role restriction on GET /api/admin/dashboard ensuring only ADMIN can access. |
| src/index.js | Proper parameterized query for individual restaurant profiles in GET /api/restaurants/:id. |
