# Phase 01: Infrastructure + Docker Compose

## Goal

Replace all stub infrastructure (SQLite, in-memory Kafka mock, simulated MongoDB) with real Docker-backed services while preserving every existing vulnerability verbatim and keeping all 14 endpoints functional.

## Scope

### Included
- [ ] Create `docker-compose.yml` with PostgreSQL 15, MongoDB 6, ZooKeeper, Kafka, and healthchecks
- [ ] Create Docker wait scripts for all services
- [ ] Switch `src/config/db_sql.py` from SQLite to `psycopg2` PostgreSQL connection pool
- [ ] Switch `src/config/db_mongo.py` from in-memory mock to `pymongo` real client
- [ ] Update `src/config/kafka_client.py`: import `kafka-python`, create connection config (broker address, topic list). The thread-queue stub is kept as a fallback transport; full topic wiring happens in Phase 4.
- [ ] Update `requirements.txt` with `psycopg2-binary`, `pymongo`, `kafka-python`
- [ ] Update `src/config/settings.py` for Docker-hosted service endpoints
- [ ] Verify all 14 existing endpoints respond after config swap
- [ ] Preserve all existing vulnerability annotations verbatim

### Excluded
- No new business features
- No database schema changes (tables still created at app init)
- No new endpoints
- No UI changes

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| `docker-compose.yml` lives at app root alongside `app.py` | Follows existing convention; containers are dev-only |
| Healthchecks use `pg_isready`, `mongosh --eval`, `kafka-topics.sh` | Standard Docker healthcheck patterns; no custom code needed |
| Config files are edited in-place, not duplicated | Existing `settings.py` already has env-var fallback pattern |
| Kafka topics created at consumer startup | Avoids hardcoded topic lists; matches existing worker patterns |
| Existing vulnerability annotations are never touched | They are benchmark ground truth |

## Vulnerability Planting

None. This phase is pure infrastructure — no new vulnerabilities, no changes to existing annotation-bearing files.

## Decoy Patterns

None new. Existing three decoys (parameterized login, role-gated course create, scoped enrollment) are preserved.

## Data Model Changes

None. Database schemas are still created in-memory via SQLite at app start. Real schema migrations will happen in Phase 2.

## Artifact Updates

- `requirements.txt`: Add `psycopg2-binary`, `pymongo`, `kafka-python`
- `docker-compose.yml`: New file
- `src/config/settings.py`: Tune for Docker service hostnames
- No changes to `.vulns`, `README.md`, or `scenarios.md` (no new vulnerabilities)

## Dependencies on Other Phases

- **Phase 2** depends on Phase 1 (real PostgreSQL + MongoDB must be running before migration)
- **Phase 3** depends on Phase 1 (real Kafka must be available for grading workflow)
- **Phase 4** depends on Phase 1 (UI dashboards use Docker-backed services)
