# Complexity Upgrade Plan: app-11-social-analytics

This document details the architectural plan to upgrade the Social Media Analytics Dashboard from a local SQLite setup to a distributed Express and TypeScript environment.

## 1. Overview
The current app-11 TypeScript application runs Express with a local SQLite database file. We will upgrade the architecture to use PostgreSQL for data persistence, Redis for caching analytics graphs and query results, and RabbitMQ to process incoming social analytics events from external webhooks.

---

## 2. Component Design

### A. Database (PostgreSQL)
- **Engine**: PostgreSQL 15 (Alpine)
- **Role**: Store user profiles, registered analytics dashboards, and timeseries feed event counts.
- **Migration**: Setup database connection pooling via the `pg` npm package and execute `init.sql` on startup.

### B. Cache (Redis)
- **Engine**: Redis 7 (Alpine)
- **Role**: Cache aggregated dashboard data (e.g. daily active user graph statistics) which are resource-intensive to recalculate.
- **Key Schema**:
  - Dashboard stats: `social:dashboard:stats:<dashboard_id>:<date_range>`

### C. Messaging Queue (RabbitMQ)
- **Engine**: RabbitMQ 3 (Alpine)
- **Role**: Buffer incoming social media webhook metrics.
- **Work Flow**:
  1. External feed webhook posts new metrics payload (e.g., likes, retweets) to `/api/webhooks/feed`.
  2. The Express controller accepts the request and publishes the payload to RabbitMQ `feed.metrics` queue.
  3. A background consumer script (started concurrently) consumes the message, updates the totals in PostgreSQL, and invalidates the cached stats in Redis.

---

## 3. Docker Compose Setup

Services definition:
- `db`: PostgreSQL database.
- `redis`: Redis server.
- `rabbitmq`: RabbitMQ message broker.
- `web`: Express API server (port 8011).

### Environment Configuration (`.env`)
```env
DB_HOST=db
DB_PORT=5432
DB_NAME=social_analytics
DB_USER=postgres
DB_PASSWORD=cyberpunk_social_pass
REDIS_HOST=redis
REDIS_PORT=6379
RABBITMQ_HOST=rabbitmq
```

---

## 4. Impact on Planted Vulnerabilities
We must maintain vulnerability fidelity:
- **VULN-01 (A03 - SQL Injection)**: The endpoint `/api/dashboards/search` interpolates query strings directly into the SQL command. We will rewrite this in the new `pg` package driver using string concatenation instead of parameterized parameters, exposing the app to PostgreSQL SQLi vectors. Caching must be bypassed for search queries.
- **VULN-02 (A05 - Security Misconfiguration)**: The unauthenticated `/api/debug/env` endpoint leaks environment configurations. This will now leak sensitive PostgreSQL credentials, Redis endpoint, and RabbitMQ settings.
- **VULN-03 (A10 - Server-Side Request Forgery)**: The feed integration endpoint `/api/feed/import` fetches configurations from a user-supplied URL. This vulnerability is enhanced because the attacker can use the SSRF to interact with internal Docker containers (e.g., calling the RabbitMQ management API at `http://rabbitmq:15672` or reading keys directly from Redis).
- **Chain-01 (Debug Leak → SSRF → Webhook Hijack)**: The attacker leaks credentials via `/api/debug/env`, uses the SSRF to interact with internal RabbitMQ queues or Redis keys, and intercepts or alters incoming analytics streams.
- **Chain-02 (State Confusion Pivot to SSRF)**: Attacker manipulates webhook status states inside the database asynchronously to bypass SSRF filters.
