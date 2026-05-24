# Chained Vulnerability Scenarios — Subscription Box

## Chain: "Package Search SQLi → Unsalted MD5 Credential Cracking"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | SQL injection in package search leaks user details | High | A03 | `src/index.ts` → `GET /api/packages/search` |
| 2 | MD5 unsalted password storage leads to authentication bypass | Medium | A07 | `src/index.ts` → `POST /api/auth/login` |


**Attack narrative**: 1. The attacker visits `/api/packages/search?q=coffee' UNION SELECT 1,username,password_hash,role FROM users --`.
2. The server processes the malformed search query, executing the SQL union and returning the user names and unsalted MD5 password hashes.
3. The attacker copies the MD5 hash `a57e4e138a08d3744952bd0176cd1f91` belonging to `admin_agent`.
4. The attacker runs a brute-force or rainbow table lookup tool offline, discovering the password is `'adminpass2026'`.
5. The attacker logs in via the login API, taking over the administrator account.

**Combined Impact**: `account_takeover` — Attacker obtains full administrative access to control all customer subscriptions and orders.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
