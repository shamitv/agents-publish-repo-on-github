# Security Report: app-38 — Museum Collection Catalog

**Language:** Javascript (Express)
**Directory:** `apps/javascript/app-38-museum-catalog`

---

## Application Information
- **App ID:** app-38
- **Name:** Museum Collection Catalog
- **Language:** Javascript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | src/index.js | CWE-639 |
| V2 | A03 | Injection | High | src/index.js | CWE-79 |
| V3 | A09 | Security Logging and Monitoring Failures | Low | src/index.js | CWE-778 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** Medium
- **Location:** `src/index.js`:136-152 (method: `GET /api/exhibits/:id`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
The exhibit detail retrieval endpoint fails to verify if the requesting user owns the exhibit or possesses curator/admin permissions, allowing authenticated users to access confidential notes.

### VULN-02: A03 — Injection

- **Severity:** High
- **Location:** `src/index.js`:155-165 (method: `GET /api/guestbook`)
- **CWE:** [CWE-79](https://cwe.mitre.org/data/definitions/79.html)

#### Description
Visitor guestbook comments are rendered to the client without HTML entity encoding, leaving visitors vulnerable to Stored XSS.

### VULN-03: A09 — Security Logging and Monitoring Failures

- **Severity:** Low
- **Location:** `src/index.js`:184-200 (method: `POST /api/exhibits/:id/delete`)
- **CWE:** [CWE-778](https://cwe.mitre.org/data/definitions/778.html)

#### Description
Deleting sensitive museum artifacts from the catalog produces no audit log tracking outputs, blinding administrators to record destruction.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Stored Guestbook XSS → Session Hijack IDOR Exfiltration

- **Combined Impact:** `db_exfiltration`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
An attacker posts an XSS cookie stealer payload to `/api/guestbook`. When the curator admin reviews the guestbook, their session cookie is leaked to the attacker. Using the hijacked admin cookie, the attacker bypasses access controls and queries `/api/exhibits/2` (IDOR) to exfiltrate private, high-value catalog notes.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Stored guestbook XSS script allows cookie theft. | Medium | A03 | CWE-79 | src/index.js | `GET /api/guestbook` |
| 2 | Details endpoint permits IDOR exfiltration of sensitive records. | Medium | A01 | CWE-639 | src/index.js | `GET /api/exhibits/:id` |

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
| 1 | Deleting sensitive museum artifacts from the catalog produces no audit log tracking outputs, blinding administrators to record destruction. | Low | A09 | CWE-778 | src/index.js | `POST /api/exhibits/:id/delete` |
| 2 | Visitor guestbook comments are rendered to the client without HTML entity encoding, leaving visitors vulnerable to Stored XSS. | High | A03 | CWE-79 | src/index.js | `GET /api/guestbook` |
| 3 | The exhibit detail retrieval endpoint fails to verify if the requesting user owns the exhibit or possesses curator/admin permissions, allowing authenticated users to access confidential notes. | Medium | A01 | CWE-639 | src/index.js | `GET /api/exhibits/:id` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.js | Proper escaping of HTML tags on exhibit titles during list lookups in GET /api/exhibits. |
| src/index.js | Proper Bcrypt hashing for password storage and validation. |
