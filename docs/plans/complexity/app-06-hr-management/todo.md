# Todo List: app-06-hr-management Complexity Upgrade

This checklist tracks the tasks required to implement the enterprise architecture for the Enterprise HR Management System.

## Phase 1: Scaffold & Dependencies
- [ ] Add dependencies to `pom.xml`:
  - `org.postgresql:postgresql`
  - `org.springframework.kafka:spring-kafka`
  - `org.springframework.boot:spring-boot-starter-data-elasticsearch`
  - `org.apache.logging.log4j:log4j-core:2.14.1` (Vulnerable Log4j dependency)
- [ ] Create modular Java package structure under `src/main/java/com/hr/`: `config`, `controller`, `dto`, `model`, `repository`, `service`, `listener`.

## Phase 2: Docker Compose Setup
- [ ] Create `docker-compose.yml` specifying:
  - `web` (Spring Boot app)
  - `db` (PostgreSQL 15)
  - `elasticsearch` (Elasticsearch 8)
  - `zookeeper`
  - `kafka`
- [ ] Configure healthcheck delay-wait configurations.

## Phase 3: PostgreSQL Migration & JPA Setup
- [ ] Set up PostgreSQL datasource credentials in `application.properties`.
- [ ] Map `@Entity` annotations to PostgreSQL database tables.
- [ ] Write SQL scripts for table migrations.

## Phase 4: Elasticsearch Integration
- [ ] Implement `ElasticsearchConfig` client connectivity.
- [ ] Add JPA post-lifecycle hooks to synchronize employee entities into Elasticsearch.
- [ ] Implement search controllers utilizing the Elasticsearch Repository helper.

## Phase 5: Kafka Event Streaming & Log4j
- [ ] Configure `KafkaTemplate` event emitter bean in Spring.
- [ ] Refactor onboarding REST APIs to emit state events to Kafka topics.
- [ ] Implement `@KafkaListener` listener to consume events.
- [ ] Add vulnerable Log4j call (`logger.info("Audit log: " + eventPayload)`) inside the consumer to enable Log4Shell exploit (A08).

## Phase 6: Onboarding Workflow Logic
- [ ] Implement state machine logic transitions using a service validator.

## Phase 7: Enterprise UI Implementation
- [ ] Construct an HTML dashboard showing onboarding flows, list of employees, and logs read from Elasticsearch.

## Phase 8: Verification
- [ ] Verify every standalone vulnerability has the required `// VULNERABILITY <OWASP_ID>: <brief description>` source annotation.
- [ ] Verify every chain component has the required `// CHAIN LINK <N> (chain-<ID>): <description>` source annotation.
- [ ] Verify `.vulns`, README chain table, and plan chain table agree on OWASP ID, severity, CWE, impact, location, and method.
- [ ] Verify nearby decoy safe patterns remain implemented and are listed in `.vulns.decoys`.
- [ ] Verify Log4j RCE (A08) works against the Kafka consumer queue.
- [ ] Verify IDOR (A01) retrieves profiles from PostgreSQL correctly.
- [ ] Verify weak cryptography (A02) still decrypts SSNs stored in PostgreSQL.
