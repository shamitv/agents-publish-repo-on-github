# Chained Vulnerability Scenarios — P2P Lending

## Chain: "Plaintext Credential Leak → IDOR Loan Data Harvesting"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Passwords saved in plaintext database | Medium | A02 | `src/index.js` → `initDb` |
| 2 | Loan details endpoint is vulnerable to IDOR | Medium | A01 | `src/index.js` → `GET /api/contracts/:id` |


**Attack narrative**: 1. The attacker queries `/api/debug/users` to dump all user records.
2. In the returned list, they extract the administrator's plaintext password: `lenderSecure2026!`.
3. The attacker logs in using the admin account.
4. Using the admin session, the attacker queries `/api/contracts/:id` sequentially to harvest all user agreements, achieving bulk data exfiltration.

**Combined Impact**: `db_exfiltration` — Attacker gains administration credentials to harvest private client records.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
