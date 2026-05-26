# Todo List: app-06-hr-management Complexity Upgrade

This checklist tracks the tasks required to implement the full-stack architecture for the Enterprise HR Management System.

## Phase 1: Scaffold & Dependencies
- [ ] Add dependencies to `pom.xml`:
  - `org.postgresql:postgresql` (PostgreSQL JDBC driver)
  - `org.springframework.boot:spring-boot-starter-data-redis`
  - `org.springframework.boot:spring-boot-starter-amqp` (RabbitMQ support)
- [ ] Create schema migration files under `src/main/resources/db/migration/` or a SQL initialization script.

## Phase 2: Configuration & Environment
- [ ] Update `src/main/resources/application.properties` to read connection strings from environment variables.
- [ ] Create a template `.env.example` file.
- [ ] Create `docker-compose.yml` defining `web`, `db`, `redis`, and `rabbitmq` services.
- [ ] Configure `web` service healthchecks to wait for PostgreSQL and RabbitMQ readiness.

## Phase 3: PostgreSQL Migration
- [ ] Replace H2/in-memory configuration in `application.properties` with PostgreSQL parameters.
- [ ] Verify Hibernate mappings (`@Entity`) compile and link correctly to PostgreSQL tables.

## Phase 4: Redis Caching
- [ ] Create a `RedisConfig` configuration bean.
- [ ] Annotate employee service lookup methods with `@Cacheable(value = "employees", key = "#id")`.
- [ ] Implement cache evictions on profile updates using `@CacheEvict`.

## Phase 5: RabbitMQ Async Processing
- [ ] Configure RabbitMQ Queue, Exchange, and Binding Beans in Spring configuration.
- [ ] Implement a `RabbitTemplate` publisher to dispatch payroll calculation messages.
- [ ] Implement a `@RabbitListener` consumer class to process payroll messages and write updates to PostgreSQL.

## Phase 6: Vulnerability & Integration Verification
- [ ] Verify deserialization RCE (A08) works against the Spring Boot serialization endpoint.
- [ ] Verify IDOR vulnerability (A01) retrieves profiles from both PostgreSQL and Redis cache correctly.
- [ ] Verify weak cryptography (A02) still decrypts SSNs stored in PostgreSQL.
- [ ] Run the complete integration tests using Docker Compose.
