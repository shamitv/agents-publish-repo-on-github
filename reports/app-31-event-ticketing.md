# Security Report: app-31-event-ticketing

## Application Information

- **App ID**: app-31
- **App Name**: Event Ticketing System
- **Language**: TypeScript
- **Framework**: Express
- **Source**: `apps/typescript/app-31-event-ticketing/`

---

## Vulnerability Summary

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | `src/index.ts` → `GET /api/events/:id/tickets` (lines 164-178) | CWE-639 |
| V2 | A03 | Injection | High | `src/index.ts` → `GET /api/events/search` (lines 148-161) | CWE-89 |
| V3 | A09 | Security Logging and Monitoring Failures | Low | `src/index.ts` → `POST /api/admin/events/:id/delete` (lines 181-198) | CWE-778 |

### V1: IDOR on Event Ticket Lists

**OWASP Category**: A01 — Broken Access Control

**Description**: Viewing ticket details by event ID lacks verification of user ownership, allowing any authenticated user to retrieve other attendees' ticket information.

**Endpoint**: `GET /api/events/:id/tickets`

**CWE**: CWE-639 (Authorization Bypass Through User-Controlled Key)

**Impact**: Medium — Any authenticated user can enumerate event IDs to view ticket codes, buyer names, and purchase details belonging to other attendees.

**Detection**: Look for absence of ownership checks where the `:id` parameter is used to query tickets without verifying the requesting user's relation to the event or ticket.

---

### V2: SQL Injection on Event Search

**OWASP Category**: A03 — Injection

**Description**: The event search parameter is directly concatenated into a raw SQL query, enabling SQL injection.

**Endpoint**: `GET /api/events/search`

**CWE**: CWE-89 (SQL Injection)

**Impact**: High — An attacker can extract arbitrary data from the database including user credentials, ticket records, and event details via UNION-based SQL injection.

**Detection**: Search for raw string concatenation with user-supplied `q` parameter inside `db.all()` or `db.query()` calls in the event search handler.

---

### V3: Missing Audit Log on Event Deletion

**OWASP Category**: A09 — Security Logging and Monitoring Failures

**Description**: Deleting events from the system produces no audit logs, leaving record destruction untracked.

**Endpoint**: `POST /api/admin/events/:id/delete`

**CWE**: CWE-778 (Insufficient Logging)

**Impact**: Low — Malicious or accidental deletion of event records cannot be traced or investigated.

**Detection**: Check the delete handler for any logging, audit trail, or notification mechanism before/after performing the deletion operation.

---

## Chained Attack Scenario

### Chain: "Event Search SQLi → IDOR Ticket Exfiltration"

**Impact**: `db_exfiltration`

**Overview**: An attacker uses SQL injection on event search to dump the database, then uses IDOR to exfiltrate attendee ticket data.

**Components**:

| Step | Issue | Severity | OWASP | CWE | Location |
|---|---|---|---|---|---|
| 1 | SQL injection on event search exposes the database | Medium | A03 | CWE-89 | `GET /api/events/search` |
| 2 | Ticket endpoint lacks authorization checks for ticket ownership | Medium | A01 | CWE-639 | `GET /api/events/:id/tickets` |

**Attack Narrative**:
1. The attacker sends `GET /api/events/search?q=concert' UNION SELECT 1,username,password_hash,role FROM users --` to dump user credentials from the database.
2. Using the admin credentials obtained, the attacker logs in and calls `GET /api/events/3/tickets` to enumerate ticket records for any event via IDOR.
3. The attacker exfiltrates all attendee ticket data including names and purchase details.

**Combined Impact**: Database exfiltration — An attacker can dump user credentials and exfiltrate attendee ticket data by chaining SQL injection with IDOR.

---

## Decoys (False-Positive Candidates)

| Location | Description |
|---|---|
| `src/index.ts` | Proper parameterized query logic in `POST /api/events/create` to create events safely |
| `src/index.ts` | Proper Bcrypt hashing for password storage and validation |

---

## Detection Commands

```bash
# Find SQL injection on event search
grep -n "SELECT.*\+.*req\.query\|db\.all.*req" apps/typescript/app-31-event-ticketing/src/index.ts

# Find IDOR on ticket lists
grep -n "tickets\|findByEvent\|event_id" apps/typescript/app-31-event-ticketing/src/index.ts

# Find missing audit logs on deletion
grep -n "delete\|remove\|log\|audit" apps/typescript/app-31-event-ticketing/src/index.ts
```

---

*Report generated from `.vulns` manifest for app-31-event-ticketing*