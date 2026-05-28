# Phase 01: PostgreSQL Migration + Infra Hardening

## Goal

Switch the application from H2 in-memory database to real PostgreSQL via Docker Compose, verify all existing Kafka and Elasticsearch integrations work with real services, and ensure healthchecks are robust across all containers.

## Scope

### Included
- [ ] Create `application-postgres.properties` profile switching from H2 to PostgreSQL
- [ ] Verify PostgreSQL 16 is configured in `docker-compose.yml` with healthcheck
- [ ] Turn on `APP_KAFKA_ENABLED=true` and verify producer/consumer flow with real Redpanda
- [ ] Turn on `APP_ELASTICSEARCH_ENABLED=true` and verify ES index creation and search
- [ ] Seed `DataInitializer.java` with PostgreSQL-compatible SQL
- [ ] Verify HikariCP connection pool config for PostgreSQL
- [ ] Run all 20 existing endpoints against real PostgreSQL
- [ ] Preserve all existing vulnerability annotations verbatim

### Excluded
- No new business logic (Phase 2)
- No new endpoints
- No vulnerability planting

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| New properties profile, not modify `application.properties` | H2 remains as fallback; Postgres profile is opt-in via `SPRING_PROFILES_ACTIVE=postgres` |
| DataInitializer uses `@Profile("postgres")` | Seed data only executes when PostgreSQL profile is active |
| Redpanda replaces Apache Kafka | Already configured in docker-compose; Kafka API-compatible |
| All changes are infra-only, no source files touched | Minimizes risk to existing vulnerability annotations |

## Vulnerability Planting

None. This phase is pure infrastructure — no new vulnerabilities, no changes to existing annotation-bearing files.

## Decoy Patterns

None new. Existing three decoys (BCrypt, parameterized JPA, protected report endpoint) are preserved.

## Data Model Changes

None. JPA entities remain unchanged.

## API Contracts

All 20 existing endpoints preserved. No new endpoints.

## Artifact Updates

- `src/main/resources/application-postgres.properties`: New file
- `src/main/java/com/hr/config/DataInitializer.java`: Add `@Profile("postgres")`
- `pom.xml`: No changes (PostgreSQL driver already exists)
- `docker-compose.yml`: Verify PostgreSQL healthcheck exists
- No changes to `.vulns`, `README.md`, or `scenarios.md`

## Dependencies on Other Phases

- **Phase 2** depends on Phase 1 (real PostgreSQL must be running for new `onboarding_requests` table)
- **Phase 3** depends on Phase 1 (real Elasticsearch must be running for A03 injection)
