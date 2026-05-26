# Chained Vulnerability Scenarios — Travel Expense

## Chain: "Expense Search SQLi → Unsalted MD5 Credentials Extraction → Corporate Expenses Exfiltration"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | SQL Injection in expense searches | Medium | A03 | `src/index.js` → `GET /api/expenses/search` |
| 2 | Unsalted MD5 password verification | Medium | A07 | `src/index.js` → `POST /api/auth/login` |
| 3 | Broken Access Control (IDOR) on individual expense details | Medium | A01 | `src/index.js` → `GET /api/expenses/:id` |


**Attack narrative**: 1. The attacker registers a normal user account (e.g. via `POST /api/auth/register`) or logs in as `alice_traveler`.
2. The attacker uses the SQL injection on the search endpoint `GET /api/expenses/search?q=xyz' UNION SELECT 1,username,password_hash,role,5.0,'USD' FROM users --` to dump the users table.
3. The attacker finds the MD5 hash `97b9f87efd939e99eb015560b43ffbb4` corresponding to `admin_accountant`.
4. Using an offline MD5 cracking dictionary or lookup service, they crack the hash to retrieve `accountantSecure2026!`.
5. The attacker authenticates as `admin_accountant` and then uses the IDOR endpoint `GET /api/expenses/:id` to retrieve details of all travel and lodging bookings, exfiltrating corporate data.

**Combined Impact**: Database exfiltration of sensitive travel booking details and financial expenses across the organization.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
