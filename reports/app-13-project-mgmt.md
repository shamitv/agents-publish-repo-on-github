# Security Report: app-13 — Project Management Tool

**Language:** Typescript (Express)
**Directory:** `apps/typescript/app-13-project-mgmt`

---

## Application Information
- **App ID:** app-13
- **Name:** Project Management Tool
- **Language:** Typescript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | High | src/index.ts | CWE-284 |
| V2 | A03 | Injection | High | public/js/app.js | CWE-79 |
| V3 | A09 | Security Logging and Monitoring Failures | Medium | src/index.ts | CWE-778 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** High
- **Location:** `src/index.ts`:110-125 (method: `getBoardById`)
- **CWE:** [CWE-284](https://cwe.mitre.org/data/definitions/284.html)

#### Description
Broken Access Control. The endpoint fetches project boards directly by their numeric ID without verifying if the requested board belongs to the currently authenticated user's organization.

### VULN-02: A03 — Injection

- **Severity:** High
- **Location:** `public/js/app.js`:100-115 (method: `renderTasks`)
- **CWE:** [CWE-79](https://cwe.mitre.org/data/definitions/79.html)

#### Description
Cross-Site Scripting (XSS). Task descriptions are rendered into the DOM using innerHTML without HTML entity encoding, allowing execution of malicious Javascript payloads.

### VULN-03: A09 — Security Logging and Monitoring Failures

- **Severity:** Medium
- **Location:** `src/index.ts`:140-160 (method: `updateBoardPermissions`)
- **CWE:** [CWE-778](https://cwe.mitre.org/data/definitions/778.html)

#### Description
Security Logging and Monitoring Failures. The endpoint modifies sensitive project access permissions but fails to generate any audit logs or trace events.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Board IDOR → Stored XSS in Task Comments → Session Token Exfiltration

- **Combined Impact:** `account_takeover`
- **Difficulty:** Medium
- **Subtlety Tags:** `cross_file` `direct_data_flow` `realistic_decoy`

#### Prerequisites
- attacker can reach the public request path
- attacker can control one request parameter or body field

#### Attack Narrative
Attacker accesses a cross-org board via IDOR, posts a script payload as a task comment. When the victim org's manager views the board and the comment is rendered via innerHTML, the script exfiltrates their session_id cookie (readable because httpOnly is absent). Attacker hijacks the manager session.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | GET /api/boards/:id does not verify board.orgId matches the authenticated user's orgId, allowing cross-organization board and task access | Medium | A01 | CWE-639 | src/index.ts | `GET /api/boards/:id` |
| 2 | Task comments stored and returned without HTML sanitization; script tags in comment content execute as Stored XSS when rendered via innerHTML by the frontend | Medium | A03 | CWE-79 | src/index.ts | `POST /api/boards/:boardId/tasks/:taskId/comments` |
| 3 | Session cookie set without httpOnly flag; JavaScript can read document.cookie, enabling the XSS payload to exfiltrate the session token | Medium | A07 | CWE-1004 | src/index.ts | `POST /api/auth/login cookie` |

### CHAIN-02: Subtle State Confusion Pivot To Ssrf

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
| 1 | Security Logging and Monitoring Failures. The endpoint modifies sensitive project access permissions but fails to generate any audit logs or trace events. | Medium | A09 | CWE-778 | src/index.ts | `updateBoardPermissions` |
| 2 | Cross-Site Scripting (XSS). Task descriptions are rendered into the DOM using innerHTML without HTML entity encoding, allowing execution of malicious Javascript payloads. | High | A03 | CWE-79 | public/js/app.js | `renderTasks` |
| 3 | Broken Access Control. The endpoint fetches project boards directly by their numeric ID without verifying if the requested board belongs to the currently authenticated user's organization. | High | A01 | CWE-284 | src/index.ts | `getBoardById` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.ts | Secure standard JWT or secure session cookie authentication middleware. |
