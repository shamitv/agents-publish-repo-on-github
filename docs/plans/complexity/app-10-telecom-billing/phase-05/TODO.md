# Phase 05 TODO — Evaluation (Difficulty + Hint Leakage)

## Pre-requisites
- [ ] Phase 04 complete — all tests pass, Docker verified, master index updated

## Difficulty Assessment

- [ ] Rate VULN-01 (A03 SQLi UsageController) → 2 (Easy)
- [ ] Rate VULN-02 (A04 Payment design) → 1 (Trivial)
- [ ] Rate VULN-03 (A01 Weak admin auth) → 2 (Easy)
- [ ] Rate VULN-04 (A04 Unvalidated rate) → 1 (Trivial)
- [ ] Rate VULN-05 (A09 Missing audit balance) → 3 (Moderate)
- [ ] Rate VULN-06 (A05 Health info leak) → 1 (Trivial)
- [ ] Rate VULN-07 (A01 Invoice IDOR) → 1 (Trivial)
- [ ] Rate VULN-08 (A09 Missing audit invoices) → 3 (Moderate)
- [ ] Rate chain-01 (single-file, 3 steps) → 2 (Easy)
- [ ] Rate chain-02 (multi-component, 4 files, 3 layers) → 4 (Hard)

## Hint Leakage Validation

- [ ] Scan 1 — annotation keywords in `.java`:
  ```powershell
  rg -n "VULNERABILITY|CHAIN LINK" apps/java/app-10-telecom-billing/src/main -g "*.java"
  ```
  Expected: 16 matches across 5 files — ALL inside `// VULNERABILITY` or `// CHAIN LINK` comment lines
  - [ ] AdminController.java: 8 (5 VULNERABILITY + 3 CHAIN LINK)
  - [ ] UsageController.java: 2 (1 VULNERABILITY + 1 CHAIN LINK)
  - [ ] PaymentService.java: 1 (1 VULNERABILITY)
  - [ ] HealthService.java: 1 (1 VULNERABILITY)
  - [ ] BillingController.java: 2 (1 VULNERABILITY + 1 CHAIN LINK)
  - [ ] BillingService.java: 2 (1 VULNERABILITY + 1 CHAIN LINK)

- [ ] Scan 2 — non-annotation hint words in `.java`:
  ```powershell
  rg -in "intentional vuln|benchmark|vulnerab|chain attack|exploit scenario" apps/java/app-10-telecom-billing/src/main -g "*.java"
  ```
  Expected: Only matches inside `VULNERABILITY` / `CHAIN LINK` annotations (permitted) or ZERO outside annotations
  - [ ] Verify each match is on a line containing `// VULNERABILITY` or `// CHAIN LINK`

- [ ] Scan 3 — test files:
  ```powershell
  rg -in "vulnerab|OWASP|chain|exploit" apps/java/app-10-telecom-billing/src/test -g "*.java"
  ```
  Expected: Matches in test assertion strings — permitted (tests check annotation presence)
  - [ ] Confirm all matches are in test method assertion strings, not in test comments

- [ ] Scan 4 — config/docker/build files:
  ```powershell
  rg -n "VULNERABILITY|CHAIN LINK" apps/java/app-10-telecom-billing -g "*.{yml,xml,properties}" -g "Dockerfile"
  ```
  Expected: ZERO matches

- [ ] Scan 5 — `.vulns` JSON validity:
  ```powershell
  # Manual inspection: no trailing commas, balanced braces, all required fields present
  # Verify chained_attacks has 2 entries (chain-01 + chain-02)
  # Verify vulnerabilities has 8 entries
  # Verify decoys has 5 entries
  ```

- [ ] Scan 6 — README.md / scenarios.md:
  ```powershell
  rg "VULNERABILITY|CHAIN LINK" apps/java/app-10-telecom-billing -g "*.md"
  ```
  Expected: Matches in README chain sections and scenarios.md — permitted (these are designated metadata files)

## eval-report.md

- [ ] Create `docs/plans/complexity/app-10-telecom-billing/eval-report.md`
- [ ] Difficulty Assessment section:
  - 10-row table (8 vulns + 2 chains) with ID, OWASP, location, difficulty, rationale
- [ ] Hint Leakage Validation section:
  - 6-row table with search scope, files scanned, matches, status
  - Final line: "ZERO matches outside the permit list. No hint leakage detected."
- [ ] OWASP Coverage Summary:
  - Before: A01, A03, A04, A09 (4 categories)
  - After: A01, A03, A04, A05, A09 (5 categories)
  - Uncovered: A02, A06, A07, A08, A10
- [ ] Exploit Complexity Summary:
  - chain-01 difficulty: 2 → chain-02 difficulty: 4
  - Files per chain: 1 → 4
  - Layers per chain: 1 (controller) → 3 (controller, service, messaging)

## Status Reports

- [ ] Create `phase-01/status-report.md`:
  - Summary: Inventory complete. 4 plan files created. 0 vulns planted. OWASP gaps identified.
  - Files created: 4 (README.md, expansion-plan.md, vuln-inventory.md, eval-report.md placeholder)
  - Files modified: 0
  - Tests passing: N/A (docs only)

- [ ] Create `phase-02/status-report.md`:
  - Summary: A05 annotation added to HealthService. 1 new standalone vuln. 1 new decoy.
  - Files created: 0
  - Files modified: 2 (HealthService.java, .vulns)
  - New vulnerabilities: 1 (A05)
  - New decoys: 1
  - Existing vulns intact: YES
  - Tests passing: 5/5

- [ ] Create `phase-03/status-report.md`:
  - Summary: Chain-02 annotations added across 3 source files. 2 new standalone vulns. 1 new chain. 2 new decoys.
  - Files created: 0
  - Files modified: 6 (UsageController.java, BillingController.java, BillingService.java, .vulns, README.md, scenarios.md)
  - New vulnerabilities: 2 (A01 IDOR, A09 audit bypass)
  - New chains: 1 (chain-02, 3 steps, 4 components, difficulty 4)
  - New decoys: 2
  - Existing vulns intact: YES
  - Chains functional: YES (chain-01 + chain-02 both exploitable)
  - Tests passing: 5/5

- [ ] Create `phase-04/status-report.md`:
  - Summary: Verification complete. 2 new tests added. Docker smoke passed. Master index updated.
  - Files modified: 2 (App10ApplicationTests.java, docs/plans/complexity/README.md)
  - Tests passing: 7/7
  - Docker: 4/4 services healthy, chain-02 exploitable end-to-end
  - Master index: Updated from "Pending" to "Implemented"

- [ ] Create `phase-05/status-report.md`:
  - Summary: Evaluation complete. Difficulty ratings assigned. Hint leakage validated — ZERO leaks.
  - Difficulty range: 1 (Trivial) to 4 (Hard)
  - Hint leakage: 6 scans run, 0 violations outside permit list
  - OWASP coverage: 5/10 categories
  - Status: All 5 phases complete

## Final Verification

- [ ] Run `mvn test` — all 7 tests pass
- [ ] Verify all plan artifacts present:
  ```
  Get-ChildItem -Recurse docs/plans/complexity/app-10-telecom-billing/ -Name
  ```
  Expected: 17 files total:
  - 1 README.md (app-level)
  - 1 expansion-plan.md
  - 1 vuln-inventory.md
  - 1 eval-report.md
  - phase-01: plan.md + TODO.md + status-report.md (3)
  - phase-02: plan.md + TODO.md + status-report.md (3)
  - phase-03: plan.md + TODO.md + status-report.md (3)
  - phase-04: plan.md + TODO.md + status-report.md (3)
  - phase-05: plan.md + TODO.md + status-report.md (3)

## Commit
- [ ] `git add -A && git commit -m "eval(app-10): complete difficulty ratings, hint leakage validation, and all phase status reports"`
