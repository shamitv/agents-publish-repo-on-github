# Security Report: app-45-travel-expense

## Application Information

- **App ID**: app-45
- **App Name**: Travel & Expense Management
- **Language**: JavaScript
- **Framework**: Express
- **Source**: `apps/javascript/app-45-travel-expense/`

---

## Vulnerability Summary

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | `src/index.js` → `GET /api/expenses/:id` (lines 156-170) | CWE-639 |
| V2 | A09 | Security Logging and Monitoring Failures | Low | `src/index.js` → `POST /api/admin/approvals/force-approve` (lines 192-206) | CWE-778 |
| V3 | A10 | Server-Side Request Forgery (SSRF) | High | `src/index.js` → `GET /api/receipts/process` (lines 173-189) | CWE-918 |

### V1: IDOR on Expense Details

**OWASP Category**: A01 — Broken Access Control

**Description**: Viewing expense records by ID lacks verification of user ownership, allowing any authenticated employee to retrieve details of another employee's expense reports.

**Endpoint**: `GET /api/expenses/:id`

**CWE**: CWE-639 (Authorization Bypass Through User-Controlled Key)

**Impact**: Medium — Any authenticated employee can enumerate expense IDs to view sensitive financial data, receipt images, and approval history of other employees.

**Detection**: Look for absence of ownership checks where the `:id` parameter is used without verifying `req.user.userId` against the expense record's employee ID.

---

### V2: Missing Audit Log on Force Approval

**OWASP Category**: A09 — Security Logging and Monitoring Failures

**Description**: Forced approval of expense reports can be triggered without security logging or audit trail, leaving admin privilege escalation unrecorded.

**Endpoint**: `POST /api/admin/approvals/force-approve`

**CWE**: CWE-778 (Insufficient Logging)

**Impact**: Low — Unauthorized or malicious approval of expense reports cannot be traced to the responsible administrator.

**Detection**: Check the force approval handler for any logging, audit trail, or notification mechanism before/after performing the approval operation.

---

### V3: SSRF via Receipt Processing

**OWASP Category**: A10 — Server-Side Request Forgery (SSRF)

**Description**: The receipt processing proxy makes HTTP calls using axios on user-supplied URL inputs with no address block restriction, enabling SSRF.

**Endpoint**: `GET /api/receipts/process`

**CWE**: CWE-918 (Server-Side Request Forgery)

**Impact**: High — An attacker can make the server send crafted HTTP requests to internal network services, bypassing firewalls and accessing internal APIs or cloud metadata endpoints.

**Detection**: Look for an endpoint that accepts a user-controlled URL parameter and passes it directly to `axios.get()` or `fetch()` without any allowlist, denylist, or hostname validation.

---

## Chained Attack Scenario

### Chain: "IDOR Expense Mining → SSRF Internal Receipt Processing Pivot"

**Impact**: `lateral_movement`

**Overview**: An attacker uses IDOR to mine sensitive expense data from colleagues, then leverages SSRF to pivot to internal receipt processing services.

**Components**:

| Step | Issue | Severity | OWASP | CWE | Location |
|---|---|---|---|---|---|
| 1 | Expenses endpoint permits IDOR details mining of other employees | Medium | A01 | CWE-639 | `GET /api/expenses/:id` |
| 2 | Receipt processing proxy makes external requests with no IP filtering | Medium | A10 | CWE-918 | `GET /api/receipts/process` |

**Attack Narrative**:
1. The attacker logs in and calls `GET /api/expenses/1` through IDOR to mine sensitive expense records and receipt metadata from other employees.
2. The attacker then uses the receipt processing proxy at `GET /api/receipts/process` with a crafted URL targeting `http://localhost:8085/internal/receipts/admin`, bypassing network segmentation to access internal receipt processing services.
3. By combining IDOR data mining with SSRF pivoting, the attacker exfiltrates the complete expense database.

**Combined Impact**: Lateral movement — An attacker can pivot from a public expense lookup endpoint to access internal receipt processing services by chaining IDOR with SSRF.

---

## Decoys (False-Positive Candidates)

| Location | Description |
|---|---|
| `src/index.js` | Proper user scoping constraints in `GET /api/expenses` limiting output to own records only |
| `src/index.js` | Proper parameterized query logic in `POST /api/expenses/submit` to record new expenses safely |

---

## Detection Commands

```bash
# Find IDOR on expense details
grep -n "expenses.*:id\|findOne\|findById" apps/javascript/app-45-travel-expense/src/index.js

# Find missing audit logs on force approval
grep -n "force-approve\|approv\|log\|audit" apps/javascript/app-45-travel-expense/src/index.js

# Find SSRF vulnerable receipt processing
grep -n "axios\.get\|axios\.post\|fetch\|receiptUrl" apps/javascript/app-45-travel-expense/src/index.js
```

---

*Report generated from `.vulns` manifest for app-45-travel-expense*