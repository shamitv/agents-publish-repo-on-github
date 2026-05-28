# Phase 03 TODO — Business Logic + Auto-Grading

## Pre-requisites
- [ ] Phase 2 complete: PostgreSQL + MongoDB seeded with data
- [ ] Read vuln-inventory.md — confirm no-touch files

## Prerequisite Validator
- [ ] Create `src/services/prereq_validator.py`:
  - `validate_prerequisites(user_id, course_id)` → checks `courses.prerequisites` JSONB against completed courses
  - Returns list of missing prerequisite course titles
  - Called by enrollment controller but **not enforced** by the vulnerable path (A04)

## Grading Service
- [ ] Create `src/services/grading_service.py`:
  - `grade_submission(quiz_id, answers)` → fetches quiz from MongoDB, computes score
  - Support question types: multiple-choice (exact match), free-text (keyword match), code-snippet (pattern match stub)
  - Returns `{ score, max_score, per_question_results }`
- [ ] Wire grading into `src/controllers/submission_controller.py` → `submit_quiz()`:
  - Call `grading_service.grade_submission()` before saving submission
  - Store computed score in MongoDB submission document

## Rate Limiter
- [ ] Create `src/services/rate_limiter.py`:
  - `check_rate_limit(user_id, quiz_id, max_attempts=3, window_seconds=300)` → bool
  - In-memory dict tracking attempt timestamps
- [ ] Wire into submission controller: reject submission if rate limit exceeded

## A09 Vulnerability — Missing Audit Logging
- [ ] Edit `src/workers/grading_listener.py`:
  - In `grade_submission()` (or equivalent score-apply method), write score to PostgreSQL grades table
  - Do NOT write to any audit log table
  - Add comment: `# VULNERABILITY A09: Grading listener applies score changes without writing audit log entries`
  - Add comment: `# CHAIN LINK 2 (chain-02): Grading listener silently updates grades without emitting audit events`
  - Add decoy: `print("DEBUG: audit_event_written=OK")` that looks like logging but does nothing

## Verification
- [ ] Restart app
- [ ] Submit a quiz via `POST /api/submissions`:
  - Verify grading service returns score
- [ ] Enroll in a course without prerequisites:
  - A04 path should succeed (no enforcement)
- [ ] Verify A09 vulnerability:
  - Submit a quiz, then check PostgreSQL `grades` table — score is stored
  - Check for any audit log table — should not exist
- [ ] Verify existing vulnerabilities remain exploitable:
  - A01 IDOR: read another user's submission
  - A05 Debug: read secrets
  - A08 Pickle: trigger import via Kafka
  - chain-01: full 3-step chain still works
- [ ] Verify decoys:
  - DECOY-01: login parameterized
  - DECOY-02: course create role-gated
  - DECOY-03: enrollment list scoped
- [ ] Run `tests/test_modular_contract.py`
