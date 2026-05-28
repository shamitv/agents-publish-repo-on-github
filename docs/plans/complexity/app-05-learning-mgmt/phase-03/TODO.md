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

## Grade Override Service
- [ ] Create `src/services/grade_override_service.py`:
  - `override_grade(instructor_id, student_id, quiz_id, new_score)` → updates grade in PostgreSQL
  - Validates instructor role but does NOT verify course ownership
  - Writes to `grades` table but NOT to `audit_log`
- [ ] Wire into `src/routes/instructor_routes.py`: register `POST /api/instructor/grades/override`
- [ ] Source comment: `# CHAIN LINK 2 (chain-02): Grade override writes scores without course-ownership check and without audit log entries`

## A09 Vulnerability — Missing Audit Logging
- [ ] Rewrite `src/workers/grading_listener.py` from 3-line stub to real grading consumer:
  - `process_submission()` — consume grading event, write score to PostgreSQL `grades` table
  - Do NOT write to `audit_log` table
  - Add comment: `# VULNERABILITY A09: Grading listener writes score changes to grades table without audit log entries`
- [ ] Add decoy in same file: `audit_enrollment_change()` method that writes structured entries to `audit_log` table (enrollment changes only, NOT grades)

## Verification
- [ ] Restart app
- [ ] Submit a quiz via `POST /api/submissions`:
  - Verify grading service returns score
- [ ] Enroll in a course with `{"role": "INSTRUCTOR"}`:
  - A04 path should succeed (role escalation via enrollment)
- [ ] Verify A09 vulnerability:
  - Submit a quiz via Kafka → grading listener writes score to `grades` table
  - Check `audit_log` table — no corresponding entry should exist for the grade write
- [ ] Verify chain-02 step 2:
  - Call `POST /api/instructor/grades/override` — grade written without course ownership check
  - Confirm `audit_log` has no entry for the grade change
- [ ] Verify decoy `audit_enrollment_change()`:
  - Enroll in a course → `audit_log` has an audit entry (safe pattern)
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

## Regular Commits
- [ ] Commit after each major task:
  `git add -A && git commit -m "app-05 phase-03: <descriptive message>"`
- [ ] Push to remote after each commit

## Phase Status Report
- [ ] Create `phase-03/status-report.md` after completion:
  - What was implemented
  - Files created (count)
  - Files modified (count)
  - Vulnerabilities planted (type, location)
  - Decoys planted (location)
  - Existing vulns still intact? (yes/no)
  - Chains functional? (yes/no)
  - Tests passing? (yes/no)
  - Blockers
