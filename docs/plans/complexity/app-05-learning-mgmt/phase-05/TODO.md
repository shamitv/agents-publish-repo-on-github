# Phase 05 TODO — Advanced Features + Verification

## Pre-requisites
- [ ] Phase 4 complete: Kafka streaming + dashboards deployed
- [ ] Read vuln-inventory.md — confirm no-touch files

## Annotation Verification
- [ ] Verify every source file has correct annotation comments:

| File | Must Have |
|------|-----------|
| `src/services/submission_service.py` | `// VULNERABILITY A01`, `// CHAIN LINK 3 (chain-01)` |
| `src/services/debug_service.py` | `// VULNERABILITY A05`, `// CHAIN LINK 1 (chain-01)`, `// CHAIN LINK 1 (chain-03)` |
| `src/services/auth_service.py` | `// CHAIN LINK 2 (chain-01)` |
| `src/workers/import_listener.py` | `// VULNERABILITY A08` |
| `src/controllers/enrollment_controller.py` | `// VULNERABILITY A04`, `// CHAIN LINK 1 (chain-02)` |
| `src/workers/grading_listener.py` | `// VULNERABILITY A09`, `// CHAIN LINK 2 (chain-02)` |
| `src/services/import_service.py` | `// VULNERABILITY A10`, `// CHAIN LINK 2 (chain-03)` |
| `src/controllers/auth_controller.py` | `// VULNERABILITY A07` |

- [ ] Fix any missing or misformatted annotations

## Decoy Verification
- [ ] DECOY-01: `src/repositories/user_repository.py` — confirm parameterized login
- [ ] DECOY-02: `src/controllers/course_controller.py` — confirm role-gated course create
- [ ] DECOY-03: `src/repositories/enrollment_repository.py` — confirm scoped enrollment list
- [ ] DECOY-04: `src/controllers/enrollment_controller.py` `→ list_enrollments()` — confirm scoped
- [ ] DECOY-05: `src/services/import_service.py` `→ fetch_metadata()` — confirm allowlist
- [ ] DECOY-06: `src/controllers/auth_controller.py` `→ login()` — confirm secure cookie flags

## Test File Update
- [ ] Edit `tests/test_modular_contract.py`:
  - Add `self.assertIn("VULNERABILITY A04", source)`
  - Add `self.assertIn("VULNERABILITY A09", source)`
  - Add `self.assertIn("VULNERABILITY A10", source)`
  - Add `self.assertIn("VULNERABILITY A07", source)`
  - Add `self.assertIn("CHAIN LINK 1 (chain-02)", source)`
  - Add `self.assertIn("CHAIN LINK 2 (chain-02)", source)`
  - Add `self.assertIn("CHAIN LINK 2 (chain-03)", source)`
  - Update manifest validation: `self.assertEqual(len(manifest["chained_attacks"]), 3)`
  - Update decoy count: `self.assertGreaterEqual(len(manifest["decoys"]), 6)`

## .vulns Update
- [ ] Add VULN-04 (A04 weak enrollment)
- [ ] Add VULN-05 (A09 missing audit logging)
- [ ] Add VULN-06 (A10 SSRF content import)
- [ ] Add VULN-07 (A07 weak dashboard session)
- [ ] Add chain-02 with 2 components
- [ ] Add chain-03 with 2 components
- [ ] Add decoys 04, 05, 06 to `decoys` array
- [ ] Verify `app_id`, `app_name`, `language`, `framework` unchanged
- [ ] Validate `.vulns` against AGENTS.md JSON schema
- [ ] Confirm `vulnerabilities` array length = 7
- [ ] Confirm `chained_attacks` array length = 3
- [ ] Confirm `decoys` array length = 6

## eval-report.md
- [ ] Create `eval-report.md`:
  - Difficulty rating table for all 7 vulns + 3 chains (1-5 scale with rationale)
  - Hint leakage validation: `rg -n "VULNERABILITY|CHAIN LINK|DECOY" -g "*.{py,html}" -g "!**/.vulns" -g "!**/README.md" -g "!**/scenarios.md" -g "!docs/plans/**"` -- expect zero matches

## README.md Update
- [ ] Update architecture section: real PostgreSQL, MongoDB, Kafka
- [ ] Update API endpoints table: add dashboard routes
- [ ] Add chain-02 table + attack narrative
- [ ] Add chain-03 table + attack narrative
- [ ] Update OWASP coverage summary

## scenarios.md Update
- [ ] Add chain-02 narrative:
  - Step-by-step: enroll without prerequisites → submit quiz → grade applied without audit trail
- [ ] Add chain-03 narrative:
  - Step-by-step: read /api/debug/config for internal topology → submit import URL to internal service → fetch internal data

## Full Verification Pass
- [ ] Start Docker Compose fresh: `docker compose down -v && docker compose up -d`
- [ ] Run app: `python app.py`
- [ ] VULN-01 A01: Read another user's submission → confirm works
- [ ] VULN-02 A05: Read `/api/debug/config` → confirm secrets leaked
- [ ] VULN-03 A08: Publish malicious pickle to Kafka import topic → confirm RCE
- [ ] VULN-04 A04: Enroll in non-existent course → confirm succeeds
- [ ] VULN-05 A09: Submit quiz, check no audit log written → confirm
- [ ] VULN-06 A10: Import URL to `http://localhost:8085/api/debug/config` → confirm fetched
- [ ] VULN-07 A07: Dashboard login → confirm cookie has no `httpOnly` flag
- [ ] chain-01: Debug leak → forge session → read submission → confirm 3 steps work
- [ ] chain-02: Enroll without prereqs → submit quiz → grade applied without audit → confirm
- [ ] chain-03: Read debug config → submit SSRF import → pivot internally → confirm
- [ ] Run `python -m pytest tests/test_modular_contract.py -v` → all pass
- [ ] Confirm no regression in any of the 14 existing API endpoints

## Regular Commits
- [ ] Commit after each major task:
  `git add -A && git commit -m "app-05 phase-05: <descriptive message>"`)
- [ ] Push to remote after each commit

## Phase Status Report
- [ ] Create `phase-05/status-report.md` after completion:
  - What was implemented
  - Files created (count)
  - Files modified (count)
  - Vulnerabilities planted (type, location)
  - Decoys planted (location)
  - Existing vulns still intact? (yes/no)
  - Chains functional? (yes/no)
  - Tests passing? (yes/no)
  - Blockers
