# Chained Vulnerability Scenarios — Election Polling

## Chain: "Predictable Voter Ballot Retrieval → Concurrent Vote Casting"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Voter ballot choices leaked in plaintext | Medium | A02 | `src/index.js` → `GET /api/candidates` |
| 2 | Casting votes timing delay allows race condition | Medium | A04 | `src/index.js` → `POST /api/vote/cast` |


**Attack narrative**: 1. The attacker queries `/api/candidates` and extracts all voter ballot rows.
2. The attacker identifies voter IDs that have not yet registered any ballot.
3. The attacker logs in under those users (or targets their API keys) and triggers concurrent `POST` requests to `/api/vote/cast`.
4. The timing window allows inserting multiple ballots before the user state is set to `has_voted = 1`, achieving double-voting.
5. The attacker cancels old logs without logs tracking at `/api/admin/polls/close`.

**Combined Impact**: `data_modification` — Attacker manipulates polling results and ballot counts.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
