# Phase 03 TODO — New Chain-02 (Multi-Component Exploit Chain)

## Pre-requisites
- [ ] Phase 02 complete — A05 annotation in place, .vulns updated with A05 entry
- [ ] Review `UsageController.java` — confirm existing A03 annotation at line 23
- [ ] Review `BillingController.java` — confirm `getCustomerInvoices(@RequestParam Long customerId)` has no ownership check
- [ ] Review `BillingService.java` — confirm `getInvoicesByCustomer()` does not call `BillingAuditProducer.publish()`

---

## Step 1: UsageController — Chain Link 1 Annotation

- [ ] Open `src/main/java/com/telecom/billing/controller/UsageController.java`
- [ ] Insert CHAIN LINK comment at line 22 (immediately BEFORE the existing `// VULNERABILITY A03` line 23):
  ```java
  // CHAIN LINK 1 (chain-02): SQLi on usage records allows an attacker to enumerate
  // customer IDs and plan associations across the billing system.
  // VULNERABILITY A03: Native SQL is built with user-controlled date values.
  ```
- [ ] Verify the existing A03 annotation text on line 23-24 is preserved exactly as-is
- [ ] Verify no other lines changed — the SQL string concatenation at line 24-25 stays identical

## Step 2: BillingController — Chain Link 2 + A01 Annotation

- [ ] Open `src/main/java/com/telecom/billing/controller/BillingController.java`
- [ ] Insert annotations on lines 22-23 (immediately BEFORE `@GetMapping("/invoices")`):
  ```java
  // CHAIN LINK 2 (chain-02): Invoice endpoint lacks per-customer access control —
  // any authenticated user can query any customer's invoices by ID.
  // VULNERABILITY A01: BillingController exposes all customer invoices with no
  // ownership enforcement.
  @GetMapping("/invoices")
  ```
- [ ] Verify no logic change — `getCustomerInvoices(@RequestParam Long customerId)` body stays identical
- [ ] Confirm no `Principal` parameter or ownership check is added

## Step 3: BillingService — Chain Link 3 + A09 Annotation

- [ ] Open `src/main/java/com/telecom/billing/service/BillingService.java`
- [ ] Insert annotations on lines 20-21 (immediately BEFORE `public List<Invoice> getInvoicesByCustomer`):
  ```java
  // CHAIN LINK 3 (chain-02): Bulk invoice reads cross no audit boundary —
  // BillingAuditProducer is available but never called during customer invoice retrieval.
  // VULNERABILITY A09: Get-invoice queries bypass the configured billing audit producer.
  public List<Invoice> getInvoicesByCustomer(Long customerId) {
  ```
- [ ] Verify no logic change — method body stays identical (no `auditProducer.publish(...)` call added)
- [ ] Confirm `BillingAuditProducer` is not injected into BillingService — the gap is real

## Metadata — .vulns Update

- [ ] Open `apps/java/app-10-telecom-billing/.vulns`
- [ ] Add to `vulnerabilities` array (2 new standalone entries):
  ```json
  {
    "owasp_id": "A01",
    "category": "Broken Access Control",
    "location": "src/main/java/com/telecom/billing/controller/BillingController.java",
    "method": "getCustomerInvoices",
    "line_range": "23-26",
    "description": "Invoice query endpoint has no per-customer access control — any authenticated user can read any customer's full invoice history.",
    "severity": "medium",
    "cwe": "CWE-639"
  },
  {
    "owasp_id": "A09",
    "category": "Security Logging and Monitoring Failures",
    "location": "src/main/java/com/telecom/billing/service/BillingService.java",
    "method": "getInvoicesByCustomer",
    "line_range": "21-23",
    "description": "Invoice retrieval bypasses the available billing audit producer — sensitive data reads generate no audit events.",
    "severity": "low",
    "cwe": "CWE-778"
  }
  ```
- [ ] Add to `chained_attacks` array (1 new entry after existing chain-01):
  ```json
  {
    "chain_id": "chain-02",
    "chain_name": "Usage SQL Injection → Invoice IDOR → Audit Bypass → db_exfiltration",
    "attack_scenario": "An attacker uses SQL injection on the usage search endpoint to enumerate all customer IDs, then iterates through those IDs against the unprotected invoice endpoint to bulk-extract every customer's complete billing history. The mass data access produces no audit trail because BillingAuditProducer is never invoked during invoice reads.",
    "impact": "db_exfiltration",
    "components": [
      {
        "step": 1,
        "owasp_id": "A03",
        "description": "SQL injection on usage search allows attacker to enumerate customer IDs and plan associations across the billing system.",
        "location": "src/main/java/com/telecom/billing/controller/UsageController.java",
        "method": "getUsageByDateRange",
        "severity": "medium",
        "cwe": "CWE-89"
      },
      {
        "step": 2,
        "owasp_id": "A01",
        "description": "Invoice endpoint has no per-customer ownership check — attacker reads any customer's invoices by cycling through enumerated customer IDs.",
        "location": "src/main/java/com/telecom/billing/controller/BillingController.java",
        "method": "getCustomerInvoices",
        "severity": "medium",
        "cwe": "CWE-639"
      },
      {
        "step": 3,
        "owasp_id": "A09",
        "description": "Bulk invoice reads bypass the available BillingAuditProducer — mass data extraction leaves no audit event trail.",
        "location": "src/main/java/com/telecom/billing/service/BillingService.java",
        "method": "getInvoicesByCustomer",
        "severity": "low",
        "cwe": "CWE-778"
      }
    ]
  }
  ```
- [ ] Add to `decoys` array (2 new entries):
  ```json
  {
    "location": "src/main/java/com/telecom/billing/controller/CustomerController.java",
    "description": "getCustomer endpoint has proper principal-based ownership check — adjacent to BillingController which lacks the same check."
  },
  {
    "location": "src/main/java/com/telecom/billing/messaging/BillingAuditProducer.java",
    "description": "Audit producer correctly publishes to Kafka when called — the vulnerability is specific endpoints not invoking it, not the producer itself."
  }
  ```
- [ ] Verify JSON validity — no trailing commas, all braces balanced

## Metadata — README.md Update

- [ ] Open `apps/java/app-10-telecom-billing/README.md`
- [ ] Insert Chain-02 section after existing "Chained Vulnerability Scenario" section and the chain-01 block (before "API Endpoints"):
  ```markdown
  ### Chain: "Usage SQL Injection → Invoice IDOR → Audit Bypass → db_exfiltration"

  An attacker enumerates customer IDs via SQL injection on usage search, then iterates through those IDs on the unprotected invoice endpoint to bulk-extract billing history with no audit trail.

  | Step | Issue | Severity (standalone) | OWASP | Location |
  |------|-------|-----------------------|-------|----------|
  | 1 | SQL injection on usage search enumerates customer IDs and plan associations | Medium | A03 | `src/main/java/com/telecom/billing/controller/UsageController.java` → `getUsageByDateRange()` |
  | 2 | Invoice endpoint has no per-customer access control — any ID is readable | Medium | A01 | `src/main/java/com/telecom/billing/controller/BillingController.java` → `getCustomerInvoices()` |
  | 3 | Bulk invoice reads bypass the available BillingAuditProducer — zero audit events | Low | A09 | `src/main/java/com/telecom/billing/service/BillingService.java` → `getInvoicesByCustomer()` |

  **Attack narrative**: The attacker authenticates, injects SQL via `GET /api/usage/search` to discover valid customer IDs across the system, then calls `GET /api/billing/invoices?customerId=<N>` for each discovered ID to extract every customer's invoice records. The mass extraction produces no Kafka audit events because `BillingAuditProducer.publish()` is never called during invoice retrieval.

  **Combined Impact**: The attacker can exfiltrate the complete billing history of all customers with zero audit footprint, resulting in high-impact database exfiltration.
  ```
- [ ] Confirm existing chain-01 section and all other sections are unchanged

## Metadata — scenarios.md Update

- [ ] Open `apps/java/app-10-telecom-billing/scenarios.md`
- [ ] Add chain-02 supplement after existing chain-01 content:
  ```markdown
  ## Chain: "Usage SQL Injection → Invoice IDOR → Audit Bypass → db_exfiltration"

  | Step | Issue | Severity (standalone) | OWASP | Location |
  |------|-------|-----------------------|-------|----------|
  | 1 | SQLi on usage search | Medium | A03 | `UsageController.java` → `getUsageByDateRange()` |
  | 2 | IDOR on invoice query | Medium | A01 | `BillingController.java` → `getCustomerInvoices()` |
  | 3 | Audit bypass on invoice reads | Low | A09 | `BillingService.java` → `getInvoicesByCustomer()` |

  **Attack narrative**: Authenticated attacker injects SQL to enumerate customer IDs via usage search, then iterates through each ID against the invoice endpoint to bulk-extract billing history. `BillingAuditProducer.publish()` is never invoked, leaving zero audit events.

  **Combined Impact**: db_exfiltration — complete billing history of all customers extracted without audit trail.
  ```

## Metadata — vuln-inventory.md Update

- [ ] Open `docs/plans/complexity/app-10-telecom-billing/vuln-inventory.md`
- [ ] Update OWASP Coverage table — A01 and A09 already covered, no gap change needed
- [ ] Update "Unannotated Exploit Surfaces" section — remove entries for BillingController and BillingService (now annotated)
- [ ] Update "Target State" table — reflect 7 standalone vulns, 2 chains, 5 decoys

## Verification

- [ ] Annotation presence check:
  ```
  rg "CHAIN LINK 1 \(chain-02\)" apps/java/app-10-telecom-billing/src/main
  rg "CHAIN LINK 2 \(chain-02\)" apps/java/app-10-telecom-billing/src/main
  rg "CHAIN LINK 3 \(chain-02\)" apps/java/app-10-telecom-billing/src/main
  ```
  Expected: 1 match each (UsageController, BillingController, BillingService)
- [ ] New standalone annotations:
  ```
  rg "VULNERABILITY A01.*BillingController" apps/java/app-10-telecom-billing/src/main
  rg "VULNERABILITY A09.*get-invoice\|bypasses" apps/java/app-10-telecom-billing/src/main
  ```
- [ ] `.vulns` JSON validity — format check
- [ ] `.vulns` chain-02 components count is 3
- [ ] `.vulns` chain-02 impact is `db_exfiltration`
- [ ] Run `mvn test` — all 5 existing tests pass
- [ ] Docker smoke test:
  - [ ] `docker compose up --build`
  - [ ] Step 1 (SQLi): `curl -u alice:alice123 "http://localhost:8010/api/usage/search?customerId=1&startDate=2020-01-01&endDate=2026-12-31"` → returns usage records
  - [ ] Step 2 (IDOR): `curl -u alice:alice123 "http://localhost:8010/api/billing/invoices?customerId=2"` → returns admin's invoices (IDOR confirmed)
  - [ ] `docker compose down -v`

## Commit
- [ ] `git add -A && git commit -m "feat(app-10): add chain-02 cross-component exploit chain — SQLi→IDOR→audit bypass→db_exfiltration (UsageController, BillingController, BillingService, BillingAuditProducer bypassed)"`
