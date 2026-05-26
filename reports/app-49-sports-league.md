# Security Report: app-49 — Sports League Management

**Language:** Python (Flask)
**Directory:** `apps/python/app-49-sports-league`

---

## Application Information
- **App ID:** app-49
- **Name:** Sports League Management
- **Language:** Python
- **Framework:** Flask

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | app.py | CWE-639 |
| V2 | A03 | Injection | High | app.py | CWE-89 |
| V3 | A05 | Security Misconfiguration | Low | app.py | CWE-200 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** Medium
- **Location:** `app.py`:173-187 (method: `get_player`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
The player profile details endpoint does not verify user roles or ownership, exposing sensitive salary and contract data to any authenticated user.

### VULN-02: A03 — Injection

- **Severity:** High
- **Location:** `app.py`:153-171 (method: `search_players`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
The player search endpoint directly concatenates user input into raw SQL query statements, permitting SQL injection.

### VULN-03: A05 — Security Misconfiguration

- **Severity:** Low
- **Location:** `app.py`:121-136 (method: `export_standings`)
- **CWE:** [CWE-200](https://cwe.mitre.org/data/definitions/200.html)

#### Description
The standings export endpoint exposes internal database schema structure and raw executed SQL query commands in response headers.


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: SQLi Player Dump → IDOR Contract Access → Score Manipulation

- **Combined Impact:** `data_modification`
- **Difficulty:** Expert
- **Subtlety Tags:** `cross_file` `state_confusion` `parser_or_config_reasoning` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker can influence a multi-step workflow
- attacker can observe or reuse application state across requests

#### Attack Narrative
An attacker uses SQL injection on the search endpoint to discover internal player IDs and team managers. They then exploit the IDOR vulnerability on the player profile endpoint to extract contract data. Finally, exploiting the missing authorization on the game score endpoint, they update game results to manipulate overall league standings.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | SQL injection in player search leaks database table schema details and record IDs. | Medium | A03 | CWE-89 | app.py | `search_players` |
| 2 | IDOR on player detail leaks sensitive contract/salary information. | Low | A01 | CWE-639 | app.py | `get_player` |
| 3 | Missing function-level access control on the game score update endpoint allows any authenticated user to change scores. | Medium | A01 | CWE-285 | app.py | `update_score` |

### CHAIN-02: Subtle Injection Pivot To Idor

- **Combined Impact:** `data_modification`
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
| 1 | The standings export endpoint exposes internal database schema structure and raw executed SQL query commands in response headers. | Low | A05 | CWE-200 | app.py | `export_standings` |
| 2 | The player search endpoint directly concatenates user input into raw SQL query statements, permitting SQL injection. | High | A03 | CWE-89 | app.py | `search_players` |
| 3 | The player profile details endpoint does not verify user roles or ownership, exposing sensitive salary and contract data to any authenticated user. | Medium | A01 | CWE-639 | app.py | `get_player` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| app.py | Proper role-based authorization check on team creation endpoint (/api/teams) restricting access to users with COMMISSIONER role. |
| app.py | Proper parameterized SQL queries for retrieving standings by team name. |
