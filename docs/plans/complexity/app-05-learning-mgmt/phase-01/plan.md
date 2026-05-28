# Phase 01: Infrastructure — Wire Stubs to Real Services

## Goal

Switch the app config layer from SQLite `:memory:`, mock MongoDB stub, and in-memory Kafka queue emulation to real PostgreSQL, MongoDB, and Redpanda (Apache Kafka protocol) services orchestrated via the existing `docker-compose.yml`. Preserve all vulnerability annotations verbatim. All 14 endpoints must remain functional.

## Scope

### Included
- [ ] Switch `src/config/db_sql.py` from SQLite `:memory:` to `psycopg2` PostgreSQL connection pool
- [ ] Switch `src/config/db_mongo.py` from `QuizDocumentStore` stub to `pymongo` real client
- [ ] Switch `src/config/kafka_client.py`: import `kafka-python`, add real `KafkaProducer` alongside existing stub (full topic wiring in Phase 4)
- [ ] Add connection retry logic for PostgreSQL, MongoDB, and Redpanda (services may not be ready at app startup)
- [ ] Verify healthcheck route confirms all three backends are reachable
- [ ] Verify existing 14 endpoints respond after config swap
- [ ] Preserve all existing vulnerability annotations verbatim — no annotation-bearing files modified

### Excluded
- No new business features, endpoints, or UI
- No database schema changes (tables still created at app init via `init_db()` for now)
- No changes to `docker-compose.yml` or `requirements.txt` (already in place)

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| `docker-compose.yml` already uses Redpanda (not ZooKeeper+Kafka) | Redpanda bundles Kafka protocol natively — simpler, single container |
| `requirements.txt` already has `psycopg2-binary`, `pymongo`, `kafka-python` | Packages were declared during initial scaffold; this phase wires them in |
| Config files edited in-place, not duplicated | Existing `settings.py` already has env-var fallback pattern for Docker hostnames |
| Healthchecks use `depends_on: condition: service_healthy` in compose | Redpanda `rpk cluster info`, PG `pg_isready`, Mongo `mongosh --eval ping` — all already configured |
| Kafka topics created at producer startup | Avoids hardcoded topic lists; matches existing worker patterns |

## Vulnerability Planting

None. This phase is pure infrastructure — no new vulnerabilities, no changes to existing annotation-bearing files.

## Decoy Patterns

None new. Existing three decoys (parameterized login, role-gated course create, scoped enrollment) are preserved.

## Data Model Changes

None. Database schemas are still created in-memory via `init_db()` at app start. Real schema migrations will happen in Phase 2.

## Artifact Updates

- `src/config/db_sql.py`: Replace `sqlite3` with `psycopg2` pool (single file, in-place)
- `src/config/db_mongo.py`: Replace stub with `pymongo.MongoClient`
- `src/config/kafka_client.py`: Add `kafka-python` imports + connection config
- `src/config/settings.py`: Minor tuning for connection retry/readiness
- No changes to `.vulns`, `README.md`, or `scenarios.md` (no new vulnerabilities)
- No changes to `docker-compose.yml` or `requirements.txt` (already correct)

## Dependencies on Other Phases

- **Phase 2** depends on Phase 1 (real PostgreSQL + MongoDB must be running before migration)
- **Phase 3** depends on Phase 1 (real Kafka must be available for grading workflow)
- **Phase 4** depends on Phase 1 (UI dashboards use Docker-backed services)
