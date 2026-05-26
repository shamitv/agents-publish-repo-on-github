# Todo List: app-01-ecommerce-catalog Complexity Upgrade

This checklist tracks the tasks required to implement the full-stack architecture for the E-Commerce Product Catalog API.

## Phase 1: Scaffold & Dependencies
- [ ] Add dependency packages to `requirements.txt`:
  - `psycopg2-binary` (PostgreSQL client)
  - `redis` (Redis client)
  - `pika` (RabbitMQ/AMQP client)
- [ ] Create database migration schema in `db/init.sql` (defining `users`, `products`, `orders`).
- [ ] Define initial seed data in `db/seed.sql` with mock catalog and users.

## Phase 2: Configuration & Environment
- [ ] Update `app.py` to read connection parameters from environment variables (host, port, credentials).
- [ ] Create a template `.env.example` file.
- [ ] Create `docker-compose.yml` defining `web`, `db`, `redis`, and `rabbitmq` services.
- [ ] Update the app's `Dockerfile` to install new dependencies and handle delay-starts using a wait script.

## Phase 3: PostgreSQL Migration
- [ ] Rewrite database helper class in `app.py` from SQLite `sqlite3` to PostgreSQL `psycopg2`.
- [ ] Verify parameterized user registration and login queries function correctly on PostgreSQL (Secure Decoys).

## Phase 4: Redis Caching
- [ ] Implement a Redis connection helper.
- [ ] Wrap `list_products()` search results in Redis caching logic.
- [ ] Ensure that cache invalidation triggers on `POST /api/products` (adding a product).

## Phase 5: RabbitMQ Async Processing
- [ ] Write worker thread initialization code inside Flask application startup.
- [ ] Refactor `POST /api/orders` to publish to AMQP exchange instead of writing state synchronously.
- [ ] Implement the AMQP queue consumer in a separate worker loop or thread that deducts stock and completes orders.

## Phase 6: Vulnerability & Integration Verification
- [ ] Verify SQL injection vulnerability on product search (A03) works on PostgreSQL syntax.
- [ ] Verify IDOR vulnerability on order details (A01) works and is not blocked by caching.
- [ ] Validate session forgery (Chain-01) works with Flask session signing.
- [ ] Run the complete integration tests using Docker Compose.
