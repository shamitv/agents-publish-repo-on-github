# Todo List: app-10-telecom-billing Complexity Upgrade

This checklist tracks the tasks required to implement the enterprise architecture for the Telecom Billing Platform.

## Phase 1: Scaffold & Dependencies
- [ ] Add dependencies to `pom.xml`:
  - `org.postgresql:postgresql`
  - `org.springframework.kafka:spring-kafka`
  - `org.springframework.boot:spring-boot-starter-data-redis`
- [ ] Create modular Java package structure under `src/main/java/com/telecom/`: `config`, `controller`, `model`, `repository`, `service`, `listener`.

## Phase 2: Docker Compose Setup
- [ ] Create `docker-compose.yml` specifying:
  - `web` (Spring Boot app)
  - `db` (PostgreSQL 15 + TimescaleDB extension setup)
  - `redis` (Redis 7)
  - `zookeeper`
  - `kafka`
- [ ] Configure healthcheck delay configurations.

## Phase 3: Polyglot Database Migration
- [ ] Map `@Entity` annotations to PostgreSQL database tables.
- [ ] Write SQL migrations to create standard tables and a partitioned `call_detail_records` table.
- [ ] Seed initial database tables with mock rates and customer details.

## Phase 4: Business Logic & Rules
- [ ] Implement `src/main/java/com/telecom/service/TariffCalculator.java` incorporating peak/off-peak, local, and roaming calculations.
- [ ] Implement grace-period and status validations.

## Phase 5: Kafka Event Streaming
- [ ] Configure `KafkaTemplate` bean in Spring settings.
- [ ] Refactor CDR logging endpoints to publish data payloads to Kafka.
- [ ] Implement `@KafkaListener` consumer `CdrConsumer` to perform dynamic tariff math, write calls to PostgreSQL partitions, and flush Redis active metrics.

## Phase 6: Enterprise UI Implementation
- [ ] Build an HTML portal dashboard showing monthly calling charts (visualizing call data from PostgreSQL), billing summaries, and billing adjustments.

## Phase 7: Verification
- [ ] Verify every standalone vulnerability has the required `// VULNERABILITY <OWASP_ID>: <brief description>` source annotation.
- [ ] Verify every chain component has the required `// CHAIN LINK <N> (chain-<ID>): <description>` source annotation.
- [ ] Verify `.vulns`, README chain table, and plan chain table agree on OWASP ID, severity, CWE, impact, location, and method.
- [ ] Verify nearby decoy safe patterns remain implemented and are listed in `.vulns.decoys`.
- [ ] Verify SQL injection vulnerability (A03) works on the PostgreSQL database.
- [ ] Verify cost manipulation (A04) processes successfully through Kafka and produces incorrect billing values.
- [ ] Confirm absence of logs (A09) in the background listener.
- [ ] Run the complete integration tests using Docker Compose.
