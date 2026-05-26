# Todo List: app-17-iot-dashboard Complexity Upgrade

This checklist tracks the tasks required to implement the full-stack architecture for the IoT Device Dashboard.

## Phase 1: Scaffold & Dependencies
- [ ] Add packages to `package.json`:
  - `pg`
  - `redis`
  - `amqplib`
- [ ] Create PostgreSQL initialization schema `db/init.sql` (defining `users`, `devices`, `commands`).

## Phase 2: Configuration & Environment
- [ ] Update Express app configuration to load settings from `.env`.
- [ ] Create a template `.env.example` file.
- [ ] Create `docker-compose.yml` defining `web`, `db`, `redis`, and `rabbitmq` services.
- [ ] Update application Dockerfile to run wait scripts before starting.

## Phase 3: PostgreSQL Migration
- [ ] Replace SQLite code in `index.js` with `pg.Pool` connection pool.
- [ ] Verify parameterized user registration functions correctly.

## Phase 4: Redis Caching
- [ ] Set up Redis client connection in Express startup.
- [ ] Wrap device status lookup in a Redis cache check (read-through caching).
- [ ] Verify live telemetry updates expire and rewrite properly.

## Phase 5: RabbitMQ Async Processing
- [ ] Configure RabbitMQ connection channel for telemetry status queues.
- [ ] Implement a telemetry consumer daemon that updates PostgreSQL and clears Redis cache.

## Phase 6: Vulnerability & Integration Verification
- [ ] Verify plaintext device credentials leak (A02) displays PostgreSQL database values correctly.
- [ ] Verify SSRF (A10) operates and can target Redis and RabbitMQ hosts.
- [ ] Confirm configuration leak (A05) reveals the new PostgreSQL and RabbitMQ credentials.
- [ ] Run the complete integration tests using Docker Compose.
