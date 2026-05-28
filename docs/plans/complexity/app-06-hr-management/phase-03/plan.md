# Phase 03: Search Injection + Audit Gap

## Goal

Add an A03 Elasticsearch query string injection vulnerability in the employee search client, and an A09 missing-audit-logging vulnerability in the onboarding workflow. Plant decoy safe patterns adjacent to both vulnerable paths.

## Scope

### Included
- [ ] Modify `EmployeeSearchClient.java`: add a raw query concatenation method that enables A03 injection
- [ ] Keep existing safe ES search method as a decoy
- [ ] Add A09 in `OnboardingWorkflowService.java`: state transitions do not write audit log entries
- [ ] Add decoy: stdout print stub that looks like logging but does nothing
- [ ] chain-02 step 2: missing audit on onboarding state change

### Excluded
- No new entities or endpoints
- No UI changes (Phase 4)
- No new infrastructure

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| A03 planted in a NEW search method, not modifying existing safe one | Existing safe method remains as decoy; new method uses string interpolation |
| A09 planted in the same service class as A04 | Vulnerabilities co-located in onboarding workflow create realistic decoy confusion |
| ES injection via query string parameter `?q=` | Matches common real-world Elasticsearch injection patterns |

## Vulnerability Planting

| # | Type | OWASP | CWE | Location | Description | Severity |
|---|------|-------|-----|----------|-------------|----------|
| 1 | Standalone | A03 | CWE-943 | `search/EmployeeSearchClient.java` → `searchEmployeesRaw()` | Search method concatenates user input directly into Elasticsearch query_string syntax via `RestTemplate` | High |
| 2 | Standalone | A09 | CWE-778 | `service/OnboardingWorkflowService.java` → `transition()` | State transition applies status change in PostgreSQL without writing an audit log entry | Medium |

### Chain-02 Step 2

| Chain | Step | OWASP | CWE | Location | Description | Severity |
|-------|------|-------|-----|----------|-------------|----------|
| chain-02 | 2 | A09 | CWE-778 | `service/OnboardingWorkflowService.java` → `transition()` | Onboarding state change persisted without audit log — no record of who bypassed which check | Low |

**Source comments**:
- `// VULNERABILITY A03: Employee search concatenates user input directly into Elasticsearch query_string syntax.`
- `// VULNERABILITY A09: Onboarding state transitions persist without writing audit log entries.`
- `// CHAIN LINK 2 (chain-02): Onboarding state change applied without audit event — no trail of who bypassed Background Check.`

## Decoy Patterns

| # | Location | Why it looks vulnerable | Why it is safe |
|---|----------|------------------------|----------------|
| 1 | `search/EmployeeSearchClient.java` → `searchEmployees()` (existing) | Same class as A03; also takes a query string parameter | Uses Spring Data Elasticsearch or a `NativeSearchQuery` builder with proper parameterization |
| 2 | `service/OnboardingWorkflowService.java` → `transition()` | Same method as A09; has a `System.out.println("AUDIT: transition=" + newState)` statement | Print-to-stdout only — does not write to any database audit table |

## Data Model Changes

None. No new tables or entities.

## API Contracts

No new endpoints. The existing `GET /api/employees?q=` endpoint now routes through the vulnerable search method.

## Artifact Updates

- `src/main/java/com/hr/search/EmployeeSearchClient.java`: Add `searchEmployeesRaw()` with A03
- `src/main/java/com/hr/service/OnboardingWorkflowService.java`: Add A09 annotation + decoy print
- `.vulns`: Add VULN-06 (A03), VULN-07 (A09), chain-02 step 2
- `README.md`: Update description of search functionality
- `scenarios.md`: Complete chain-02 narrative with both steps

## Dependencies on Other Phases

- **Depends on Phase 2**: Onboarding workflow must exist for A09 planting
- **Depends on Phase 1**: Real Elasticsearch must be running for A03 injection
- **Phase 4** depends on Phase 3: All code must be in place for final verification
