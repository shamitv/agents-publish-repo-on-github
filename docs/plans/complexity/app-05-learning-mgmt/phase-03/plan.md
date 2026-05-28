# Phase 03: Business Logic + Auto-Grading

## Goal

Implement the core LMS business logic — prerequisite course validation, auto-grading engine for multi-question-type quizzes, and submission retry rate limiting — while planting an A09 missing-audit vulnerability in the grading pipeline and chain-02 step 2.

## Scope

### Included
- [ ] `src/services/prereq_validator.py` — check completed prerequisite courses before allowing enrollment or quiz submission
- [ ] `src/services/grading_service.py` — score multiple-choice, free-text, and code-snippet questions
- [ ] `src/services/rate_limiter.py` — limit submission retry frequency per student per quiz
- [ ] Wire grading service into submission controller
- [ ] Plant A09: grading listener applies scores without audit logging
- [ ] Add decoy: logging stub that writes to stdout near the vulnerable consumer
- [ ] chain-02 step 2: grading data-modification without audit trail

### Excluded
- No Kafka changes (Phase 4 — real streaming)
- No UI changes (Phase 4)
- No infrastructure changes

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Grading service is synchronous for now | Simpler to validate; async Kafka grading comes in Phase 4 |
| Rate limiter uses in-memory counters | No Redis dependency yet; resets on app restart (acceptable for benchmark) |
| A09 planted in `src/workers/grading_listener.py` | Follows the existing pattern of VULN-03 (pickle) in a worker file — same directory, same risk profile |

## Vulnerability Planting

| # | Type | OWASP | CWE | Location | Description | Severity |
|---|------|-------|-----|----------|-------------|----------|
| 1 | Standalone | A09 | CWE-778 | `src/workers/grading_listener.py` → `grade_submission()` | Grading listener writes score updates to PostgreSQL without recording audit log entries, enabling undetected grade tampering | Medium |

**Source comment**: `# VULNERABILITY A09: Grading listener applies score changes without writing audit log entries`

### Chain-02 Step 2

| Chain | Step | OWASP | CWE | Location | Description | Severity |
|-------|------|-------|-----|----------|-------------|----------|
| chain-02 | 2 | A09 | CWE-778 | `src/workers/grading_listener.py` → `grade_submission()` | Score changes applied without audit logging — no trail of who changed what grade | Low |

**Source comment**: `# CHAIN LINK 2 (chain-02): Grading listener silently updates grades without emitting audit events`

## Decoy Patterns

| # | Location | Why it looks vulnerable | Why it is safe |
|---|----------|------------------------|----------------|
| 1 | `src/workers/grading_listener.py` → `grade_submission()` | Same file as the vulnerable un-audited path; has a `print()` statement that looks like logging | Print-only — does not write to any structured audit table. This is a **false decoy**: it looks like a mitigation but is actually window dressing. |

## Data Model Changes

- `src/services/prereq_validator.py` — new file, pure logic (no new schema)
- `src/services/grading_service.py` — new file, reads quiz from MongoDB, computes score
- `src/services/rate_limiter.py` — new file, in-memory dict of `(user_id, quiz_id) → [timestamps]`

## API Contracts

No new endpoints. Existing endpoints now use grading services:
- `POST /api/submissions` → submission controller calls `grading_service.grade()` before saving

## Artifact Updates

- `src/services/prereq_validator.py`: New file
- `src/services/grading_service.py`: New file
- `src/services/rate_limiter.py`: New file
- `src/workers/grading_listener.py`: Add A09 annotation + decoy print stub
- `.vulns`: Add VULN-05 (A09) + chain-02 step 2
- `README.md`: Update description to mention auto-grading
- `scenarios.md`: Complete chain-02 narrative with both steps

## Dependencies on Other Phases

- **Depends on Phase 2**: Data models must exist for grading queries
- **Depends on Phase 1**: Kafka stub must be functional for worker communication
- **Phase 4** depends on Phase 3: Grading service exists before Kafka consumer can use it
