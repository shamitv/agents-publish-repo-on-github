# Chained Vulnerability Scenarios — Insurance Claims

## Chain: "SQL Injection → IDOR Claim Access → Silent Payout Fraud"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | SQL injection in claim search reveals internal claim IDs | Medium | A03 | `app.py` → `search_claims()` |
| 2 | IDOR on claim detail endpoint allows viewing/modifying any claim | Medium | A01 | `app.py` → `get_claim()` |
| 3 | No audit logging on claim approval allows silent payout | Low | A09 | `app.py` → `approve_claim()` |


**Attack narrative**: 1. The attacker logs in as a low-privileged customer.
2. The attacker uses the claim search endpoint `/api/claims/search?q=1' OR '1'='1` (or union-based payloads) to trigger SQL injection, leaking claim IDs, status, and request details for other users.
3. The attacker requests specific claim details using the IDOR vulnerability at `/api/claims/<claim_id>`. Since there is no ownership check, they retrieve the claimant's information.
4. Using adjuster credentials (or session takeover/escalation if combined, or directly if they possess an adjuster account but want to perform actions without detection), they approve the claims at `/api/claims/<claim_id>/approve`. Because the system fails to log this action, the fraud goes completely unnoticed.

**Combined Impact**: `data_modification` — Attacker executes unauthorized payouts silently without any audit trail or logging records.

---

_This file is for internal reference. Ground truth vulnerability data is maintained in [.vulns](.vulns)._
