# Complexity Upgrade Plan: app-17-iot-dashboard

This document details the architectural plan to upgrade the IoT Device Dashboard from a SQLite-backed setup to a multi-container Express/JavaScript environment.

## 1. Overview
The current app-17 JavaScript application runs Express with local SQLite database operations. We will upgrade the application to use PostgreSQL for device configuration data, Redis for active device telemetry caching, and RabbitMQ to queue device status update events.

---

## 2. Component Design

### A. Database (PostgreSQL)
- **Engine**: PostgreSQL 15 (Alpine)
- **Role**: Store persistent tables for `devices`, `users`, `commands`, and `alert_logs`.
- **Migration**: Setup database connection pooling via the `pg` npm package and execute `init.sql` on startup.

### B. Cache (Redis)
- **Engine**: Redis 7 (Alpine)
- **Role**: Cache high-frequency device telemetry (e.g. current temperature, CPU load) to avoid overload on the database.
- **Key Schema**:
  - Live Telemetry: `device:telemetry:live:<device_id>` (expires in 1 minute).

### C. Messaging Queue (RabbitMQ)
- **Engine**: RabbitMQ 3 (Alpine)
- **Role**: Buffer incoming telemetry report streams and queue outgoing device commands.
- **Work Flow**:
  1. IoT devices post status updates to the `/api/devices/telemetry` endpoint.
  2. Express endpoint enqueues the reports into the `telemetry.reports` queue in RabbitMQ.
  3. A background task consumer processes the queue, saves aggregated metrics to PostgreSQL, and updates the live cache in Redis.

---

## 3. Docker Compose Setup

Services definition:
- `db`: PostgreSQL database server.
- `redis`: Redis cache server.
- `rabbitmq`: RabbitMQ broker.
- `web`: IoT Express application (port 8017).

### Environment Configuration (`.env`)
```env
DB_HOST=db
DB_PORT=5432
DB_NAME=iot_dashboard
DB_USER=postgres
DB_PASSWORD=cyberpunk_iot_pass
REDIS_HOST=redis
REDIS_PORT=6379
RABBITMQ_HOST=rabbitmq
```

---

## 4. Impact on Planted Vulnerabilities
We must maintain vulnerability fidelity:
- **VULN-01 (A02 - Cryptographic Failures)**: Plaintext API tokens are stored in the database. Moving to PostgreSQL means these secrets will be queryable directly in PostgreSQL tables, demonstrating how cleartext credentials can expose database links.
- **VULN-02 (A05 - Security Misconfiguration)**: The debug endpoint `/api/debug/system` dumps runtime configurations. In the upgraded setup, this will expose all environment variables, leaking PostgreSQL and RabbitMQ passwords and hosts.
- **VULN-03 (A10 - Server-Side Request Forgery)**: The firmware update function `/api/devices/update` requests files from a user-supplied URL. With RabbitMQ and Redis present in the Docker network, this SSRF becomes highly dangerous, allowing attackers to query the RabbitMQ API (`http://rabbitmq:15672`) or connect to the Redis port inside the network.
- **Chain-01 (API Key Leak → SSRF → Internal Pivot)**: Attacker reads plaintext device credentials, uses the SSRF firmware update endpoint to pivot requests internally, and alters RabbitMQ queues or Redis values.
- **Chain-02 (State Confusion Pivot to IDOR)**: Attacker exploits background command-queue states to read other device configurations.
