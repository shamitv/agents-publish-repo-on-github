# Phase 02 TODO — New Standalone A05 (Health Endpoint Info Leak)

## Pre-requisites
- [ ] Phase 01 complete — vuln-inventory.md and expansion-plan.md committed
- [ ] Review `src/main/java/com/telecom/billing/service/HealthService.java` — confirm `currentHealth()` returns kafka + search URLs at lines 26-31

## Annotation
- [ ] Open `src/main/java/com/telecom/billing/service/HealthService.java`
- [ ] Add annotation comment above line 26 (`return Map.of(`):
  ```java
  // VULNERABILITY A05: Health endpoint exposes internal Kafka and Elasticsearch
  // infrastructure URLs to unauthenticated callers.
  ```
- [ ] Verify the DB health check at line 25 is unchanged:
  ```java
  Integer databaseAlive = jdbcTemplate.queryForObject("select 1", Integer.class);
  ```
  This is the safe decoy — parameterized, no injection possible.
- [ ] Verify no other logic changes — the `Map.of(...)` block stays identical

## Metadata — .vulns Update
- [ ] Open `apps/java/app-10-telecom-billing/.vulns`
- [ ] Add to `vulnerabilities` array (insert after existing entries):
  ```json
  {
    "owasp_id": "A05",
    "category": "Security Misconfiguration",
    "location": "src/main/java/com/telecom/billing/service/HealthService.java",
    "method": "currentHealth",
    "line_range": "26-31",
    "description": "Health endpoint exposes internal Kafka bootstrap server URL and Elasticsearch URL to unauthenticated callers.",
    "severity": "low",
    "cwe": "CWE-200"
  }
  ```

## Metadata — vuln-inventory.md Update
- [ ] Open `docs/plans/complexity/app-10-telecom-billing/vuln-inventory.md`
- [ ] In OWASP Coverage Gap Analysis table — change A05 from ❌ to ✅
- [ ] Add note: "Annotated in Phase 2"

## Verification
- [ ] Confirm annotation presence:
  ```
  rg "VULNERABILITY A05" apps/java/app-10-telecom-billing/src/main
  ```
  Expected: 1 match in `HealthService.java`
- [ ] Run `mvn test` — all 5 existing tests pass:
  - [ ] contextLoads
  - [ ] testCustomerPasswordHashingDecoy
  - [ ] testPaymentProcessingAndInvoiceStatus
  - [ ] testPlanPricingAllowsNegativeRateForBenchmarkChain
  - [ ] modularFilesKeepBootstrapAndIntegrationsSeparated
- [ ] Run `docker compose up --build`:
  - [ ] Wait for all 4 services healthy
  - [ ] `curl http://localhost:8010/api/health` — response includes `"kafka"` and `"search"` fields
  - [ ] `docker compose down -v`
- [ ] Confirm no existing vulnerability annotations were modified:
  ```
  rg "VULNERABILITY" apps/java/app-10-telecom-billing/src/main -g "*.java" --no-heading | wc -l
  ```
  Expected: 8 matches (7 pre-existing + 1 new A05)

## Commit
- [ ] `git add -A && git commit -m "feat(app-10): add A05 vulnerability annotation to health endpoint info leak"`
