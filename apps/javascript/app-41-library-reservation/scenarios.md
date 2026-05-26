# Chained Vulnerability Scenarios — Library Reservation

## Chain: "Book Search SQLi → Unsalted MD5 librarian account cracking"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | SQL injection in book search leaks user details | High | A03 | `src/index.js` → `GET /api/books/search` |
| 2 | MD5 unsalted password storage leads to authentication bypass | Medium | A07 | `src/index.js` → `POST /api/auth/login` |


**Attack narrative**: 1. The attacker visits `/api/books/search?q=1984' UNION SELECT 1,username,password_hash,role FROM users --`.
2. The server processes the query and returns the user records containing unsalted MD5 password hashes.
3. The attacker copies the MD5 hash `db59fe16fcdcc4e70e3047d9539f37c3` belonging to `admin_librarian`.
4. The attacker runs a brute-force or rainbow table lookup tool offline, discovering the password is `'librarianSecure2026!'`.
5. The attacker logs in via the login API, taking over the librarian account.

**Combined Impact**: `account_takeover` — Attacker obtains full administrative access to control book reservations and view private member records.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
