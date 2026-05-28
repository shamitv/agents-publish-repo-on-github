# Phase 01 TODO — PostgreSQL Migration + Infra Hardening

## Pre-requisites
- [ ] Read vuln-inventory.md — confirm all no-touch files
- [ ] Read expansion-plan.md — confirm phase scope

## PostgreSQL Profile
- [ ] Create `src/main/resources/application-postgres.properties`:
  - `spring.datasource.url=jdbc:postgresql://${DB_HOST:localhost}:5432/hrdb`
  - `spring.datasource.driver-class-name=org.postgresql.Driver`
  - `spring.datasource.username=${DB_USER:postgres}`
  - `spring.datasource.password=${DB_PASS:postgres}`
  - `spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect`
  - `spring.jpa.hibernate.ddl-auto=update`
  - `app.kafka.enabled=true`
  - `app.elasticsearch.enabled=true`
- [ ] Edit `DataInitializer.java`: add `@Profile("postgres")` annotation to prevent seeding in dev mode

## Docker Compose Verification
- [ ] Add `SPRING_PROFILES_ACTIVE=postgres` to the `web` service environment in `docker-compose.yml` (env vars already set  `SPRING_DATASOURCE_URL`, `APP_KAFKA_ENABLED`, `APP_ELASTICSEARCH_ENABLED`)
- [ ] Create `.env.example` at app root listing all expected environment variables with placeholder values
- [ ] Verify `docker-compose.yml` has healthcheck for `postgres`:
  ```yaml
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres"]
    interval: 5s
    timeout: 3s
    retries: 5
  ```
- [ ] Verify `web` service depends_on with condition for all services
- [ ] Verify `SPRING_PROFILES_ACTIVE=postgres` is set as environment variable for `web` service

## Integration Verification
- [ ] Start Docker Compose: `docker compose up -d --build`
- [ ] Wait for all healthchecks to pass
- [ ] Verify app starts with PostgreSQL profile
- [ ] Verify JPA tables are created in PostgreSQL (connect and run `\dt`)
- [ ] Verify Kafka producer/consumer:
  - Trigger a payroll audit event
  - Verify PayrollAuditConsumer receives it
- [ ] Verify Elasticsearch:
  - Check ES index created (if any)
  - `GET /api/employees?q=test` returns results
- [ ] Run all 20 endpoints against real PostgreSQL:
  - `GET /api/health` → 200
  - `GET /api/employees` → list
  - `GET /api/payroll/1` → payroll (IDOR works)
  - `POST /api/employees` → create
  - `POST /api/employees/import` → deserialization trigger
  - etc.

## Verification
- [ ] Verify existing vulnerabilities remain exploitable:
  - A01 IDOR: read another employee's payroll
  - A02 XOR: decrypt SSN from payroll response
  - A08 deserialization: upload malicious .ser file
  - A08 Log4j: send JNDI payload via Kafka event
- [ ] Verify decoys still present:
  - DECOY-01: BCrypt still used for passwords
  - DECOY-02: JPA queries still parameterized
  - DECOY-03: payroll report still role-gated
- [ ] Run `mvn test` — all 5 tests pass
- [ ] Confirm no annotation-bearing files were modified

## Regular Commits
- [ ] Commit after PostgreSQL profile works
- [ ] Commit after full integration verification passes

## Phase Status Report
- [ ] Create `phase-01/status-report.md` after completion
