# Chained Vulnerability Scenarios — Support Tickets

## Chain: "Verbose Diagnostics Exposure → Administrative Ticket Export Bypass"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | System diagnostics endpoint leaks recovery keys | Medium | A05 | `src/index.ts` → `GET /api/system/health` |
| 2 | Backup export endpoint permits authentication bypass via recovery token | Medium | A01 | `src/index.ts` → `POST /api/admin/export` |


**Attack narrative**: 1. The attacker accesses `/api/system/health?diagnostics=true` and notices that it displays sensitive diagnostic information.
2. In the returned diagnostic config payload, the attacker discovers a hardcoded administrative recovery token (`SUPPORT-ADMIN-DEV-RECOVERY-KEY-2026`).
3. The attacker calls `/api/admin/export` passing the header `x-admin-token: SUPPORT-ADMIN-DEV-RECOVERY-KEY-2026`.
4. The server validates the token and returns a complete list of users and support tickets, achieving database exfiltration.

**Combined Impact**: `db_exfiltration` — Attacker gains administrative access to bulk download user records and private ticket history.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
