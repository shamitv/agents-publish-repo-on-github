# Security Report: app-41-library-reservation

## Application Information

- **App ID**: app-41
- **App Name**: Library Book Reservation System
- **Language**: JavaScript
- **Framework**: Express
- **Source**: `apps/javascript/app-41-library-reservation/`

---

## Vulnerability Summary

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | `src/index.js` → `GET /api/reservations/:id` (lines 146-162) | CWE-639 |
| V2 | A03 | Injection | High | `src/index.js` → `GET /api/books/search` (lines 165-177) | CWE-89 |
| V3 | A07 | Identification and Authentication Failures | Medium | `src/index.js` → `POST /api/auth/login` (lines 100-123) | CWE-328 |

### V1: IDOR on Reservation Details

**OWASP Category**: A01 — Broken Access Control

**Description**: Viewing book reservation logs by ID lacks verification of user ownership, allowing any authenticated borrower to retrieve details of another borrower's history.

**Endpoint**: `GET /api/reservations/:id`

**CWE**: CWE-639 (Authorization Bypass Through User-Controlled Key)

**Impact**: Medium — Any authenticated user can view another user's private reservation history including book titles, dates, and personal notes.

**Detection**: Look for absence of ownership checks in the reservation detail handler where the `:id` parameter is used without verifying `req.user.id` matches the reservation's user ID.

---

### V2: SQL Injection on Book Search

**OWASP Category**: A03 — Injection

**Description**: User search parameter is directly concatenated into SQL query statement, exposing the database to SQL injection.

**Endpoint**: `GET /api/books/search`

**CWE**: CWE-89 (SQL Injection)

**Impact**: High — An attacker can extract arbitrary data from the database including user credentials, passwords, and other sensitive records via UNION-based SQL injection.

**Detection**: Search for raw string concatenation with user-supplied `q` parameter inside `db.all()` or `db.query()` calls in the book search handler.

---

### V3: Unsalted MD5 Password Hashing

**OWASP Category**: A07 — Identification and Authentication Failures

**Description**: User account passwords are encrypted using unsalted MD5 hashing and saved in the database, allowing brute-force or rainbow table cracking.

**Endpoint**: `POST /api/auth/login`

**CWE**: CWE-328 (Use of Weak Hash)

**Impact**: Medium — If the password database is compromised, an attacker can crack passwords offline using precomputed rainbow tables or brute-force techniques.

**Detection**: Search for `md5()` usage in password hashing/verification logic instead of bcrypt, scrypt, or argon2.

---

## Chained Attack Scenario

### Chain: "Book Search SQLi → Unsalted MD5 librarian account cracking"

**Impact**: `account_takeover`

**Overview**: An attacker uses SQL injection on the book search endpoint to dump the users table, cracks the admin librarian's unsalted MD5 password offline, and takes over the admin account.

**Components**:

| Step | Issue | Severity | OWASP | CWE | Location |
|---|---|---|---|---|---|
| 1 | Union-based SQL injection on book search exposes internal database tables | Medium | A03 | CWE-89 | `GET /api/books/search` |
| 2 | Admin passwords stored as unsalted MD5 hashes are cracked offline, enabling account takeover | Medium | A07 | CWE-328 | `POST /api/auth/login` |

**Attack Narrative**:
1. The attacker sends `GET /api/books/search?q=1984' UNION SELECT 1,username,password_hash,role FROM users --` to dump the users table via SQL injection.
2. They retrieve the unsalted MD5 hash `db59fe16fcdcc4e70e3047d9539f37c3` for the `admin_librarian` user.
3. By performing offline MD5 decryption/lookup, they crack the admin password `librarianSecure2026!` and log in as the admin.
4. Using the admin session, they exfiltrate private reader reservation details via IDOR on `GET /api/reservations/:id`.

**Combined Impact**: Account takeover — An attacker can crack the librarian admin password and access all reservation records in the system.

---

## Decoys (False-Positive Candidates)

| Location | Description |
|---|---|
| `src/index.js` | Proper parameterized query logic in `GET /api/books/:id` to retrieve single books safely |
| `src/index.js` | Proper user scoping constraints in `GET /api/reservations` limiting output database entries to active customer only |

---

## Detection Commands

```bash
# Find SQL injection on book search
grep -n "SELECT.*\+.*req\.query\|db\.all.*req" apps/javascript/app-41-library-reservation/src/index.js

# Find weak password hashing
grep -n "md5\|hash\|password" apps/javascript/app-41-library-reservation/src/index.js

# Find IDOR on reservations
grep -n "reservations.*:id\|findById\|findOne" apps/javascript/app-41-library-reservation/src/index.js
```

---

*Report generated from `.vulns` manifest for app-41-library-reservation*