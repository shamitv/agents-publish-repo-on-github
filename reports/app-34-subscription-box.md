# Security Report: app-34 — Subscription Box Service

**Language:** Typescript (Express)
**Directory:** `apps/typescript/app-34-subscription-box`

---

## Application Information
- **App ID:** app-34
- **Name:** Subscription Box Service
- **Language:** Typescript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A03 | Injection | High | src/index.ts | CWE-89 |
| V2 | A07 | Identification and Authentication Failures | Medium | src/index.ts | CWE-328 |
| V3 | A09 | Security Logging and Monitoring Failures | Low | src/index.ts | CWE-778 |

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection

- **Severity:** High
- **Location:** `src/index.ts`:173-185 (method: `GET /api/packages/search`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
The search query parameter is directly concatenated into a raw SQL query statement, leading to SQL injection.

### VULN-02: A07 — Identification and Authentication Failures

- **Severity:** Medium
- **Location:** `src/index.ts`:136-159 (method: `POST /api/auth/login`)
- **CWE:** [CWE-328](https://cwe.mitre.org/data/definitions/328.html)

#### Description
User account passwords are encrypted using unsalted MD5 hashing and saved in the database, allowing brute-force or rainbow table cracking.

### VULN-03: A09 — Security Logging and Monitoring Failures

- **Severity:** Low
- **Location:** `src/index.ts`:199-231 (method: `POST /api/subscriptions/update`)
- **CWE:** [CWE-778](https://cwe.mitre.org/data/definitions/778.html)

#### Description
Critical security events such as subscription modifications or payment level updates are not logged, disabling security event visibility.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Package Search SQLi → Unsalted MD5 Credential Cracking

- **Combined Impact:** `account_takeover`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
An attacker uses a SQL union injection query on `/api/packages/search?q=coffee' UNION SELECT 1,username,password_hash,role FROM users --` to dump the users table. They retrieve the unsalted MD5 hash `a57e4e138a08d3744952bd0176cd1f91` for the admin_agent user. By performing offline MD5 decryption/lookup, they crack the admin password ('adminpass2026') and take over the admin session.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Union-based SQL injection on package search exposes internal database tables. | Medium | A03 | CWE-89 | src/index.ts | `GET /api/packages/search` |
| 2 | Admin passwords stored as unsalted MD5 hashes are cracked offline, enabling account takeover. | Medium | A07 | CWE-328 | src/index.ts | `POST /api/auth/login` |

### CHAIN-02: Subtle State Confusion Pivot To Injection

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
| 1 | Critical security events such as subscription modifications or payment level updates are not logged, disabling security event visibility. | Low | A09 | CWE-778 | src/index.ts | `POST /api/subscriptions/update` |
| 2 | User account passwords are encrypted using unsalted MD5 hashing and saved in the database, allowing brute-force or rainbow table cracking. | Medium | A07 | CWE-328 | src/index.ts | `POST /api/auth/login` |
| 3 | The search query parameter is directly concatenated into a raw SQL query statement, leading to SQL injection. | High | A03 | CWE-89 | src/index.ts | `GET /api/packages/search` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.ts | Proper parameterized query logic in GET /api/packages/:id to retrieve single packages safely. |
| src/index.ts | Proper security auditing logs printed during user profile updates in POST /api/user/profile. |
| src/index.ts | Proper session token security with cryptographically secure generation using crypto.randomBytes. |
