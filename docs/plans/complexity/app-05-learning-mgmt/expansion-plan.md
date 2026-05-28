# App 05 (learning-mgmt) — Complexity Upgrade Expansion Plan

## Overview

Upgrade the Online Learning Management System from a stub-backed Flask application (SQLite, in-memory Kafka emulation, mock MongoDB) to a Docker-orchestrated, enterprise-grade polyglot system with real PostgreSQL, MongoDB, Apache Kafka, auto-grading business logic, and instructor/student portal dashboards.

**Current app**: Python/Flask, 37 source files, 14 endpoints, 3 standalone vulns, 1 chained scenario
**Target app**: Same 14 endpoints upgraded to real DB/Kafka + new grading pipeline + 2 new dashboards, ~55–65 source files

> **Non-goals / Constraints**
> - Do **not** remove or fix any intentionally planted vulnerability listed in [vuln-inventory.md](./vuln-inventory.md).
> - Add new code with realistic patterns, including **decoy safe code** near vulnerable-looking code.
> - Add 1–2 new standalone vulnerabilities per phase, plus new chained scenarios.
> - Update `.vulns`, `README.md`, `scenarios.md` after each phase.
> - Avoid introducing real external network dependencies beyond Docker Compose.

---

## Current State

| Property | Value |
|----------|-------|
| App ID | `app-05` |
| Language | Python |
| Framework | Flask |
| Current structure | Modular `src/` with controllers, services, repositories, routes, config, workers |
| Standalone vulns | 3 (A01 IDOR, A05 Debug Leak, A08 Pickle RCE) |
| Chain scenarios | 1 (chain-01: Debug Leak → Session Forgery → IDOR Exfiltration) |
| Decoys | 3 (parameterized login, role-gated course create, scoped enrollment list) |
| OWASP gaps | A03, A04, A06, A07, A09, A10 uncovered |
| Test suite | `tests/test_modular_contract.py` validates endpoint contract + annotation presence |

---

## Architecture Changes

### 1) Infrastructure — replace stubs with real services

| Component | Current (stub) | Target (real) |
|-----------|---------------|---------------|
| Primary DB | SQLite (`db_sql.py`) | PostgreSQL 15 via `psycopg2-binary` |
| Document store | In-memory mock (`db_mongo.py`) | MongoDB 6 via `pymongo` |
| Event broker | Python-thread-based queue emulation (`kafka_client.py`) | Apache Kafka via `kafka-python` |
| Orchestration | Manual | `docker-compose.yml` with healthchecks |

### 2) Existing code preserved verbatim

All existing source files, vulnerability annotations, and benchmark metadata stay in place. The migration touches only config files and the `src/config/` layer — controllers, services, routes remain intact.

### 3) New business logic modules

- `src/services/prereq_validator.py` — prerequisite course completion checks
- `src/services/grading_service.py` — multi-question-type auto-grading engine
- `src/services/rate_limiter.py` — submission retry throttling

### 4) New UI dashboards

Static HTML/JS dashboards served by Flask:
- **Student View** — gradebook, active courses, enrollment status
- **Instructor View** — quiz builder, grading queue console, student list

### 5) Extend vulnerability surface to 7/10 OWASP categories

| Phase | New OWASP | Rationale |
|-------|-----------|-----------|
| 2 | A04 — Insecure Design | Weak enrollment validation in the enrollment migration |
| 3 | A09 — Security Logging & Monitoring | Grading pipeline applies score changes without audit trail |
| 4 | A10 — SSRF | Course content import fetches user-supplied URLs |
| 4 | A07 — Identification & Auth Failures | Dashboard session cookie missing `httpOnly`/`secure` flags |

---

## Vulnerability Planting Strategy

### Per-Phase Summary

| Phase | Standalone Vulns Added | Chain Additions | Decoy Patterns |
|-------|-----------------------|-----------------|----------------|
| 1 | — | — | — |
| 2 | 1 (A04) | chain-02 step 1 | Proper enrollment guard on list endpoint |
| 3 | 1 (A09) | chain-02 step 2 | Logging stub that writes to stdout near vulnerable consumer |
| 4 | 2 (A10, A07) | chain-03 step 2 | URL allowlist on import GET; proper session config on auth |
| 5 | — | chain-03 step 1 (uses existing A05) | Decoy enrollment validation variant |

**Total new**: 4 standalone vulnerabilities, 2 new chain scenarios
**OWASP coverage after expansion**: A01, A02 (chain), A04, A05, A07, A08, A09, A10 — 8/10 covered

---

## Feature Inventory by Phase

### Phase 1 — Infrastructure + Docker Compose
- [ ] `docker-compose.yml` with PostgreSQL 15, MongoDB 6, ZooKeeper, Kafka
- [ ] Healthcheck wait scripts for all services
- [ ] Switch `src/config/db_sql.py` from SQLite to `psycopg2` PostgreSQL connection pool
- [ ] Switch `src/config/db_mongo.py` from mock to `pymongo` real client
- [ ] Switch `src/config/kafka_client.py` from thread-queue stub to `kafka-python` producer/consumer
- [ ] Update `requirements.txt` with `psycopg2-binary`, `pymongo`, `kafka-python`
- [ ] Verify existing endpoints still respond after config swap
- [ ] Preserve all existing vulnerability annotations verbatim

### Phase 2 — Polyglot Persistence + Core CRUD
- [ ] PostgreSQL schema migration scripts (`users`, `courses`, `enrollments`)
- [ ] MongoDB document initialization (quiz definitions, submission answers)
- [ ] Migrate all repositories from SQLite queries to PostgreSQL
- [ ] Wire quiz/submission repositories to MongoDB
- [ ] Seed data for all tables
- [ ] Verify all 14 endpoints work with real databases
- [ ] Plant A04 vulnerability in enrollment flow
- [ ] Add decoy: proper enrollment validation on list endpoint

### Phase 3 — Business Logic + Auto-Grading
- [ ] `src/services/prereq_validator.py` — prerequisite completion checker
- [ ] `src/services/grading_service.py` — multi-question-type scoring engine
- [ ] `src/services/rate_limiter.py` — submission retry throttle
- [ ] Wire grading service into submission flow
- [ ] Plant A09 vulnerability in grading listener
- [ ] Add decoy: logging stub near vulnerable consumer

### Phase 4 — Real Kafka Streaming + Enterprise UI
- [ ] Real `KafkaProducer` in `src/config/kafka_client.py`
- [ ] Wire submission controller to emit grading events to `grading` topic
- [ ] Real `KafkaConsumer` in `GradingListener` worker
- [ ] Real `KafkaConsumer` in `ImportListener` worker (pickle RCE preserved)
- [ ] Student dashboard: gradebook, active courses, enrollment
- [ ] Instructor dashboard: quiz builder, grading queue
- [ ] Plant A10 (SSRF in content import) and A07 (weak session cookies on dashboard)
- [ ] Add decoys: URL allowlist on import GET, proper session config on auth

### Phase 5 — Advanced Features + Verification
- [ ] chain-02 scenario: Weak Enrollment → Missing Audit → Unlogged Grade Change
- [ ] chain-03 scenario: Debug Config Leak → SSRF Internal Pivot
- [ ] Add decoy variants for all new chains
- [ ] Update `tests/test_modular_contract.py` for new annotations
- [ ] Update `.vulns` — add VULN-04 (A04), VULN-05 (A09), VULN-06 (A10), VULN-07 (A07) + chain-02, chain-03
- [ ] Update `README.md` — architecture, endpoints, chain tables
- [ ] Update `scenarios.md` — chain-02 and chain-03 narratives

---

## Data Model Changes

### New PostgreSQL Tables (beyond existing SQLite schema)

| Table | Columns | Purpose |
|-------|---------|---------|
| `users` | id, username, password_hash, role (student/instructor/admin), created_at | Auth profiles |
| `courses` | id, title, description, instructor_id, prerequisites (JSON), status | Course metadata |
| `enrollments` | id, user_id, course_id, enrolled_at, status | Enrollment records |
| `grades` | id, user_id, course_id, quiz_id, score, graded_at | Grading results |

### New MongoDB Collections

| Collection | Documents | Purpose |
|------------|-----------|---------|
| `quiz_definitions` | `{ quiz_id, course_id, questions: [{ type, prompt, options, answer }], max_score }` | Quiz configurations |
| `submissions` | `{ submission_id, quiz_id, user_id, answers: [], score, submitted_at }` | Student answer records |

---

## API Endpoint Inventory

All 14 existing endpoints preserved; new dashboards served via static routes:

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/login` | No | Authenticate |
| POST | `/api/auth/logout` | Yes | End session |
| GET | `/api/auth/me` | Yes | Current user info |
| GET | `/api/health` | No | Health check |
| GET | `/api/courses` | No | List/search courses |
| POST | `/api/courses` | Instructor+ | Create course |
| POST | `/api/courses/import` | Instructor+ | Import course from file/URL |
| GET | `/api/enrollments` | Yes | List user enrollments |
| POST | `/api/enrollments` | Yes | Enroll in course |
| GET | `/api/submissions/<id>` | Yes | Get submission |
| POST | `/api/submissions` | Yes | Submit quiz answers |
| GET | `/api/debug/config` | No | **Vulnerable**: leaks secrets |
| GET | `/api/instructor/courses` | Instructor+ | Instructor's courses |
| GET | `/api/instructor/submissions/<quiz_id>` | Instructor+ | Submissions for a quiz |
| GET | `/dashboard/student` | Student | Student portal UI |
| GET | `/dashboard/instructor` | Instructor+ | Instructor portal UI |

---

## Security Benchmark Considerations

- Keep existing benchmark vulnerabilities intact — refer to [vuln-inventory.md](./vuln-inventory.md) before every code change.
- Each phase adds decoy safe patterns near vulnerable-looking code:
  - Phase 2: Proper enrollment validation on list endpoint near weak validation
  - Phase 3: Logging stdout stub near un-audited grading consumer
  - Phase 4: URL allowlist on import GET near SSRF; proper session config on auth
  - Phase 5: Additional decoy variants for chain steps
- New code includes realistic "looks vulnerable" areas without removing existing benchmark vulnerabilities.

---

## Testing Plan

- **Unit tests**: Extend `test_modular_contract.py` for new annotations and endpoints
- **Integration tests**: Verify all endpoints work with real PostgreSQL + MongoDB + Kafka
- **Security checks** (run after every phase):
  - Existing vulnerabilities remain exploitable
  - New vulnerabilities are exploitable
  - Decoy safe patterns exist near vulnerable-looking code
  - `.vulns`, `README.md`, `scenarios.md` are up to date

---

## Deliverables Checklist

- [x] Vuln inventory documented ([vuln-inventory.md](./vuln-inventory.md))
- [x] Expansion plan (this document)
- [ ] Phase 1: Infrastructure + Docker Compose
- [ ] Phase 2: Polyglot Persistence + Core CRUD
- [ ] Phase 3: Business Logic + Auto-Grading
- [ ] Phase 4: Real Kafka Streaming + Enterprise UI
- [ ] Phase 5: Advanced Features + Verification
- [ ] `.vulns`, `README.md`, `scenarios.md` updated after each phase
- [ ] All existing vulnerabilities preserved and verified
- [ ] Git commit after phase completion
