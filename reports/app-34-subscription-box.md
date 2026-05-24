# Security Report: app-34-subscription-box

## Application Information

- **App ID**: app-34
- **App Name**: Subscription Box Service
- **Language**: TypeScript
- **Framework**: Express
- **Source**: `apps/typescript/app-34-subscription-box/`

---

## Vulnerability Summary

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | `src/index.ts` → `GET /api/subscriptions/:id` (lines 156-168) | CWE-639 |
| V2 | A03 | Injection | High | `src/index.ts` → `POST /api/subscriptions` (lines 171-186) | CWE-89 |
| V3 | A09 | Security Logging and Monitoring Failures | Low | `src/index.ts` → `POST /api/admin/subscriptions/:id/cancel` (lines 189-205) | CWE-778 |

### V1: IDOR on Subscription Details

**OWASP Category**: A01 — Broken Access Control

**Description**: Viewing subscription details by ID lacks verification of user ownership, allowing any authenticated user to retrieve another customer's subscription information.

**Endpoint**: `GET /api/subscriptions/:id`

**CWE**: CWE-639 (Authorization Bypass Through User-Controlled Key)

**Impact**: Medium — Any authenticated user can enumerate subscription IDs to view sensitive billing details, shipping addresses, and box preferences.

**Detection**: Look for absence of ownership checks where the `:id` parameter is used without verifying `req.user.id` against the subscription's customer ID.

---

### V2: SQL Injection on Subscription Creation

**OWASP Category**: A03 — Injection

**Description**: The subscription creation endpoint concatenates user input directly into a raw SQL query, enabling SQL injection.

**Endpoint**: `POST /api/subscriptions`

**CWE**: CWE-89 (SQL Injection)

**Impact**: High — An attacker can inject SQL via the `plan` or `address` parameters during subscription creation, extracting arbitrary data from the database.

**Detection**: Search for raw string concatenation with user-supplied parameters inside `db.run()` or `db.all()` calls in the subscription creation handler.

---

### V3: Missing Audit Log on Subscription Cancellation

**OWASP Category**: A09 — Security Logging and Monitoring Failures

**Description**: Cancelling active subscriptions at the admin level produces no audit logs, leaving state modifications untracked.

**Endpoint**: `POST /api/admin/subscriptions/:id/cancel`

**CWE**: CWE-778 (Insufficient Logging)

**Impact**: Low — Malicious or accidental cancellation of customer subscriptions cannot be traced or investigated.

**Detection**: Check the cancel handler for any logging, audit trail, or notification mechanism before/after performing the cancellation operation.

---

## Chained Attack Scenario

### Chain: "Subscription SQLi → IDOR Subscription Exfiltration"

**Impact**: `db_exfiltration`

**Overview**: An attacker exploits SQL injection during subscription creation to dump the database, then uses IDOR to exfiltrate other customers' subscription details.

**Components**:

| Step | Issue | Severity | OWASP | CWE | Location |
|---|---|---|---|---|---|
| 1 | SQL injection during subscription creation exposes the database | Medium | A03 | CWE-89 | `POST /api/subscriptions` |
| 2 | Subscription detail endpoint permits IDOR exfiltration of customer data | Medium | A01 | CWE-639 | `GET /api/subscriptions/:id` |

**Attack Narrative**:
1. The attacker sends a subscription creation request with a crafted `plan` parameter: `Premium' UNION SELECT 1,username,password_hash,address,card_last4 FROM users --`.
2. The query returns user credentials and payment card details in the response, which the attacker captures.
3. Using the obtained credentials, the attacker logs in and calls `GET /api/subscriptions/3` through IDOR to enumerate other customers' subscription data including addresses and preferences.

**Combined Impact**: Database exfiltration — An attacker can dump user credentials and exfiltrate other customers' subscription data by chaining SQL injection with IDOR.

---

## Decoys (False-Positive Candidates)

| Location | Description |
|---|---|
| `src/index.ts` | Proper parameterized query logic in `GET /api/boxes` to list available boxes safely |
| `src/index.ts` | Proper Bcrypt hashing for password storage and validation |

---

## Detection Commands

```bash
# Find SQL injection on subscription creation
grep -n "INSERT.*\+.*req\|db\.run.*req" apps/typescript/app-34-subscription-box/src/index.ts

# Find IDOR on subscription details
grep -n "subscriptions.*:id\|findOne\|findById" apps/typescript/app-34-subscription-box/src/index.ts

# Find missing audit logs on cancellation
grep -n "cancel\|subscription\|log\|audit" apps/typescript/app-34-subscription-box/src/index.ts
```

---

*Report generated from `.vulns` manifest for app-34-subscription-box*