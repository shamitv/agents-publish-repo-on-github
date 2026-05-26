# Todo List: app-05-learning-mgmt Complexity Upgrade

This checklist tracks the tasks required to implement the full-stack architecture for the Online Learning Management System.

## Phase 1: Scaffold & Dependencies
- [ ] Add dependency packages to `requirements.txt`:
  - `psycopg2-binary`
  - `redis`
  - `pika`
- [ ] Create database migration schema in `db/init.sql` (defining `users`, `courses`, `enrollments`, `submissions`).
- [ ] Define initial seed data in `db/seed.sql` with mock student/instructor credentials and courses.

## Phase 2: Configuration & Environment
- [ ] Update `app.py` to read connection parameters from environment variables (host, port, credentials).
- [ ] Create a template `.env.example` file.
- [ ] Create `docker-compose.yml` defining `web`, `db`, `redis`, and `rabbitmq` services.
- [ ] Update the app's `Dockerfile` to launch both the Flask server and the background grading worker.

## Phase 3: PostgreSQL Migration
- [ ] Rewrite database helpers in `app.py` from SQLite `sqlite3` to PostgreSQL `psycopg2`.
- [ ] Verify parameterized user registration and enrollment validation logic function correctly.

## Phase 4: Redis Caching
- [ ] Implement a Redis connection manager.
- [ ] Store active session ID mapping in Redis.
- [ ] Wrap submission retrieval in Redis cache read/write calls.

## Phase 5: RabbitMQ Async Processing
- [ ] Refactor quiz submission endpoint to publish message containing quiz inputs to RabbitMQ.
- [ ] Write RabbitMQ grading consumer to compute scores, update PostgreSQL database, and invalidate Redis score cache.
- [ ] Refactor course import endpoint to publish base64 pickled templates to `course.import` queue.
- [ ] Write RabbitMQ import consumer that executes `pickle.loads()`.

## Phase 6: Vulnerability & Integration Verification
- [ ] Verify Pickle deserialization RCE (A08) works against the async import worker.
- [ ] Verify IDOR vulnerability on submission retrieval (A01) works and is not blocked by caching.
- [ ] Validate session forgery via secret key leak (Chain-01) works under the new environment.
- [ ] Run the complete integration tests using Docker Compose.
