# Chained Vulnerability Scenario — Telecom Billing Platform

Supplemental notes only. Ground truth vulnerability data is maintained in [.vulns](.vulns), and the required human-readable chain is in [README.md](README.md).

## Chain: "Weak Billing Admin Auth → Unvalidated Custom Rate → Missing Audit Logs"

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Pricing endpoint trusts `CUSTOMER` users as billing admins | Medium | A01 | `AdminController.java` → `updatePlanRate()` |
| 2 | Negative or arbitrary custom rates are accepted and persisted | Medium | A04 | `AdminController.java` → `updatePlanRate()` |
| 3 | Rate changes bypass the available audit event producer | Low | A09 | `AdminController.java` → `updatePlanRate()` |

**Attack narrative**: A normal customer calls the plan-rate endpoint with a negative rate, the value is persisted without validation, and no audit event is emitted for the billing mutation.

**Combined Impact**: Unauthorized data modification of stored telecom billing plan rates.
