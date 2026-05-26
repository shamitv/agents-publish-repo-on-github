# Todo List: app-05-learning-mgmt Complexity Upgrade

This checklist tracks the tasks required to implement the enterprise architecture for the Online Learning Management System.

## Phase 1: Scaffold & Dependencies
- [ ] Add packages to `requirements.txt`:
  - `psycopg2-binary`
  - `pymongo`
  - `kafka-python`
- [ ] Structure directory under `src/`: `blueprints/`, `config/`, `controllers/`, `services/`, `models/`, `workers/`.

## Phase 2: Docker Compose Setup
- [ ] Create `docker-compose.yml` specifying:
  - `web` (App server + consumer worker threads)
  - `db` (PostgreSQL 15)
  - `mongodb` (MongoDB 6)
  - `zookeeper`
  - `kafka`
- [ ] Setup wait scripts for all database and broker services.

## Phase 3: Polyglot Database Migration
- [ ] Implement database client configurations in `src/config/`:
  - PostgreSQL pools for course metadata.
  - MongoDB connections for quiz layouts and submissions.
- [ ] Migrate schemas and models.

## Phase 4: Business Logic & Rules
- [ ] Implement `src/services/prereq_validator.py` checking course dependency rules.
- [ ] Implement quiz auto-grading rules (handling multiple question configurations).

## Phase 5: Kafka Event Streaming
- [ ] Set up Kafka Producer.
- [ ] Refactor quiz submission API to publish to the `grading` topic.
- [ ] Implement `src/workers/grading_listener.py` to calculate quiz scores and update PostgreSQL.
- [ ] Refactor course import API to publish to the `course-imports` topic.
- [ ] Implement `src/workers/import_listener.py` running `pickle.loads()`.

## Phase 6: Enterprise UI Implementation
- [ ] Build a multi-panel student portal dashboard displaying enrollments, gradebooks, and active course paths.

## Phase 7: Verification
- [ ] Verify Pickle deserialization RCE (A08) works against the background Kafka import consumer.
- [ ] Verify every standalone vulnerability has the required `// VULNERABILITY <OWASP_ID>: <brief description>` source annotation.
- [ ] Verify every chain component has the required `// CHAIN LINK <N> (chain-<ID>): <description>` source annotation.
- [ ] Verify `.vulns`, README chain table, and plan chain table agree on OWASP ID, severity, CWE, impact, location, and method.
- [ ] Verify nearby decoy safe patterns remain implemented and are listed in `.vulns.decoys`.
- [ ] Verify IDOR vulnerability (A01) bypasses session checks in the modularized quiz controller.
