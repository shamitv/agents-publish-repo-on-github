# Phase 01 TODO — Infrastructure + Docker Compose

## Pre-requisites
- [ ] Read vuln-inventory.md — confirm all no-touch files
- [ ] Read expansion-plan.md — confirm phase scope

## Docker Compose
- [ ] Create `docker-compose.yml` with services:
  - `web` (app server, build from `Dockerfile`, ports 8085:8085, depends_on db/mongo/kafka)
  - `db` (PostgreSQL 15, healthcheck: `pg_isready -U postgres`)
  - `mongo` (MongoDB 6, healthcheck: `mongosh --eval "db.runCommand('ping')"`)
  - `zookeeper` (confluentinc/cp-zookeeper)
  - `kafka` (confluentinc/cp-kafka, depends_on zookeeper)
- [ ] Add healthcheck wait loop in `app.py` or a bootstrap script

## Requirements
- [ ] Add to `requirements.txt`:
  - `psycopg2-binary`
  - `pymongo`
  - `kafka-python`

## Config — PostgreSQL
- [ ] Edit `src/config/db_sql.py`: replace `sqlite3.connect(...)` with `psycopg2.pool.SimpleConnectionPool`
- [ ] Update `src/config/settings.py`: add `PG_HOST`, `PG_PORT`, `PG_DB`, `PG_USER`, `PG_PASS` env vars with defaults
- [ ] Verify connection works when Docker Compose is up

## Config — MongoDB
- [ ] Edit `src/config/db_mongo.py`: replace in-memory dict store with `pymongo.MongoClient`
- [ ] Update `src/config/settings.py`: add `MONGO_URI` env var
- [ ] Verify connection works when Docker Compose is up

## Config — Kafka
- [ ] Edit `src/config/kafka_client.py`: replace thread-queue stub with `kafka.KafkaProducer` / `kafka.KafkaConsumer`
- [ ] Update `src/config/settings.py`: add `KAFKA_BROKER` env var
- [ ] Verify producer/consumer works when Docker Compose is up

## Verification
- [ ] Start Docker Compose: `docker compose up -d`
- [ ] Wait for all healthchecks to pass
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
