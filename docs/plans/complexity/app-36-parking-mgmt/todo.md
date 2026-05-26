# Todo List: app-36-parking-mgmt Complexity Upgrade

This checklist tracks the tasks required to implement the full-stack architecture for the Parking Management System.

## Phase 1: Scaffold & Dependencies
- [ ] Add packages to `package.json`:
  - `pg`
  - `redis`
  - `amqplib`
- [ ] Create PostgreSQL initialization schema `db/init.sql` (defining `users`, `spots`, `reservations`).

## Phase 2: Configuration & Environment
- [ ] Update Express app configuration to load settings from `.env`.
- [ ] Create a template `.env.example` file.
- [ ] Create `docker-compose.yml` defining `web`, `db`, `redis`, and `rabbitmq` services.
- [ ] Update application Dockerfile to run wait scripts before starting.

## Phase 3: PostgreSQL Migration
- [ ] Replace SQLite code in `index.js` with `pg.Pool` connection pool.
- [ ] Maintain raw string interpolation in search queries to keep the SQLi vulnerability active.

## Phase 4: Redis Caching
- [ ] Set up Redis client connection in Express startup.
- [ ] Wrap spot availability rates lookup in a Redis cache check (read-through caching).
- [ ] Verify live rates updates expire and rewrite properly.

## Phase 5: RabbitMQ Async Processing
- [ ] Configure RabbitMQ connection channel for reservation booking queues.
- [ ] Implement a booking consumer daemon that updates PostgreSQL and clears Redis cache.

## Phase 6: Vulnerability & Integration Verification
- [ ] Verify SQL injection vulnerability (A03) works on the PostgreSQL database.
- [ ] Verify cost manipulation (A04) processes successfully through RabbitMQ and produces incorrect billing states.
- [ ] Confirm absence of logs (A09) in the background listener.
- [ ] Run the complete integration tests using Docker Compose.
