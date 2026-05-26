# Todo List: app-11-social-analytics Complexity Upgrade

This checklist tracks the tasks required to implement the full-stack architecture for the Social Media Analytics Dashboard.

## Phase 1: Scaffold & Dependencies
- [ ] Add packages to `package.json`:
  - `pg` and `@types/pg` (PostgreSQL client)
  - `redis` (Redis client)
  - `amqplib` and `@types/amqplib` (RabbitMQ/AMQP client)
- [ ] Create PostgreSQL initialization file `db/init.sql` (defining `users`, `dashboards`, `metrics`).

## Phase 2: Configuration & Environment
- [ ] Update Express app configuration to load settings from `.env`.
- [ ] Create a template `.env.example` file.
- [ ] Create `docker-compose.yml` defining `web`, `db`, `redis`, and `rabbitmq` services.
- [ ] Configure startup order to ensure PostgreSQL and RabbitMQ are fully available before the web server starts.

## Phase 3: PostgreSQL Migration
- [ ] Rewrite database access code to use `pg.Pool` connection pool.
- [ ] Maintain raw string interpolation in search queries to keep the SQLi vulnerability active.

## Phase 4: Redis Caching
- [ ] Set up Redis client connection in Express startup.
- [ ] Wrap dashboard stats computation endpoint in a Redis cache check (read-through caching).

## Phase 5: RabbitMQ Async Processing
- [ ] Refactor webhook endpoint to enqueue metrics payloads into RabbitMQ.
- [ ] Implement a worker process (or concurrent consumer thread) in TypeScript using `amqplib` to process metrics, save to PostgreSQL, and flush expired Redis keys.

## Phase 6: Vulnerability & Integration Verification
- [ ] Verify SQL injection vulnerability (A03) works on the PostgreSQL database.
- [ ] Verify SSRF (A10) operates correctly and can target Redis and RabbitMQ internal hosts.
- [ ] Confirm configuration leak (A05) reveals the new PostgreSQL and RabbitMQ secrets.
- [ ] Run the complete integration tests using Docker Compose.
