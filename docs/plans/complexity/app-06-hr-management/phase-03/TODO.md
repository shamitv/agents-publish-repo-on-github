# Phase 03 TODO — Search Injection + Audit Gap

## Pre-requisites
- [ ] Phase 2 complete: onboarding workflow running
- [ ] Phase 1 complete: Elasticsearch accessible
- [ ] Read vuln-inventory.md — confirm no-touch files

## A03 — Elasticsearch Injection
- [ ] Edit `src/main/java/com/hr/search/EmployeeSearchClient.java`:
  - Add method `searchEmployeesRaw(String query)`:
    - Builds ES query string by concatenating user input: `"{\"query\":{\"query_string\":{\"query\":\"" + query + "\"}}}"`
    - Sends via `RestTemplate` to `{elasticsearchUrl}/employees/_search`
    - Do NOT use any query builder or parameterization
    - Add comment: `// VULNERABILITY A03: Employee search concatenates user input directly into Elasticsearch query_string syntax.`
  - Ensure existing `searchEmployees(String query)` method is preserved as decoy:
    - Uses proper `NativeSearchQuery` builder or Spring Data Elasticsearch
    - Add comment noting it's safe (if not already present)
- [ ] Wire `EmployeeController.listEmployees()` to call `searchEmployeesRaw()` when `?q=` param is present

## A09 — Missing Audit Logging
- [ ] Edit `src/main/java/com/hr/service/OnboardingWorkflowService.java`:
  - In `transition()` method, after applying state change to PostgreSQL:
    - Do NOT write to any audit table or audit log
    - Add comment: `// VULNERABILITY A09: Onboarding state transitions persist without writing audit log entries.`
    - Add comment: `// CHAIN LINK 2 (chain-02): Onboarding state change applied without audit event — no trail of who bypassed Background Check.`
  - Add decoy print statement before the return:
    - `System.out.println("AUDIT: onboarding=" + onboardingId + " transitioned to " + targetState);`
    - This prints to console but writes nothing to any database

## Verification
- [ ] Restart app
- [ ] Verify A03 injection:
  - `GET /api/employees?q=*` → returns all employees (wildcard injection)
  - `GET /api/employees?q={\"match_all\":{}}` → returns all (raw JSON injection)
  - Compare with safe method (should not respond to raw JSON in query)
- [ ] Verify A09 vulnerability:
  - Transition onboarding state via `PUT /api/onboarding/1/transition`
  - Check PostgreSQL for any audit log table → should NOT exist
  - Check console output for the decoy print → should show "AUDIT: onboarding=..."
- [ ] Verify chain-02 end-to-end:
  - Step 1 (A04): Transition Draft→Active directly (skip Background Check)
  - Step 2 (A09): Verify no audit log entry for this transition
- [ ] Verify existing vulnerabilities still exploitable:
  - A01 IDOR on payroll
  - A02 XOR decrypt SSN
  - A08 deserialization import
  - A08 Log4j via Kafka
  - chain-01: IDOR → XOR → exfiltration
  - A04: transition bypass (from Phase 2)
- [ ] Verify decoys:
  - `searchEmployees()` (safe) rejects raw injection queries
  - Console print in onboarding service is NOT persisted as audit record
- [ ] Run `mvn test` — all tests pass

## Regular Commits
- [ ] Commit after A03 injection in ES search
- [ ] Commit after A09 missing audit in onboarding
- [ ] Commit after full verification passes

## Phase Status Report
- [ ] Create `phase-03/status-report.md` after completion
