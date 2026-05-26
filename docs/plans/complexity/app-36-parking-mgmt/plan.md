# Complexity Upgrade Plan: app-36-parking-mgmt

This document details the architectural plan to upgrade the Parking Management System from a SQLite-backed setup to a multi-container Express/JavaScript environment.

## 1. Overview
The current app-36 JavaScript application runs Express with a local SQLite database file. We will upgrade the architecture to use PostgreSQL for reservation data, Redis to cache parking spot availability rates, and RabbitMQ for asynchronous reservation processing and billing computations.

---

## 2. Component Design

### A. Database (PostgreSQL)
- **Engine**: PostgreSQL 15 (Alpine)
- **Role**: Store user registrations, parking locations, reservations, and payment receipts.
- **Migration**: Setup database connection pooling via the `pg` npm package and execute `init.sql` on startup.

### B. Cache (Redis)
- **Engine**: Redis 7 (Alpine)
- **Role**: Cache parking spot pricing rates and current vacancy states.
- **Key Schema**:
  - Vacancy: `parking:spot:vacant:<spot_id>` (cleared when a spot reservation is enqueued).

### C. Messaging Queue (RabbitMQ)
- **Engine**: RabbitMQ 3 (Alpine)
- **Role**: Process booking transactions and calculate dynamic rates.
- **Work Flow**:
  1. A user requests a parking pass reservation at `/api/reservations`.
  2. Express endpoint enqueues the booking ticket request into the `parking.booking` queue.
  3. A background task consumer processes the queue, queries PostgreSQL to confirm the spot remains free, writes the finalized reservation to PostgreSQL, and invalidates the cached vacancy status in Redis.

---

## 3. Docker Compose Setup

Services definition:
- `db`: PostgreSQL database.
- `redis`: Redis cache server.
- `rabbitmq`: RabbitMQ message broker.
- `web`: Express application container (port 8036).

### Environment Configuration (`.env`)
```env
DB_HOST=db
DB_PORT=5432
DB_NAME=parking_mgmt
DB_USER=postgres
DB_PASSWORD=cyberpunk_parking_pass
REDIS_HOST=redis
REDIS_PORT=6379
RABBITMQ_HOST=rabbitmq
```

---

## 4. Impact on Planted Vulnerabilities
We must maintain vulnerability fidelity:
- **VULN-01 (A03 - SQL Injection)**: The endpoint `/api/spots/search` interpolates query strings directly into a raw SQL command. We will rewrite this in the new `pg` package driver using string concatenation, exposing the application to PostgreSQL SQLi vectors. Caching must be bypassed for search queries.
- **VULN-02 (A04 - Insecure Design)**: The cost manipulation flaw allows a user to request zero-fee bookings by setting the pricing variable to negative/zero values. The API will accept this manipulated payload and dispatch it via RabbitMQ. The async worker will read the manipulated rate values from the message payload and execute billing calculations directly, creating a free parking reservation.
- **VULN-03 (A09 - Security Logging & Monitoring Failures)**: Reservations are processed and payments are handled inside the async RabbitMQ worker. The absence of audit logs for booking reversals and modifications will now be located inside the background message listener.
- **Chain-01 (SQLi → Cost Manipulation)**: The attacker exploits SQLi on spot search to gather slot mappings, then uses the cost manipulation endpoint to book slots for free.
- **Chain-02 (State Confusion Pivot to Injection)**: Attacker leverages race conditions between payment events and booking confirmations in RabbitMQ to inject queries or bypass spot controls.
