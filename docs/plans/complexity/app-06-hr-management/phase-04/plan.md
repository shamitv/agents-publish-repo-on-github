# Phase 04: UI Enhancement + Chains + Verification

## Goal

Add onboarding pipeline visualization to the existing dashboard UI, finalize chain-02 and chain-03 scenarios with decoy placements, seed chain-03 step 2 (weak session), update all benchmark metadata, and run full verification across all 8 vulnerabilities + 3 chains + 5 decoys.

## Scope

### Included
- [ ] Add onboarding pipeline status widget to `dashboard.html`
- [ ] Add onboarding management page to UI
- [ ] chain-03 step 2: plant A07 weak session configuration in a dashboard path
- [ ] Add decoy for chain-03: proper session config on API auth path
- [ ] Finalize all source annotations across all files
- [ ] Update `tests/App06ApplicationTests.java` for new annotations
- [ ] Update `.vulns` — all new entries added
- [ ] Update `README.md` — architecture, endpoints, chain tables
- [ ] Update `scenarios.md` — chain-02 and chain-03 full narratives
- [ ] Create `eval-report.md` with difficulty ratings + hint leakage check
- [ ] Full verification pass

### Excluded
- No new standalone vulnerabilities (4 already planted across phases 2–3)
- No new infrastructure

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| chain-03 step 2 uses weak session timeout | Short idle timeout (e.g., 60 seconds) in the dashboard web path makes brute-force more feasible after password hash leak |
| Onboarding UI added as Thymeleaf fragment | Leverages existing Thymeleaf templates; no new frontend framework |
| Session vuln planted in WebController (dashboard) only | API endpoints retain proper session config as decoy |

## Vulnerability Planting

None new. All vulnerabilities planted in prior phases:
- Phase 2: VULN-05 (A04), VULN-08 (formalized A01)
- Phase 3: VULN-06 (A03), VULN-07 (A09)

### Chain-03 Step 2 (A07)

| Chain | Step | OWASP | CWE | Location | Description | Severity |
|-------|------|-------|-----|----------|-------------|----------|
| chain-03 | 2 | A07 | CWE-613 | `controller/WebController.java` → `dashboard()` | Dashboard session has excessively long idle timeout (e.g., 86400s = 24h), enabling session brute-force after password hash crack | Low |

**Source comment**: `// CHAIN LINK 2 (chain-03): Dashboard session idle timeout is set to 24 hours, enabling prolonged brute-force after credential exposure.`

## Chained Scenarios

### chain-02: Onboarding State Bypass → Missing Audit → Data Modification

**Combined Impact**: `data_modification`

| Step | OWASP | CWE | Location | Method | Severity | Source Comment |
|------|-------|-----|----------|--------|----------|----------------|
| 1 | A04 | CWE-602 | `service/OnboardingWorkflowService.java` | `transition()` | Low | `// CHAIN LINK 1 (chain-02): State machine allows bypassing Background Check by requesting Active directly.` |
| 2 | A09 | CWE-778 | `service/OnboardingWorkflowService.java` | `transition()` | Low | `// CHAIN LINK 2 (chain-02): Onboarding state change applied without audit event — no trail of who bypassed Background Check.` |

### chain-03: Password Hash Leak → Weak Session → Account Takeover

**Combined Impact**: `account_takeover`

| Step | OWASP | CWE | Location | Method | Severity | Source Comment |
|------|-------|-----|----------|--------|----------|----------------|
| 1 | A01 | CWE-639 | `controller/EmployeeController.java` | `getEmployeeAudit()` | Low | `// CHAIN LINK 1 (chain-03): Employee audit endpoint returns passwordHash for any employee by ID without authorization.` |
| 2 | A07 | CWE-613 | `controller/WebController.java` | `dashboard()` | Low | `// CHAIN LINK 2 (chain-03): Dashboard session idle timeout is set to 24 hours, enabling prolonged brute-force after credential exposure.` |

## Decoy Patterns

| # | Location | Why it looks vulnerable | Why it is safe | Phase |
|---|----------|------------------------|----------------|-------|
| 1 | `config/SecurityConfig.java` | BCryptPasswordEncoder | Proper hashing | Existing |
| 2 | `repository/EmployeeRepository.java` | Spring Data JPA | Parameterized queries | Existing |
| 3 | `controller/PayrollController.java` | Same controller as IDOR | Role-gated report | Existing |
| 4 | `controller/OnboardingController.java` → `listOnboardingRequests()` | Same controller as A04 | Scoped by creator | Phase 2 |
| 5 | `controller/EmployeeController.java` → `getEmployee()` | Same controller as audit leak | Role/ownership gated | Phase 2 |
| 6 | `search/EmployeeSearchClient.java` → `searchEmployees()` | Same class as A03 | Proper query builder | Phase 3 |
| 7 | `config/SecurityConfig.java` → API security config | Session can be configured | Proper 30-min timeout set for API | Phase 4 |

## Artifact Updates

- `src/main/resources/templates/dashboard.html`: Add onboarding status widget
- `src/main/resources/templates/onboarding.html`: New page
- `src/main/java/com/hr/controller/WebController.java`: Add `onboarding()` view + chain-03 step 2 annotation
- `src/main/java/com/hr/config/SecurityConfig.java`: Add decoy session config comment for API
- `tests/App06ApplicationTests.java`: Update for new annotation presence
- `.vulns`: Add chain-03 step 2, update chain entries
- `README.md`: Full rewrite of architecture, endpoints table, chain tables
- `scenarios.md`: Complete chain-02 + chain-03 narratives
- `eval-report.md`: New file — difficulty ratings + hint leakage validation

## Dependencies on Other Phases

- **Depends on Phase 3**: All code in place for final verification
- No dependencies beyond this phase

## Testing Focus

- [ ] All 8 vulnerabilities exploitable
- [ ] All 3 chain scenarios functional end-to-end
- [ ] All 7 decoy patterns present and safe
- [ ] `.vulns` matches source annotations exactly
- [ ] README chain section matches `.vulns`
- [ ] `scenarios.md` describes all chains
- [ ] `tests/App06ApplicationTests.java` passes
- [ ] Hint leakage check passes (zero matches outside permit list)
- [ ] No regression in any of the 20 existing endpoints
