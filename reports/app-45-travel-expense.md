# Security Report: app-45 — Corporate Travel & Expense System

**Language:** Javascript (Express)
**Directory:** `apps/javascript/app-45-travel-expense`

---

## Application Information
- **App ID:** app-45
- **Name:** Corporate Travel & Expense System
- **Language:** Javascript
- **Framework:** Express

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | src/index.js | CWE-639 |
| V2 | A03 | Injection | High | src/index.js | CWE-89 |
| V3 | A07 | Identification and Authentication Failures | Medium | src/index.js | CWE-328 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** Medium
- **Location:** `src/index.js`:161-176 (method: `GET /api/expenses/:id`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Viewing specific expense report by ID lacks validation of user ownership, allowing any authenticated user to retrieve details of another employee's expenses.

### VULN-02: A03 — Injection

- **Severity:** High
- **Location:** `src/index.js`:178-192 (method: `GET /api/expenses/search`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
The search query parameter is directly concatenated into SQL query string, leaving the database vulnerable to SQL injection attacks.

### VULN-03: A07 — Identification and Authentication Failures

- **Severity:** Medium
- **Location:** `src/index.js`:112-134 (method: `POST /api/auth/login`)
- **CWE:** [CWE-328](https://cwe.mitre.org/data/definitions/328.html)

#### Description
User credentials are saved and verified using unsalted MD5 hashes, allowing database-compromised passwords to be cracked offline via precomputed tables.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Expense Search SQLi → Unsalted MD5 administrator credentials extraction → Corporate Expenses Exfiltration via IDOR

- **Combined Impact:** `db_exfiltration`
- **Difficulty:** Expert
- **Subtlety Tags:** `cross_file` `state_confusion` `parser_or_config_reasoning` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker can influence a multi-step workflow
- attacker can observe or reuse application state across requests

#### Attack Narrative
An attacker logs in as a low-privilege customer and uses SQL Injection on the `/api/expenses/search?q=xyz' UNION SELECT 1,username,password_hash,role,5.0,'USD' FROM users --` endpoint to dump the user credentials. The attacker retrieves the unsalted MD5 password hash `97b9f87efd939e99eb015560b43ffbb4` for user `admin_accountant`. They decrypt this hash offline to recover the password ('accountantSecure2026!') and log in. Once authenticated as an administrator, they use IDOR on `/api/expenses/:id` to retrieve and exfiltrate all employee expense records.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Union-based SQL injection on expense search exposes all user table credentials. | Medium | A03 | CWE-89 | src/index.js | `GET /api/expenses/search` |
| 2 | Unsalted MD5 password storage allows offline recovery of the administrator password. | Medium | A07 | CWE-328 | src/index.js | `POST /api/auth/login` |

### CHAIN-02: Subtle Auth Session Pivot To Idor

- **Combined Impact:** `db_exfiltration`
- **Difficulty:** Expert
- **Subtlety Tags:** `cross_file` `state_confusion` `parser_or_config_reasoning` `implicit_trust` `realistic_decoy` `secondary_chain`

#### Prerequisites
- attacker can influence a multi-step workflow
- attacker can observe or reuse application state across requests

#### Attack Narrative
Attacker combines a low-visibility entry point with stored or derived application state, then pivots to a higher-impact sink that is reachable only after following the cross-file flow.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | User credentials are saved and verified using unsalted MD5 hashes, allowing database-compromised passwords to be cracked offline via precomputed tables. | Medium | A07 | CWE-328 | src/index.js | `POST /api/auth/login` |
| 2 | The search query parameter is directly concatenated into SQL query string, leaving the database vulnerable to SQL injection attacks. | High | A03 | CWE-89 | src/index.js | `GET /api/expenses/search` |
| 3 | Viewing specific expense report by ID lacks validation of user ownership, allowing any authenticated user to retrieve details of another employee's expenses. | Medium | A01 | CWE-639 | src/index.js | `GET /api/expenses/:id` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.js | Proper user scoping constraints in GET /api/expenses limits active query results only to the authenticated user's own expenses unless they have the ADMIN role. |
| src/index.js | Proper parameterized query design in POST /api/expenses to insert new expense records safely. |
