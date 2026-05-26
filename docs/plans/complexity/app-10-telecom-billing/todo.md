# Todo List: app-10-telecom-billing Complexity Upgrade

This checklist tracks the tasks required to implement the full-stack architecture for the Telecom Billing Platform.

## Phase 1: Scaffold & Dependencies
- [ ] Add dependencies to `pom.xml`:
  - `org.postgresql:postgresql`
  - `org.springframework.boot:spring-boot-starter-data-redis`
  - `org.springframework.boot:spring-boot-starter-amqp`
- [ ] Create database migration schema in `src/main/resources/db/init.sql` (defining `customers`, `rate_plans`, `calls`, `invoices`).

## Phase 2: Configuration & Environment
- [ ] Update `src/main/resources/application.properties` to read connection strings from environment variables.
- [ ] Create a template `.env.example` file.
- [ ] Create `docker-compose.yml` defining `web`, `db`, `redis`, and `rabbitmq` services.
- [ ] Ensure that the app wait script blocks until PostgreSQL and RabbitMQ accept connections.

## Phase 3: PostgreSQL Migration
- [ ] Replace H2/in-memory configuration in `application.properties` with PostgreSQL settings.
- [ ] Verify Hibernate mappings compile and JDBC connections pool correctly.

## Phase 4: Redis Caching
- [ ] Create a `RedisConfig` configuration bean.
- [ ] Annotate rate plan lookup method in `RatePlanService` with `@Cacheable(value = "plans", key = "#planId")`.
- [ ] Clear rate plan cache when plans are updated.

## Phase 5: RabbitMQ Async Processing
- [ ] Define billing queue (`telecom.billing.queue`) and exchange (`telecom.billing.exchange`) Beans.
- [ ] Refactor payment and invoice trigger endpoints to publish message bodies to RabbitMQ.
- [ ] Implement a `@RabbitListener` worker to calculate invoices asynchronously and save to PostgreSQL.

## Phase 6: Vulnerability & Integration Verification
- [ ] Verify SQL injection vulnerability (A03) works on the PostgreSQL database.
- [ ] Verify insecure design cost manipulation (A04) processes successfully through RabbitMQ and produces incorrect invoice states.
- [ ] Confirm absence of logs (A09) in the background listener.
- [ ] Run the complete integration tests using Docker Compose.
