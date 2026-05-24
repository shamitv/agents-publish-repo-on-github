# Security Report: app-44-election-polling

## Application Information

- **App ID**: app-44
- **App Name**: Election Polling System
- **Language**: JavaScript
- **Framework**: Express
- **Source**: `apps/javascript/app-44-election-polling/`

---

## Vulnerability Summary

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A02 | Cryptographic Failures | Medium | `src/index.js` → `GET /api/candidates` (lines 136-146) | CWE-312 |
| V2 | A04 | Insecure Design | Medium | `src/index.js` → `POST /api/vote/cast` (lines 149-178) | CWE-362 |
| V3 | A09 | Security Logging and Monitoring Failures | Low | `src/index.js` → `POST /api/admin/polls/close` (lines 181-190) | CWE-778 |

### V1: Plaintext Ballot Storage

**OWASP Category**: A02 — Cryptographic Failures

**Description**: Voter selections (ballots) are stored in plaintext format in the database and exposed directly to the public API, violating voter anonymity.

**Endpoint**: `GET /api/candidates`

**CWE**: CWE-312 (Cleartext Storage of Sensitive Information)

**Impact**: Medium — Anyone who accesses the candidates API response can read the raw `ballots` or `votes` array, linking individual voters to their selections.

**Detection**: Look for the candidates endpoint returning raw ballot data (e.g., `vote`, `ballot`, `selection` fields) without anonymization, aggregation, or encryption.

---

### V2: Race Condition on Vote Casting

**OWASP Category**: A04 — Insecure Design

**Description**: The vote casting logic uses asynchronous processing delays without database transactions or locks, enabling users to submit multiple votes concurrently.

**Endpoint**: `POST /api/vote/cast`

**CWE**: CWE-362 (Concurrent Execution Using Shared Resource with Improper Synchronization)

**Impact**: Medium — An attacker can send multiple rapid concurrent requests to the vote casting endpoint, casting more votes than their account allows (double-voting).

**Detection**: Look for asynchronous operations (e.g., `setTimeout`, `async/await` with no locking) between reading the current vote count and writing the updated count, with no database transaction or row lock.

---

### V3: Missing Audit Log on Poll Closure

**OWASP Category**: A09 — Security Logging and Monitoring Failures

**Description**: Critical administrative commands such as closing election polls are performed without security logs or audit trails, leaving system state modifications unrecorded.

**Endpoint**: `POST /api/admin/polls/close`

**CWE**: CWE-778 (Insufficient Logging)

**Impact**: Low — Malicious or premature closing of election polls cannot be traced to the responsible administrator.

**Detection**: Check the poll closure handler for any logging, audit trail, or notification mechanism before/after changing the poll state.

---

## Chained Attack Scenario

### Chain: "Predictable Voter Ballot Retrieval → Concurrent Vote Casting"

**Impact**: `data_modification`

**Overview**: An attacker reads all cast voter ballots in plaintext, then exploits a race condition to submit multiple unauthorized votes under other users' identities.

**Components**:

| Step | Issue | Severity | OWASP | CWE | Location |
|---|---|---|---|---|---|
| 1 | Exposing plaintext database ballots compromises voter selection details | Medium | A02 | CWE-312 | `GET /api/candidates` |
| 2 | Casting votes has an asynchronous timing window enabling race-based double-voting | Medium | A04 | CWE-362 | `POST /api/vote/cast` |

**Attack Narrative**:
1. The attacker queries `GET /api/candidates` to read all cast voter ballots in plaintext, identifying active voter accounts that have not yet voted.
2. The attacker sends concurrent, parallel HTTP requests to `POST /api/vote/cast` with those voters' credentials, exploiting the race condition to submit multiple unauthorized votes under those users' identities.
3. Because poll closure at `POST /api/admin/polls/close` generates no audit logs, the attacker can close the polls early without detection once their fraudulent votes are cast.

**Combined Impact**: Data modification — An attacker can submit fraudulent votes and prematurely close polls without detection.

---

## Decoys (False-Positive Candidates)

| Location | Description |
|---|---|
| `src/index.js` | Proper security auditing logs printed during candidate registration in `POST /api/admin/candidates` |
| `src/index.js` | Proper Bcrypt hashing for password storage and validation |

---

## Detection Commands

```bash
# Find plaintext ballot exposure
grep -n "ballot\|vote\|selection\|candidates" apps/javascript/app-44-election-polling/src/index.js

# Find race condition in vote casting
grep -n "setTimeout\|async\|await\|lock\|transaction" apps/javascript/app-44-election-polling/src/index.js

# Find missing audit logs on poll closure
grep -n "close\|poll\|log\|audit" apps/javascript/app-44-election-polling/src/index.js
```

---

*Report generated from `.vulns` manifest for app-44-election-polling*