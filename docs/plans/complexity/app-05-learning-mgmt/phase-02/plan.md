# Phase 02: Polyglot Persistence + Core CRUD

## Goal

Migrate all data storage from SQLite auto-created tables to real PostgreSQL migrations with MongoDB document storage for quiz data, while planting an A04 Insecure Design vulnerability in the enrollment flow.

## Scope

### Included
- [ ] Write PostgreSQL migration scripts for `users`, `courses`, `enrollments`, `grades` tables
- [ ] Write MongoDB initialization for `quiz_definitions` and `submissions` collections
- [ ] Migrate all repositories from SQLite queries to PostgreSQL parameterized queries
- [ ] Wire quiz/submission repositories to MongoDB
- [ ] Seed mock data for all tables/collections
- [ ] Verify all 14 endpoints work with real databases
- [ ] Plant A04 insecure enrollment design (trusts client-supplied role + unvalidated course_id)
- [ ] Add decoy: proper enrollment guard on list endpoint (scoped to session user_id, ignores client-supplied role)

### Excluded
- No Kafka changes (Phase 3)
- No UI changes (Phase 4)
- No grading business logic (Phase 3)

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Migration scripts in `src/config/migrations/` | Separation from runtime code; one-time run at container init |
| Seed data in `src/config/seed.py` | Idempotent seeding with `IF NOT EXISTS` guards |
| Repositories use raw SQL with `psycopg2` | Preserves the original pattern from SQLite version — no ORM dependency |
| A04 planted in enrollment controller, not repository | Controller is where the missing validation is most visible; trusts client-supplied `role` and `course_id` without server-side checks |

## Vulnerability Planting

| # | Type | OWASP | CWE | Location | Description | Severity |
|---|------|-------|-----|----------|-------------|----------|
| 1 | Standalone | A04 | CWE-602 | `src/controllers/enrollment_controller.py` → `enroll()` | Enrollment accepts client-supplied `role` parameter and arbitrary `course_id` without server-side validation of course existence, active status, student prerequisites, or role authorization | Medium |

**Source comment**: `# VULNERABILITY A04: Enrollment trusts client-supplied role and course_id without server-side validation`

### Chain-02 Step 1

| Chain | Step | OWASP | CWE | Location | Description | Severity |
|-------|------|-------|-----|----------|-------------|----------|
| chain-02 | 1 | A04 | CWE-602 | `src/controllers/enrollment_controller.py` → `enroll()` | Enrollment accepts attacker-supplied elevated role (e.g., "INSTRUCTOR"), granting unauthorized access to instructor-facing grading endpoints | Low |

**Source comment**: `# CHAIN LINK 1 (chain-02): Enrollment trusts client-supplied role, enabling privilege escalation to instructor access`

## Decoy Patterns

| # | Location | Why it looks vulnerable | Why it is safe |
|---|----------|------------------------|----------------|
| 1 | `src/controllers/enrollment_controller.py` → `list_enrollments()` | Same controller file as vulnerable `enroll()`; appears to expose all enrollments | Scopes query to `session["user_id"]` — only returns the authenticated user's enrollments. Does NOT trust client-supplied `role`. |

## Data Model Changes

### PostgreSQL Tables (migration scripts)

| Table | Columns | Notes |
|-------|---------|-------|
| `users` | `id SERIAL PK, username VARCHAR UNIQUE, password_hash VARCHAR, role VARCHAR, created_at TIMESTAMP` | Student/instructor/admin roles |
| `courses` | `id SERIAL PK, title VARCHAR, description TEXT, instructor_id INT FK, prerequisites JSONB, status VARCHAR` | Prerequisites stored as JSON array of course IDs |
| `enrollments` | `id SERIAL PK, user_id INT FK, course_id INT FK, enrolled_at TIMESTAMP, status VARCHAR` | Unique constraint on (user_id, course_id) |
| `grades` | `id SERIAL PK, user_id INT FK, course_id INT FK, quiz_id INT, score FLOAT, graded_at TIMESTAMP` | Per-quiz scoring |
| `audit_log` | `id SERIAL PK, user_id INT, action VARCHAR, entity_type VARCHAR, entity_id INT, old_value TEXT, new_value TEXT, created_at TIMESTAMP` | Decoy-only: proper audit trail near the un-audited grade write path (Phase 3) |

### MongoDB Collections

| Collection | Document Shape | Purpose |
|------------|---------------|---------|
| `quiz_definitions` | `{ quiz_id, course_id, title, questions: [{ type, prompt, options, answer }], max_score }` | Question bank per course |
| `submissions` | `{ submission_id, quiz_id, user_id, answers: [{ question_id, response }], score, submitted_at }` | Student answer records |

## API Contracts

No new endpoints. Existing endpoints now use real PostgreSQL + MongoDB.

## Artifact Updates

- `src/config/settings.py`: Add MongoDB collection names, table name constants
- `src/config/migrations/001_init.sql`: PostgreSQL schema
- `src/config/seed.py`: Idempotent seed data
- `src/controllers/enrollment_controller.py`: Add A04 weak validation + decoy (already has scoped list)
- `src/repositories/enrollment_repository.py`: Switch to PostgreSQL queries
- `src/repositories/course_repository.py`: Switch to PostgreSQL queries
- `src/repositories/user_repository.py`: Switch to PostgreSQL queries (DECOY-01 preserved)
- `src/repositories/submission_repository.py`: Switch to MongoDB queries
- `.vulns`: Add VULN-04 (A04) + chain-02 components
- `README.md`: Update architecture section for real DB
- `scenarios.md`: Add chain-02 narrative (step 1 only)

## Dependencies on Other Phases

- **Depends on Phase 1**: Real PostgreSQL + MongoDB must be running
- **Phase 3** depends on Phase 2: Data models must exist before adding grading logic
- **Phase 4** depends on Phase 2: Dashboards consume real data
