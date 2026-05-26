# Chained Vulnerability Scenarios — Compliance Tracker

## Chain: "Dev Mode Config Leak → Admin Document Retrieval Bypass"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Debug endpoint leaks administration recovery key | Medium | A05 | `src/index.ts` → `GET /api/admin/debug` |
| 2 | Document details endpoint allows IDOR retrieval via administration header | Medium | A01 | `src/index.ts` → `GET /api/documents/:id` |


**Attack narrative**: 1. The attacker visits `/api/admin/debug?dev=true` and retrieves the developer debug configuration.
2. In the returned payload, the attacker discovers a hardcoded administrative recovery key: `ADMIN-DEV-TOKEN-KEY-8871`.
3. The attacker requests a private document at `/api/documents/1` passing the header `x-admin-token: ADMIN-DEV-TOKEN-KEY-8871`.
4. The server validates the token, logs the caller in as administrative auditor, and returns the private tax compliance documents, achieving data bypass.

**Combined Impact**: `account_takeover` — Attacker gains administration access to bypass security boundaries and extract sensitive client files.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
