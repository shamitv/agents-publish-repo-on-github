# Phase 03: Business Logic + Auto-Grading

## Goal

Implement the core LMS business logic — prerequisite course validation, auto-grading engine for multi-question-type quizzes, and submission retry rate limiting — while planting an A09 missing-audit vulnerability in the grading pipeline and chain-02 step 2.

## Scope

### Included
- [ ] `src/services/prereq_validator.py` — check prerequisite completion (used by the safe enrollment path; ignored by the A04 vulnerable path)
- [ ] `src/services/grading_service.py` — multi-question-type auto-grading engine
- [ ] `src/services/rate_limiter.py` — submission retry throttle per student per quiz
- [ ] `src/services/grade_override_service.py` — instructor manual grade adjustment with weak authorization (chain-02 write vector)
- [ ] Wire grading service into submission flow: grade on submit, write to `grades` table
- [ ] Add `POST /api/instructor/grades/override` endpoint
- [ ] Plant A09: grading listener writes scores to `grades` without writing to `audit_log`
- [ ] Plant chain-02 step 2: grade override lacks course-ownership check + missing audit trail
- [ ] Add decoy: `audit_enrollment_change()` method in grading_listener.py — writes proper audit entries to `audit_log` table (enrollment changes only, not grades)

### Excluded
- No Kafka changes (Phase 4 — real streaming)
- No UI changes (Phase 4)
- No infrastructure changes

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Grading service is synchronous for now | Simpler to validate; async Kafka grading comes in Phase 4 |
| Rate limiter uses in-memory counters | No Redis dependency yet; resets on app restart (acceptable for benchmark) |
| A09 planted in `src/workers/grading_listener.py` | Follows the existing pattern of VULN-03 (pickle) in a worker file — same directory, same risk profile. The current stub is 3 lines; real grading code must be added first for the vuln to be meaningful. |
| Grade override in `src/services/grade_override_service.py` | Separate service for chain-02 step 2 — validates instructor role but does NOT verify course ownership, enabling cross-course grade tampering |

## Vulnerability Planting

| # | Type | OWASP | CWE | Location | Description | Severity |
|---|------|-------|-----|----------|-------------|----------|
| 1 | Standalone | A09 | CWE-778 | `src/workers/grading_listener.py` → `process_submission()` | Grading listener writes score to `grades` table but does NOT write to `audit_log`. No record exists of who changed what grade or when. | Medium |

**Source comment**: `# VULNERABILITY A09: Grading listener writes score changes to grades table without audit log entries`

### Chain-02 Step 2

| Chain | Step | OWASP | CWE | Location | Description | Severity |
|-------|------|-------|-----|----------|-------------|----------|
| chain-02 | 2 | A09 | CWE-778 | `src/services/grade_override_service.py` → `override_grade()` | Grade override endpoint validates INSTRUCTOR role but does NOT check course ownership — any instructor can modify any student's grade. Combined with missing audit trail, tampering is untraceable. | Medium |

**Source comment**: `# CHAIN LINK 2 (chain-02): Grade override writes scores without course-ownership check and without audit log entries — tampering is undetectable`

## Decoy Patterns

| # | Location | Why it looks vulnerable | Why it is safe |
|---|----------|------------------------|----------------|
| 1 | `src/workers/grading_listener.py` → `audit_enrollment_change()` | Same file as un-audited `process_submission()`; looks like it handles all audit events | Writes proper structured audit entries with user_id, timestamp, old/new value pairs to `audit_log` — only for enrollment changes, not grades |

## Data Model Changes

- `src/services/prereq_validator.py` — new file, pure logic (no new schema)
- `src/services/grading_service.py` — new file, reads quiz from MongoDB, computes score
- `src/services/rate_limiter.py` — new file, in-memory dict of `(user_id, quiz_id) → [timestamps]`

## API Contracts

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/instructor/grades/override` | Instructor+ | Override a student's grade — no course ownership verification (vulnerable, chain-02 write vector) |

Existing endpoints now use grading services:
- `POST /api/submissions` → submission controller calls `grading_service.grade()` before saving

## Artifact Updates

- `src/services/prereq_validator.py`: New file
- `src/services/grading_service.py`: New file
- `src/services/rate_limiter.py`: New file
- `src/services/grade_override_service.py`: New file (chain-02 step 2 location)
- `src/workers/grading_listener.py`: Rewrite from 3-line stub to real grading consumer — add A09 annotation + decoy `audit_enrollment_change()` method
- `src/routes/instructor_routes.py`: Add `/api/instructor/grades/override` route
- `.vulns`: Add VULN-05 (A09) + chain-02 step 2
- `README.md`: Update description to mention auto-grading and grade override
- `scenarios.md`: Complete chain-02 narrative with both steps

## Dependencies on Other Phases

- **Depends on Phase 2**: Data models must exist for grading queries
- **Depends on Phase 1**: Kafka connection config is available (real `kafka-python` imports); workers use the transport abstraction layer; full topic wiring happens in Phase 4
- **Phase 4** depends on Phase 3: Grading service exists before Kafka consumer can use it
