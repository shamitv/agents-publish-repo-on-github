# Complexity Upgrade Plan: app-01-ecommerce-catalog

This document details the architectural plan to upgrade the E-Commerce Product Catalog API from a simple SQLite-backed app to a production-like multi-container full-stack service.

## 1. Overview
The current Flask application utilizes a local SQLite database for product catalog, user auth, and order data, running completely in-memory/in-file. We will migrate to a multi-container Docker Compose structure incorporating PostgreSQL as the database, Redis as a caching layer for search results, and RabbitMQ for asynchronous order processing.

---

## 2. Component Design

### A. Database (PostgreSQL)
- **Engine**: PostgreSQL 15 (Alpine)
- **Role**: Replace SQLite for persistent storage of users, products, and orders.
- **Migration**: A `migration.sql` script will run upon database initialization to build tables (`users`, `products`, `orders`).
- **Connection**: Managed via `psycopg2-binary` pool in Flask.

### B. Cache (Redis)
- **Engine**: Redis 7 (Alpine)
- **Role**: Cache product list searches and product details to speed up catalog views.
- **Eviction/TTL**: 5-minute TTL on product search cache; invalidated when new products are added.
- **Key Schema**:
  - Search queries: `cache:products:search:<query_term>`
  - Details: `cache:products:detail:<product_id>`

### C. Messaging Queue (RabbitMQ)
- **Engine**: RabbitMQ 3 (with Management Plugin)
- **Role**: Asynchronous order processing and stock deduction.
- **Work Flow**:
  1. User calls `/api/orders` to checkout.
  2. Flask API validates basic request parameters, creates a pending order in the database, and publishes a JSON message `{"order_id": <id>, "user_id": <uid>}` to the `order.checkout` queue.
  3. A background daemon consumer thread running inside the Flask container (or a separate worker process) consumes the message, deducts inventory, and updates order status to `completed`.

---

## 3. Docker Compose Setup

Three services will run in a private Docker network:
- `db`: PostgreSQL container, persistence via named volume `pg_data`.
- `redis`: Redis container.
- `rabbitmq`: RabbitMQ container with standard AMQP port 5672.
- `web`: Flask web application container, exposed on port 8001.

### Environment Configuration (`.env`)
```env
DB_HOST=db
DB_PORT=5432
DB_NAME=ecommerce
DB_USER=postgres
DB_PASSWORD=cyberpunk_db_secure_pass
REDIS_HOST=redis
REDIS_PORT=6379
RABBITMQ_HOST=rabbitmq
```

---

## 4. Impact on Planted Vulnerabilities
We must ensure that all vulnerabilities remain fully exploitable after the upgrade:
- **VULN-01 (A01 - IDOR)**: The order details query is migrated to PostgreSQL. The Redis cache must not bypass ownership checks or hide the IDOR. Caching will key purely on `order_id` (e.g. `cache:orders:detail:<order_id>`) without validating the requesting user, making the IDOR exploitable directly from cache or DB.
- **VULN-02 (A03 - SQLi)**: The product search remains vulnerable via raw string formatting. We will construct the SQL query using PostgreSQL formatting, exposing PostgreSQL-specific SQLi syntax. The results of the query (including SQLi payloads) will be cached in Redis with the search key to show how caching can store malicious query results.
- **VULN-03 (A09 - Logging Failure)**: The checkout process is now handled asynchronously by the background consumer thread. The lack of structured audit logging will now extend to the consumer worker where stock deduction and state updates are executed.
- **Chain-01 (User Enumeration → Session Forge → Admin Takeover)**: The user existence endpoint and Flask session signing remain unaltered, allowing session forgery using the hardcoded key.
- **Chain-02 (State Confusion Pivot to IDOR)**: State is stored in PostgreSQL and modified by RabbitMQ consumer. Since order status transitions depend on the background worker, stateful race conditions or state confusion can be demonstrated.
