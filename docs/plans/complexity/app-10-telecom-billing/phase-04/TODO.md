# Phase 04 TODO — Integration Verification & Metadata Sync

## Pre-requisites
- [ ] Phase 03 complete — all chain-02 annotations, .vulns, README, scenarios updated

---

## Test Updates — App10ApplicationTests.java

- [ ] Open `src/test/java/com/telecom/billing/App10ApplicationTests.java`
- [ ] Add `testChain02MetadataMatchesManifest()` method (after the existing `benchmarkMetadataMatchesCanonicalChain` test):

  ```java
  @Test
  void testChain02MetadataMatchesManifest() throws Exception {
      JsonNode manifest = new ObjectMapper().readTree(Path.of(".vulns").toFile());
      JsonNode chain = null;
      for (JsonNode c : manifest.path("chained_attacks")) {
          if ("chain-02".equals(c.path("chain_id").asText())) {
              chain = c;
              break;
          }
      }
      assertNotNull(chain, "chain-02 not found in .vulns chained_attacks");
      assertEquals("db_exfiltration", chain.path("impact").asText());
      assertEquals(3, chain.path("components").size());
      assertEquals("getUsageByDateRange", chain.path("components").get(0).path("method").asText());
      assertEquals("getCustomerInvoices", chain.path("components").get(1).path("method").asText());
      assertEquals("getInvoicesByCustomer", chain.path("components").get(2).path("method").asText());

      String usageCt = Files.readString(Path.of(
          "src/main/java/com/telecom/billing/controller/UsageController.java"));
      assertTrue(usageCt.contains("CHAIN LINK 1 (chain-02)"));

      String billingCt = Files.readString(Path.of(
          "src/main/java/com/telecom/billing/controller/BillingController.java"));
      assertTrue(billingCt.contains("CHAIN LINK 2 (chain-02)"));

      String billingSv = Files.readString(Path.of(
          "src/main/java/com/telecom/billing/service/BillingService.java"));
      assertTrue(billingSv.contains("CHAIN LINK 3 (chain-02)"));
  }
  ```

- [ ] Add `testHealthEndpointExposesInfraUrls()` method:

  ```java
  @Test
  void testHealthEndpointExposesInfraUrls() throws Exception {
      String healthService = Files.readString(Path.of(
          "src/main/java/com/telecom/billing/service/HealthService.java"));
      assertTrue(healthService.contains("VULNERABILITY A05"));
      assertTrue(healthService.contains("\"kafka\""));
      assertTrue(healthService.contains("\"search\""));
  }
  ```

## Test Suite Run

- [ ] Run `mvn test`
- [ ] Confirm all 7 tests pass:
  - [ ] contextLoads
  - [ ] testCustomerPasswordHashingDecoy
  - [ ] testPaymentProcessingAndInvoiceStatus
  - [ ] testPlanPricingAllowsNegativeRateForBenchmarkChain
  - [ ] modularFilesKeepBootstrapAndIntegrationsSeparated
  - [ ] benchmarkMetadataMatchesCanonicalChain
  - [ ] testChain02MetadataMatchesManifest (NEW)
  - [ ] testHealthEndpointExposesInfraUrls (NEW)

## Docker Smoke Test

- [ ] `docker compose up --build`
- [ ] Wait for all 4 services healthy:
  - [ ] web (health: `curl -fsS localhost:8082/api/health`)
  - [ ] postgres (pg_isready)
  - [ ] kafka (rpk cluster info)
  - [ ] elasticsearch (/_cluster/health)
- [ ] Health check: `curl http://localhost:8010/api/health` → 200, includes kafka/search
- [ ] Auth check: `curl -u alice:alice123 http://localhost:8010/api/auth/me` → alice profile
- [ ] Chain-01 check: `curl -u alice:alice123 "http://localhost:8010/api/admin/plans/1/rate?customRate=-99.99"` → returns plan with negative rate
- [ ] Chain-02 Step 1 (SQLi): `curl -u alice:alice123 "http://localhost:8010/api/usage/search?customerId=1&startDate=2020-01-01&endDate=2026-12-31"` → returns usage records
- [ ] Chain-02 Step 2 (IDOR): `curl -u alice:alice123 "http://localhost:8010/api/billing/invoices?customerId=2"` → returns admin's invoices (confirm customerId=2 is admin)
- [ ] Tear down: `docker compose down -v`
- [ ] Clean up: `docker system prune -a -f --volumes`

## Master Index Update

- [ ] Open `docs/plans/complexity/README.md`
- [ ] Change app-10 row (currently line 26):
  - Phase Structure: change `_Phase structure pending_` to linked:
    ```
    [Plan](app-10-telecom-billing/expansion-plan.md) - [Phase 1](app-10-telecom-billing/phase-01/plan.md) ... [Phase 5](app-10-telecom-billing/phase-05/plan.md)
    ```
  - Phase Count: change `-` to `5`
  - Status: change `Pending` to `Implemented`
- [ ] Verify updated row:
  ```markdown
  | **10** | Telecom Billing Platform | Java (Spring Boot) | Postgres, TimescaleDB, Kafka, MVC, Multi-Tier Tariffs | [Plan](app-10-telecom-billing/expansion-plan.md) - [Phase 1](app-10-telecom-billing/phase-01/plan.md) ... [Phase 5](app-10-telecom-billing/phase-05/plan.md) | 5 | Implemented |
  ```

## Final Annotation Audit

- [ ] Total `VULNERABILITY` annotations in `.java` files:
  ```
  rg -c "VULNERABILITY" apps/java/app-10-telecom-billing/src/main -g "*.java"
  ```
  Expected: 10 occurrences (7 standalone + 3 chain-paired vulns)

- [ ] Total `CHAIN LINK` annotations:
  ```
  rg -c "CHAIN LINK" apps/java/app-10-telecom-billing/src/main -g "*.java"
  ```
  Expected: 6 occurrences (3 chain-01 + 3 chain-02)

- [ ] Per-file breakdown:
  | File | VULNERABILITY | CHAIN LINK |
  |------|:---:|:---:|
  | AdminController.java | 5 | 3 |
  | UsageController.java | 1 | 1 |
  | PaymentService.java | 1 | — |
  | HealthService.java | 1 | — |
  | BillingController.java | 1 | 1 |
  | BillingService.java | 1 | 1 |

## Commit
- [ ] `git add -A && git commit -m "test(app-10): add chain-02 metadata and A05 verification tests; update master complexity index"`
