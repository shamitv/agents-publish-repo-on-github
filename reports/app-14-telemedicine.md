# Security Report: app-14-telemedicine

## Application Information

- **App ID**: app-14
- **App Name**: Telemedicine Platform
- **Language**: TypeScript
- **Framework**: Express
- **Source**: `apps/typescript/app-14-telemedicine/`

---

## Vulnerability Summary

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | `src/index.ts` → `GET /api/medical-records/:id` (lines 168-185) | CWE-639 |
| V2 | A02 | Cryptographic Failures | High | `src/index.ts` → `GET /api/admin/database/export` (lines 144-153) | CWE-312 |
| V3 | A07 | Identification and Authentication Failures | Medium | `src/index.ts` → `POST /api/auth/login` (lines 104-137) | CWE-328 |

### V1: IDOR on Medical Records

**OWASP Category**: A01 — Broken Access Control

**Description**: Viewing patient medical records by ID lacks verification of user ownership, allowing any authenticated provider to retrieve details of another patient's records.

**Endpoint**: `GET /api/medical-records/:id`

**CWE**: CWE-639 (Authorization Bypass Through User-Controlled Key)

**Impact**: Medium — Any authenticated user can view another patient's sensitive medical records by enumerating record IDs.

**Detection**: Look for absence of ownership checks where the `:id` parameter is used without verifying the requesting user's role or relationship to the patient.

---

### V2: Plaintext Medical Data Export

**OWASP Category**: A02 — Cryptographic Failures

**Description**: An administrative database export endpoint returns all patient medical records including sensitive PII in plaintext format with no encryption or access scoping.

**Endpoint**: `GET /api/admin/database/export`

**CWE**: CWE-312 (Cleartext Storage of Sensitive Information)

**Impact**: High — Any admin user can download the full patient database dump containing names, addresses, medical conditions, and treatment notes in plaintext.

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

### Chain: "MD5 Password Cracking → Medical Records IDOR Exfiltration"

**Impact**: `db_exfiltration`

**Overview**: An attacker cracks a provider's MD5-hashed password, logs into their account, and exfiltrates sensitive patient medical records via IDOR.

**Components**:

| Step | Issue | Severity | OWASP | CWE | Location |
|---|---|---|---|---|---|
| 1 | Weak unsalted MD5 password hashing enables offline credential cracking | Medium | A07 | CWE-328 | `POST /api/auth/login` |
| 2 | Medical records endpoint lacks authorization checks for record ownership | Medium | A01 | CWE-639 | `GET /api/medical-records/:id` |

**Attack Narrative**:
1. The attacker obtains the users table (e.g., through SQL injection on another endpoint or data breach), retrieves the unsalted MD5 hash for `dr_smith`, and cracks the password offline.
2. Using the cracked credentials, the attacker logs in as `dr_smith` and calls `GET /api/medical-records/2` through IDOR to access another provider's patient medical records.
3. The attacker exfiltrates sensitive medical records across the platform without authorization.

**Combined Impact**: Database exfiltration — An attacker can steal sensitive patient medical records by cracking weak passwords and exploiting missing access controls.

---

## Decoys (False-Positive Candidates)

| Location | Description |
|---|---|
| `src/index.ts` | Proper user scoping constraints in `GET /api/patients` limiting results to assigned patients only |
| `src/index.ts` | Proper parameterized query logic in `POST /api/appointments` to book appointments safely |

---

## Detection Commands

```bash
# Find IDOR on medical records
grep -n "medical-records.*:id\|findOne\|findById" apps/typescript/app-14-telemedicine/src/index.ts

# Find plaintext data export
grep -n "export\|database\|admin" apps/typescript/app-14-telemedicine/src/index.ts

# Find weak password hashing
grep -n "md5\|hash\|password" apps/typescript/app-14-telemedicine/src/index.ts
```

---

*Report generated from `.vulns` manifest for app-14-telemedicine*