# Todo List: app-14-telemedicine Complexity Upgrade

This checklist tracks the tasks required to implement the full-stack architecture for the Telemedicine Appointment System.

## Phase 1: Scaffold & Dependencies
- [ ] Add npm packages to `package.json`:
  - `pg` and `@types/pg`
  - `redis`
  - `amqplib` and `@types/amqplib`
- [ ] Create PostgreSQL initialization file `db/init.sql` (defining tables for `patients`, `appointments`, `medical_records`, `sessions`).

## Phase 2: Configuration & Environment
- [ ] Update application config code to parse database, Redis, and RabbitMQ settings from `.env`.
- [ ] Create a template `.env.example` file.
- [ ] Create `docker-compose.yml` defining `web`, `db`, `redis`, and `rabbitmq` services.
- [ ] Set up Docker Compose healthchecks to wait for PostgreSQL and RabbitMQ databases to accept connections.

## Phase 3: PostgreSQL Migration
- [ ] Replace SQLite queries with `pg.Pool` connection pooling in all endpoints.
- [ ] Verify parameterized user registration functions correctly.

## Phase 4: Redis Caching & Session Management
- [ ] Implement Redis-backed session verification helper.
- [ ] Use Redis to cache doctor directories and appointment lists.
- [ ] Ensure cache invalidation occurs when appointments are updated or canceled.

## Phase 5: RabbitMQ Async Processing
- [ ] Configure RabbitMQ connection channel for enqueuing appointment bookings.
- [ ] Implement a background notification worker using `amqplib` that listens to `appointments.reminders` queue.
- [ ] Implement prescription processing background task enqueuing.

## Phase 6: Vulnerability & Integration Verification
- [ ] Verify weak JWT signature verification (A02) allows access to PostgreSQL endpoints.
- [ ] Verify IDOR vulnerability (A01) retrieves medical files and appointment data correctly.
- [ ] Verify session cookie predictability (A07) works with the Redis session cache.
- [ ] Run the complete integration tests using Docker Compose.
