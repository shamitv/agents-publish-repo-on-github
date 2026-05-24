# Security Report: app-35-compliance-tracker

## Application Information

- **App ID**: app-35
- **App Name**: Compliance Document Tracker
- **Language**: TypeScript
- **Framework**: Express
- **Source**: `apps/typescript/app-35-compliance-tracker/`

---

## Vulnerability Summary

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | `src/index.ts` → `GET /api/documents/:id` (lines 160-175) | CWE-639 |
| V2 | A02 | Cryptographic Failures | High | `src/index.ts` → `GET /api/admin/documents/export` (lines 144-157) | CWE-312 |
| V3 | A07 | Identification and Authentication Failures | Medium | `src/index.ts` → `POST /api/auth/login` (lines 103-138) | CWE-328 |

### V1: IDOR on Compliance Documents

**OWASP Category**: A01 — Broken Access Control

**Description**: Viewing compliance document details by ID lacks verification of user ownership, allowing any authenticated user to retrieve another organization's sensitive compliance documents.

**Endpoint**: `GET /api/documents/:id`

**CWE**: CWE-639 (Authorization Bypass Through User-Controlled Key)

**Impact**: Medium — Any authenticated user can enumerate document IDs to view audit reports, regulatory filings, and confidential compliance data from other organizations.

**Detection**: Look for absence of ownership checks where the `:id` parameter is used without verifying `req.user.orgId` against the document's organization ID.

---

### V2: Plaintext Compliance Data Export

**OWASP Category**: A02 — Cryptographic Failures

**Description**: An administrative document export endpoint returns all compliance documents including sensitive regulatory data in plaintext format with no encryption or access scoping.

**Endpoint**: `GET /api/admin/documents/export`

**CWE**: CWE-312 (Cleartext Storage of Sensitive Information)

**Impact**: High — Any admin user can download the full compliance document database containing audit findings, financial records, and regulatory submissions in plaintext.

**Detection**: Look for an admin export endpoint that reads all rows from the database and returns them as-is without redaction, encryption, or aggregation.

---

### V3: Unsalted MD5 Password Hashing

**OWASP Category**: A07 — Identification and Authentication Failures

**Description**: User account passwords are hashed using unsalted MD5 and stored in the database, allowing brute-force or rainbow table cracking.

**Endpoint**: `POST /api/auth/login`

**CWE**: CWE-328 (Use of Weak Hash)

**Impact**: Medium — If the password database is compromised, an attacker can crack passwords offline using precomputed rainbow tables or brute-force techniques.

**Detection**: Search for `md5()` usage in password hashing/verification logic instead of bcrypt, scrypt, or argon2.

---

## Chained Attack Scenario

### Chain: "MD5 Password Cracking → IDOR Compliance Document Exfiltration"

**Impact**: `db_exfiltration`

**Overview**: An attacker cracks an admin's MD5-hashed password, logs into their account, and exfiltrates compliance documents from other organizations via IDOR.

**Components**:

| Step | Issue | Severity | OWASP | CWE | Location |
|---|---|---|---|---|---|
| 1 | Weak unsalted MD5 password hashing enables offline credential cracking | Medium | A07 | CWE-328 | `POST /api/auth/login` |
| 2 | Document endpoint lacks authorization checks for organization ownership | Medium | A01 | CWE-639 | `GET /api/documents/:id` |

**Attack Narrative**:
1. The attacker obtains the users table (e.g., through SQL injection on another endpoint), retrieves the unsalted MD5 hash for `compliance_admin`, and cracks the password offline.
2. Using the cracked credentials, the attacker logs in as `compliance_admin` and calls `GET /api/documents/5` through IDOR to access compliance documents from other organizations.
3. The attacker exfiltrates sensitive audit reports and regulatory filings across the platform.

**Combined Impact**: Database exfiltration — An attacker can steal sensitive compliance documents by cracking weak passwords and exploiting missing access controls.

---

## Decoys (False-Positive Candidates)

| Location | Description |
|---|---|
| `src/index.ts` | Proper user scoping constraints in `GET /api/documents` limiting results to own organization only |
| `src/index.ts` | Proper parameterized query logic in `POST /api/documents/upload` to upload documents safely |

---

## Detection Commands

```bash
# Find IDOR on document details
grep -n "documents.*:id\|findOne\|findById" apps/typescript/app-35-compliance-tracker/src/index.ts

# Find plaintext data export
grep -n "export\|database\|admin" apps/typescript/app-35-compliance-tracker/src/index.ts

# Find weak password hashing
grep -n "md5\|hash\|password" apps/typescript/app-35-compliance-tracker/src/index.ts
```

---

*Report generated from `.vulns` manifest for app-35-compliance-tracker*