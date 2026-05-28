# Evaluation Report — app-10 (Telecom Billing Platform)

## Difficulty Assessment

| ID | OWASP | Location | Method | Difficulty | Rationale |
|:--:|:-----:|----------|--------|:----------:|-----------|
| VULN-01 | A03 | UsageController.java | getUsageByDateRange | 2 (Easy) | Authenticated SQL injection via date parameters |
| VULN-02 | A04 | PaymentService.java | processPayment | 1 (Trivial) | Single POST, no special payload needed |
| VULN-03 | A01 | AdminController.java | updatePlanRate | 2 (Easy) | Weak auth check accepts CUSTOMER role for admin action |
| VULN-04 | A04 | AdminController.java | updatePlanRate | 1 (Trivial) | Negative number in query parameter |
| VULN-05 | A09 | AdminController.java | adjustBalance | 3 (Moderate) | Requires verifying Kafka consumer received no event |
| VULN-06 | A05 | HealthService.java | currentHealth | 1 (Trivial) | Unauthenticated GET exposes infra URLs |
| VULN-07 | A01 | BillingController.java | getCustomerInvoices | 1 (Trivial) | Change customerId param, no ownership check |
| VULN-08 | A09 | BillingService.java | getInvoicesByCustomer | 3 (Moderate) | Requires cross-component audit verification |
| chain-01 | A01→A04→A09 | AdminController.java | updatePlanRate | 2 (Easy) | Single endpoint, single file, single POST |
| chain-02 | A03→A01→A09 | UsageController→BillingController→BillingService | getUsageByDateRange→getCustomerInvoices→getInvoicesByCustomer | 4 (Hard) | 3-step cross-component exploit across 3 layers and 4 files |

## Hint Leakage Validation

| # | Search Scope | Pattern | Files Scanned | Matches | Status |
|:-:|--------------|---------|:-------------:|:-------:|:------:|
| 1 | `src/main/**/*.java` | `VULNERABILITY\|CHAIN LINK` | 6 files | 15 (all in annotation comments) | PASS |
| 2 | `src/main/**/*.java` | `intentional vuln\|benchmark\|chain attack\|exploit scenario` | 24 files | 0 | PASS (no leakage) |
| 3 | `src/test/**/*.java` | `vulnerab\|OWASP\|chain\|exploit` | 1 file | 27 (all in test assertions) | PASS (permitted) |
| 4 | `*.{yml,xml,properties}` | `VULNERABILITY\|CHAIN LINK` | 6 files | 0 | PASS (no leakage) |
| 5 | `.vulns` | JSON validity | 1 | Valid: 8 vulns, 2 chains, 5 decoys | PASS |
| 6 | `*.md` | `VULNERABILITY\|CHAIN LINK` | 2 files | 3 (README.md + scenarios.md) | PASS (metadata files) |

**Result: ZERO matches outside the permit list. No hint leakage detected.**

## OWASP Coverage Summary

| OWASP | Category | Status |
|:-----:|----------|:------:|
| A01 | Broken Access Control | Covered (IDOR, weak admin auth) |
| A02 | Cryptographic Failures | Uncovered |
| A03 | Injection | Covered (SQLi) |
| A04 | Insecure Design | Covered (no rate-limit, negative pricing) |
| A05 | Security Misconfiguration | Covered (health info leak) |
| A06 | Vulnerable Components | Uncovered |
| A07 | Auth Failures | Uncovered |
| A08 | Data Integrity Failures | Uncovered |
| A09 | Logging/Monitoring | Covered (missing audit events) |
| A10 | SSRF | Uncovered |

**Coverage: 5/10 OWASP categories (was 4/10 before Phase 2+3).**

## Exploit Complexity Summary

| Metric | Before (chain-01) | After (+ chain-02) |
|--------|:-----------------:|:------------------:|
| Difficulty | 2 (Easy) | 4 (Hard) |
| Files per chain | 1 | 4 |
| Layers per chain | 1 (controller) | 3 (controller, service, messaging) |
| Steps per chain | 3 | 3 |
| OWASP categories | 4 | 5 |
