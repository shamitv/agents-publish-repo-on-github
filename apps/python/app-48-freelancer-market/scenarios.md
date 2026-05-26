# Chained Vulnerability Scenarios — Freelancer Market

## Chain: "Weak Token → IDOR Bid Espionage → Payment Fraud"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Predictable session token generation | Medium | A07 | `app.py` → `login()` |
| 2 | IDOR on proposals leaks competitor bid details | Medium | A01 | `app.py` → `get_proposal()` |


**Attack narrative**: 1. The attacker logs in and notices the session token is a simple six-digit number. The token generator utilizes python's `random.randint()` initialized with a static/reproducible state.
2. The attacker predicts session tokens for other registered client accounts and inputs the hijacked session ID into their request cookies.
3. Once logged in as a victim client, the attacker queries the proposal details endpoint `/api/proposals/<proposal_id>`. Since the system does not check proposal ownership, the attacker reads competitor bid descriptions and pricing options.
4. Finally, the attacker triggers `/api/jobs/<job_id>/release-payment`. The system accepts the action and releases payment funds to the freelancer without verifying the request source or checking work completion.

**Combined Impact**: `account_takeover` — Attacker hijacks other users' client sessions, steals competitor data, and commits escrow financial fraud.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
