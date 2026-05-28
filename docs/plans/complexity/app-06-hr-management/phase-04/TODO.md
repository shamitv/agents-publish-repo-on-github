# Phase 04 TODO — UI Enhancement + Chains + Verification

## Pre-requisites
- [ ] Phase 3 complete: ES injection + audit gap planted
- [ ] Read vuln-inventory.md — confirm no-touch files

## Onboarding UI
- [ ] Edit `src/main/resources/templates/dashboard.html`:
  - Add onboarding pipeline status widget:
    - Count of requests at each state (Draft/Verified/Background Checked/Active)
    - Clickable list of pending requests
    - Uses `/api/onboarding` data via existing JS patterns
- [ ] Create `src/main/resources/templates/onboarding.html`:
  - List all onboarding requests with state badges
  - Transition action buttons (Advance to Verified, Advance to Background Check, etc.)
  - Uses existing Thymeleaf layout patterns from `employees.html`
- [ ] Edit `src/main/java/com/hr/controller/WebController.java`:
  - Add `GET /onboarding` view to serve `onboarding.html`
  - Add comment for chain-03 step 2: `// CHAIN LINK 2 (chain-03): Dashboard session idle timeout is set to 24 hours, enabling prolonged brute-force after credential exposure.`

## Chain-03 Step 2 — Weak Session (A07)
- [ ] In `WebController.java`, ensure the dashboard/onboarding session config has excessively long timeout:
  - If using Spring Security's `sessionManagement()` in `SecurityConfig.java`, set `maximumSessions(1).expiredUrl("/login")` but with a very long idle timeout
  - Alternatively, set `server.servlet.session.timeout=86400` in `application-postgres.properties` (24h)
  - Add annotation explaining this is the vulnerable chain step

## Decoy — Proper Session Config
- [ ] In `src/main/java/com/hr/config/SecurityConfig.java`:
  - Add comment near the `BCryptPasswordEncoder` bean noting that API auth sessions have proper 30-minute timeout
  - Verify the existing security config sets appropriate timeouts for API endpoints

## Test File Update
- [ ] Edit `src/test/java/com/hr/App06ApplicationTests.java`:
  - Add `assertIn` checks for new annotations:
    - `VULNERABILITY A04` — onboarding state bypass
    - `VULNERABILITY A03` — ES injection
    - `VULNERABILITY A09` — missing audit
    - `CHAIN LINK 1 (chain-02)`
    - `CHAIN LINK 2 (chain-02)`
    - `CHAIN LINK 1 (chain-03)`
    - `CHAIN LINK 2 (chain-03)`
  - Update manifest validation:
    - `chained_attacks` length → 3
    - `decoys` length → 7
    - `vulnerabilities` length → 8

## .vulns Update
- [ ] Add VULN-05 (A04 onboarding bypass)
- [ ] Add VULN-06 (A03 ES injection)
- [ ] Add VULN-07 (A09 missing audit)
- [ ] Add VULN-08 (A01 audit endpoint leak — formalized)
- [ ] Add chain-02 with 2 components
- [ ] Add chain-03 with 2 components
- [ ] Update decoys array to include all 7 decoys
- [ ] Verify all entries match source annotations exactly

## README.md Update
- [ ] Update architecture section: PostgreSQL, onboarding pipeline, ES search
- [ ] Update API endpoints table: add onboarding routes
- [ ] Add chain-02 table + attack narrative
- [ ] Add chain-03 table + attack narrative
- [ ] Update OWASP coverage summary (3→7/10)

## scenarios.md Update
- [ ] Add chain-02 narrative:
  - HR admin bypasses Background Check by requesting Active state directly
  - Onboarding state changes without audit trail enabling undetected backdoor
- [ ] Add chain-03 narrative:
  - Attacker reads `GET /api/employees/{id}/audit` for any employee's passwordHash
  - Cracks hash offline (BCrypt but weak/common passwords)
  - Uses 24-hour dashboard session window to brute-force login

## eval-report.md
- [ ] Create `phase-04/eval-report.md`:
  - Difficulty rating table for all 8 vulns + 3 chains (1-5 scale)
  - Hint leakage validation (grep results)
  - Summary of OWASP coverage

## Full Verification Pass
- [ ] Start Docker Compose fresh: `docker compose down -v && docker compose up -d --build`
- [ ] VULN-01 A01: Read another employee's payroll → confirm works
- [ ] VULN-02 A02: Decrypt SSN from payroll response with XOR key → confirm
- [ ] VULN-03 A08: Upload malicious `.ser` file to employee import → confirm RCE
- [ ] VULN-04 A08: Send JNDI payload in Kafka audit event → confirm Log4j trigger
- [ ] VULN-05 A04: Transition Draft→Active directly (skip Background Check) → confirm
- [ ] VULN-06 A03: `GET /api/employees?q=*` → confirm wildcard injection
- [ ] VULN-07 A09: Transition state, check no audit log exists → confirm
- [ ] VULN-08 A01: `GET /api/employees/1/audit` → confirm passwordHash leaked
- [ ] chain-01: Payroll IDOR → XOR decrypt → SSN exfiltration → confirm 2 steps
- [ ] chain-02: Skip Background Check → no audit trail → confirm 2 steps
- [ ] chain-03: Leak passwordHash → weak session → account takeover potential → confirm 2 steps
- [ ] Hint leakage: search source tree for annotation comments outside permit list (use `Select-String -Pattern "VULNERABILITY|CHAIN LINK|DECOY" -Include *.java,*.html,*.properties,*.xml -Recurse` on Windows, or `rg "VULNERABILITY|CHAIN LINK|DECOY" --include "*.java" --include "*.html" --include "*.properties" --include "*.xml"` if ripgrep is available) → zero matches outside permit list
- [ ] Run `mvn test` → all tests pass
- [ ] Confirm no regression in any of the 20 existing endpoints

## Regular Commits
- [ ] Commit after onboarding UI is implemented
- [ ] Commit after chain-03 step 2 planted
- [ ] Commit after metadata updates and verification

## Phase Status Report
- [ ] Create `phase-04/status-report.md` after completion
