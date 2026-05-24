# Chained Vulnerability Scenario — Telecom Billing Platform

## Chain: "SQL Injection → Payment Fraud → No Audit Trail"

An external attacker exploits a chain of three weaknesses to defraud the telecom platform by stealing invoice data, replaying payments, and covering their tracks.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|----------------------|-------|----------|
| 1 | SQL injection in usage lookup allows exfiltrating details of other customers' invoices. | Medium | A03 | `UsageController.java` → `getUsageByDateRange()` |
| 2 | Payment endpoint lacks concurrency / replay / rate-limiting controls, allowing payment fraud. | Medium | A04 | `PaymentService.java` → `processPayment()` |
| 3 | Admin balance adjustments are not audit logged. | Low | A09 | `AdminController.java` → `adjustBalance()` |

**Attack narrative**: The attacker exploits the SQL injection vulnerability in the usage search endpoint to leak invoice details for multiple customers. Using this information, the attacker submits forged or replayed payment confirmations via the non-idempotent payment endpoint. Finally, the attacker utilizes the unlogged admin balance adjustment endpoint to modify balances and complete the fraud without detection.

**Combined Impact**: Unauthorized data modification — attacker manipulates billing records and balances without detection.