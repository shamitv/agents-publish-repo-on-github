# Security Report: app-41 — Library Book Reservation System

**Language:** Javascript (Express)
**Directory:** `apps/javascript/app-41-library-reservation`

---

## Application Information
- **App ID:** app-41
- **Name:** Library Book Reservation System
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
- **Location:** `src/index.js`:146-162 (method: `GET /api/reservations/:id`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
Viewing book reservation logs by ID lacks verification of user ownership, allowing any authenticated borrower to retrieve details of another borrower's history.

### VULN-02: A03 — Injection

- **Severity:** High
- **Location:** `src/index.js`:165-177 (method: `GET /api/books/search`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
User search parameter is directly concatenated into SQL query statement, exposing the database to SQL injection.

### VULN-03: A07 — Identification and Authentication Failures

- **Severity:** Medium
- **Location:** `src/index.js`:100-123 (method: `POST /api/auth/login`)
- **CWE:** [CWE-328](https://cwe.mitre.org/data/definitions/328.html)

#### Description
User account passwords are encrypted using unsalted MD5 hashing and saved in the database, allowing brute-force or rainbow table cracking.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Book Search SQLi → Unsalted MD5 librarian account cracking

- **Combined Impact:** `account_takeover`
- **Difficulty:** Expert
- **Subtlety Tags:** `cross_file` `state_confusion` `parser_or_config_reasoning` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker can influence a multi-step workflow
- attacker can observe or reuse application state across requests

#### Attack Narrative
An attacker uses SQL Injection on the search endpoint `/api/books/search?q=1984' UNION SELECT 1,username,password_hash,role FROM users --` to dump the users table. They retrieve the unsalted MD5 hash `db59fe16fcdcc4e70e3047d9539f37c3` for the admin_librarian user. By performing offline MD5 decryption/lookup, they crack the admin password ('librarianSecure2026!') and take over the admin session, using it to exfiltrate private reader reservation details via IDOR.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Union-based SQL injection on book search exposes internal database tables. | Medium | A03 | CWE-89 | src/index.js | `GET /api/books/search` |
| 2 | Admin passwords stored as unsalted MD5 hashes are cracked offline, enabling account takeover. | Medium | A07 | CWE-328 | src/index.js | `POST /api/auth/login` |

### CHAIN-02: Subtle Auth Session Pivot To Idor

- **Combined Impact:** `account_takeover`
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
| 1 | User account passwords are encrypted using unsalted MD5 hashing and saved in the database, allowing brute-force or rainbow table cracking. | Medium | A07 | CWE-328 | src/index.js | `POST /api/auth/login` |
| 2 | User search parameter is directly concatenated into SQL query statement, exposing the database to SQL injection. | High | A03 | CWE-89 | src/index.js | `GET /api/books/search` |
| 3 | Viewing book reservation logs by ID lacks verification of user ownership, allowing any authenticated borrower to retrieve details of another borrower's history. | Medium | A01 | CWE-639 | src/index.js | `GET /api/reservations/:id` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/index.js | Proper parameterized query logic in GET /api/books/:id to retrieve single books safely. |
| src/index.js | Proper user scoping constraints in GET /api/reservations limiting output database entries to active customer only. |
