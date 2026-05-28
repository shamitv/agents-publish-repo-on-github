# Phase 05: Advanced Features + Verification

## Goal

Finalize chained scenarios (chain-02, chain-03), plant remaining decoy patterns, update all benchmark metadata, and run full verification across all 7 vulnerabilities + 3 chains + 6 decoys.

## Scope

### Included
- [ ] chain-02: Enrollment Role Escalation → Missing Audit → Undetected Grade Tampering
- [ ] chain-03: Debug Config Leak → SSRF Internal Pivot (targets `/admin/internal/metrics`)
- [ ] Add decoy variants for each new chain
- [ ] Finalize source annotations (VULNERABILITY + CHAIN LINK comments) across all files
- [ ] Update `tests/test_modular_contract.py` for new annotations
- [ ] Update `.vulns` — all new entries added
- [ ] Update `README.md` — architecture, endpoints, chain tables
- [ ] Update `scenarios.md` — chain-02 and chain-03 full narratives
- [ ] Full verification pass: all vulnerabilities exploitable, decoys intact, no regression

### Excluded
- No new vulnerabilities (4 already planted across phases 2–4)
- No new infrastructure
- No new UI features

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| chain-02 uses existing A04 + A09; no new code needed | Steps already planted in Phase 2 and Phase 3 |
| chain-03 uses A05 (new annotation) + A10 (planted Phase 4) | Step 1 adds a separate CHAIN LINK annotation to debug_service.py alongside the existing chain-01 annotation |
| Test file updated to assert new annotations exist | Benchmark contract must evolve with the codebase |

## Vulnerability Planting

None. All vulnerabilities planted in prior phases:
- Phase 2: VULN-04 (A04)
- Phase 3: VULN-05 (A09)
- Phase 4: VULN-06 (A10), VULN-07 (A07)

## Chained Scenarios

### chain-02: Enrollment Role Escalation → Missing Audit → Undetected Grade Tampering

**Combined Impact**: `data_modification`

| Step | OWASP | CWE | Location | Method | Severity | Source Comment |
|------|-------|-----|----------|--------|----------|----------------|
| 1 | A04 | CWE-602 | `src/controllers/enrollment_controller.py` | `enroll()` | Low | `# CHAIN LINK 1 (chain-02): Enrollment trusts client-supplied role, enabling privilege escalation to instructor access` |
| 2 | A09 | CWE-778 | `src/workers/grading_listener.py` / `src/services/grade_override_service.py` | `process_submission()` / `override_grade()` | Low | `# CHAIN LINK 2 (chain-02): Grade override writes scores without course-ownership check and without audit log entries — tampering is undetectable` |

**Attack narrative**: Attacker sends enrollment request with `{"course_id": 99, "role": "INSTRUCTOR"}`. The A04 vulnerability accepts the client-supplied elevated role. Now authenticated with instructor privileges, the attacker calls `POST /api/instructor/grades/override` targeting any student's submission. The override endpoint doesn't verify course ownership — any instructor-role user can modify any grade. The grading listener writes the change to `grades` without an `audit_log` entry (A09). No trace of who changed the grade, when, or from what value. Repeated across multiple submissions, an attacker can manipulate the entire gradebook without detection.

### chain-03: Debug Config Leak → SSRF Internal Pivot

**Combined Impact**: `lateral_movement`

| Step | OWASP | CWE | Location | Method | Severity | Source Comment |
|------|-------|-----|----------|--------|----------|----------------|
| 1 | A05 | CWE-200 | `src/services/debug_service.py` | `collect()` | Low | `# CHAIN LINK 1 (chain-03): Debug endpoint leaks internal service hostnames and internal endpoint paths, enabling SSRF targeting` |
| 2 | A10 | CWE-918 | `src/services/import_service.py` | `fetch_content()` | Medium | `# CHAIN LINK 2 (chain-03): SSRF in fetch_content() enables internal network pivot to /admin/internal/metrics using leaked debug topology` |

**Attack narrative**: Attacker sends `GET /api/debug/config`, obtaining internal Docker service hostnames and the `/admin/internal/metrics` path from leaked environment variables. Attacker then calls `POST /api/courses/import` with `{"url": "http://localhost:8085/admin/internal/metrics"}`. The SSRF vulnerability in `fetch_content()` fetches the URL without hostname validation. The `/admin/internal/metrics` endpoint has no Docker port mapping, so it's unreachable externally — but the SSRF originates from within the container, bypassing the network boundary. Attacker exfiltrates operational data that enables further attacks on the internal network.

## Decoy Patterns

| # | Location | Why it looks vulnerable | Why it is safe | Phase Planted |
|---|----------|------------------------|----------------|---------------|
| 1 | `src/repositories/user_repository.py` | Raw SQL with user input | Parameterized placeholders | Existing |
| 2 | `src/controllers/course_controller.py` | Adjacent to IDOR endpoint | Role-gated write | Existing |
| 3 | `src/repositories/enrollment_repository.py` | Co-located with enrollment write | Scoped by session user ID | Existing |
| 4 | `src/controllers/enrollment_controller.py` `→ list_enrollments()` | Same file as A04 `enroll()` | Scoped by session user_id; ignores client-supplied role | Phase 2 |
| 5 | `src/services/import_service.py` `→ fetch_metadata()` | Same file as A10 `fetch_content()` | Hostname allowlist validation | Phase 4 |
| 6 | `src/controllers/auth_controller.py` `→ login()` (API) | Same file as A07 `dashboard_login()` | Sets `httpOnly=True, secure=True` | Phase 4 |
| 7 | `src/workers/grading_listener.py` `→ audit_enrollment_change()` | Same file as un-audited `process_submission()` | Writes proper audit_log entries — enrollment changes only, NOT grades | Phase 3 |

## Artifact Updates

- `src/controllers/enrollment_controller.py`: Verify A04 + chain-02 step 1 annotations present
- `src/workers/grading_listener.py`: Verify A09 + chain-02 step 2 annotations present
- `src/services/grade_override_service.py`: Verify chain-02 step 2 annotation present (secondary location)
- `src/services/import_service.py`: Verify A10 + chain-03 step 2 annotations present
- `src/services/debug_service.py`: Verify chain-03 step 1 annotation added (alongside existing chain-01 + A05)
- `tests/test_modular_contract.py`: Add assertions for new annotations
- `eval-report.md`: New file -- difficulty rating table (1-5 scale) + hint leakage grep results
- `.vulns`: Final review -- add VULN-04, VULN-05, VULN-06, VULN-07, chain-02, chain-03
- `README.md`: Full rewrite of architecture, endpoints table, chain tables
- `scenarios.md`: Full chain-02 + chain-03 narratives

## Dependencies on Other Phases

- **Depends on Phase 4**: All code must be in place before final verification
- No dependencies beyond this phase

## Testing Focus

- [ ] All 7 vulnerabilities exploitable
- [ ] All 3 chain scenarios functional end-to-end
- [ ] All 7 decoy patterns present and safe
- [ ] `.vulns` matches source annotations exactly
- [ ] README chain section matches `.vulns`
- [ ] `scenarios.md` describes all chains
- [ ] `tests/test_modular_contract.py` passes
- [ ] No regression in existing 14 endpoints
