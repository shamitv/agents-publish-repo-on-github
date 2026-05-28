# Phase 01 TODO — Infrastructure + Docker Compose

## Pre-requisites
- [ ] Read vuln-inventory.md — confirm all no-touch files
- [ ] Read expansion-plan.md — confirm phase scope
- [ ] Verify `docker-compose.yml` is present (already in app root — uses Redpanda, not ZooKeeper)
- [ ] Verify `requirements.txt` includes `psycopg2-binary`, `pymongo`, `kafka-python` (already declared)

## Config — PostgreSQL
- [ ] Edit `src/config/db_sql.py`: replace `sqlite3.connect(...)` with `psycopg2.pool.SimpleConnectionPool`
- [ ] Add connection retry logic (loop with backoff until PG responds)
- [ ] Verify connection works when Docker Compose is up

## Config — MongoDB
- [ ] Edit `src/config/db_mongo.py`: replace `QuizDocumentStore` stub with `pymongo.MongoClient`
- [ ] Add connection retry logic
- [ ] Verify connection works when Docker Compose is up

## Config — Kafka
- [ ] Edit `src/config/kafka_client.py`: add `kafka.KafkaProducer` / `kafka.KafkaConsumer` imports and connection config
- [ ] Keep existing thread-queue stub as fallback; full topic wiring happens in Phase 4
- [ ] Verify producer connects when Docker Compose is up

## Verification
- [ ] Start Docker Compose: `docker compose up -d`
- [ ] Wait for all healthchecks to pass (Redpanda `rpk cluster info`, PG `pg_isready`, Mongo `mongosh --eval ping`)
- [ ] Start Flask app: `python app.py`
- [ ] Verify all 14 endpoints respond correctly:
  - `GET /api/health` → 200
  - `POST /api/auth/login` → 200
  - `GET /api/courses` → 200
  - `POST /api/enrollments` → 200
  - `GET /api/submissions/2` → 200
  - `GET /api/debug/config` → 200 (leaks secrets)
  - etc.
- [ ] Verify existing vulnerabilities remain exploitable:
  - A01 IDOR: read another user's submission
  - A05 Debug: read secrets from `/api/debug/config`
  - A08 Pickle: trigger import via Kafka with malicious payload
  - chain-01: Debug leak → session forge → submission read
- [ ] Verify decoys still present:
  - DECOY-01: parameterized login still works
  - DECOY-02: course creation still gated by role
  - DECOY-03: enrollment list still scoped to session
- [ ] Confirm no annotation-bearing files were modified

## Regular Commits
- [ ] Commit after each major task:
  `git add -A && git commit -m "app-05 phase-01: <descriptive message>"`
- [ ] Push to remote after each commit

## Phase Status Report
- [ ] Create `phase-01/status-report.md` after completion:
  - What was implemented
  - Files created (count)
  - Files modified (count)
  - Vulnerabilities planted (type, location)
  - Decoys planted (location)
  - Existing vulns still intact? (yes/no)
  - Chains functional? (yes/no)
  - Tests passing? (yes/no)
  - Blockers
