# Phase 02 TODO — Polyglot Persistence + Core CRUD

## Pre-requisites
- [ ] Phase 1 complete: Docker Compose running, real PostgreSQL + MongoDB accepting connections
- [ ] Read vuln-inventory.md — confirm no-touch files
- [ ] Read expansion-plan.md — confirm phase scope

## PostgreSQL Migration Scripts
- [ ] Create `src/config/migrations/` directory
- [ ] Write `src/config/migrations/001_init.sql`:
  - `CREATE TABLE IF NOT EXISTS users (...)`
  - `CREATE TABLE IF NOT EXISTS courses (...)`
  - `CREATE TABLE IF NOT EXISTS enrollments (...)`
  - `CREATE TABLE IF NOT EXISTS grades (...)`
- [ ] Write `src/config/migrations/run.py` — reads and executes SQL files in order

## MongoDB Initialization
- [ ] Write `src/config/mongo_init.py` — creates `quiz_definitions` and `submissions` collections with indexes
- [ ] Verify `pymongo` client connects and creates collections

## Seed Data
- [ ] Write `src/config/seed.py`:
  - Insert mock users (student_alice, instructor_bob, admin_charlie)
  - Insert mock courses with prerequisites
  - Insert mock quiz definitions in MongoDB
  - Insert seed enrollments
- [ ] Seed script must be idempotent (check-then-insert)

## Repository Migration — PostgreSQL
- [ ] Edit `src/repositories/user_repository.py`: switch from SQLite to `psycopg2` pool
  - Preserve parameterized login query (DECOY-01) verbatim
- [ ] Edit `src/repositories/course_repository.py`: switch to PostgreSQL
- [ ] Edit `src/repositories/enrollment_repository.py`: switch to PostgreSQL
  - Preserve scoped list query (DECOY-03) verbatim

## Repository Migration — MongoDB
- [ ] Edit `src/repositories/submission_repository.py`: switch from in-memory dict to `pymongo` collection
  - `get_submission()`: query by submission_id
  - `save_submission()`: insert document

## A04 Vulnerability — Weak Enrollment
- [ ] Edit `src/controllers/enrollment_controller.py`:
  - In `enroll()`, accept enrollment without checking course existence, active status, or prerequisites
  - Add comment: `# VULNERABILITY A04: Enrollment accepts course_id without verifying course exists, is active, or student meets prerequisites`
  - Add comment: `# CHAIN LINK 1 (chain-02): Enrollment accepts arbitrary course_id without prerequisite or existence checks`
- [ ] Verify `list_enrollments()` still scopes by `session["user_id"]` (DECOY-03 preserved)

## Config Tuning
- [ ] Update `src/config/settings.py`: add MongoDB collection names, migration paths
- [ ] Ensure `app.py` or `src/main.py` runs migration + seed on startup

## Verification
- [ ] Restart Docker Compose and app
- [ ] Verify all 14 endpoints respond correctly with real data:
  - `POST /api/auth/login` reads from real PostgreSQL
  - `GET /api/courses` reads from real PostgreSQL
  - `POST /api/enrollments` accepts enrollment into non-existent course (A04)
  - `GET /api/submissions/2` reads from real MongoDB
- [ ] Verify A04 vulnerability:
  - Enroll in a non-existent course ID → should succeed
  - Enroll in a course without prerequisites → should succeed
- [ ] Verify existing vulnerabilities remain exploitable:
  - A01 IDOR: read another user's submission via `/api/submissions/{id}`
  - A05 Debug: read secrets from `/api/debug/config`
  - A08 Pickle: trigger via Kafka import topic
- [ ] Verify chain-01 still functional:
  - Debug leak → session forge → submission read
- [ ] Verify decoys:
  - DECOY-01: login still parameterized
  - DECOY-02: course creation still role-gated
  - DECOY-03: enrollment list still scoped
- [ ] Run `tests/test_modular_contract.py`

## Regular Commits
- [ ] Commit after each major task:
  `git add -A && git commit -m "app-05 phase-02: <descriptive message>"`
- [ ] Push to remote after each commit

## Phase Status Report
- [ ] Create `phase-02/status-report.md` after completion:
  - What was implemented
  - Files created (count)
  - Files modified (count)
  - Vulnerabilities planted (type, location)
  - Decoys planted (location)
  - Existing vulns still intact? (yes/no)
  - Chains functional? (yes/no)
  - Tests passing? (yes/no)
  - Blockers
