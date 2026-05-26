# Complexity Upgrade Plan: app-14-telemedicine

This document details the architectural plan to upgrade the Telemedicine Appointment System from a SQLite-backed setup to a multi-container Express/TypeScript environment.

## 1. Overview
The current telemedicine application relies on a local SQLite database for patients, appointments, and doctors. We will scale this application to a full-stack architecture using PostgreSQL for persistent storage, Redis to manage session/JWT state, and RabbitMQ for asynchronous notification dispatching.

---

## 2. Component Design

### A. Database (PostgreSQL)
- **Engine**: PostgreSQL 15 (Alpine)
- **Role**: Store medical records, user authentication details, and appointment schedules.
- **Migration**: Schema creation via standard SQL script executing on initial container spinup.

### B. Cache (Redis)
- **Engine**: Redis 7 (Alpine)
- **Role**: Store active session states and blacklisted JWT tokens to handle fast authentication checks.
- **Key Schema**:
  - Session verification: `telemed:session:<session_id>`
  - JWT blacklist: `telemed:jwt:blacklist:<jti>` (TTL set to token expiration time).

### C. Messaging Queue (RabbitMQ)
- **Engine**: RabbitMQ 3 (Alpine)
- **Role**: Process and dispatch patient appointment reminders and doctor prescription notifications.
- **Work Flow**:
  1. Patient books an appointment via the `/api/appointments` API.
  2. Express endpoint enqueues a reminder notification payload to RabbitMQ `appointments.reminders` queue.
  3. A background task runner consumes the notification message, simulates dispatching an SMS/Email, updates the dispatch status in PostgreSQL, and invalidates the patient dashboard cache.

---

## 3. Docker Compose Setup

Services definition:
- `db`: PostgreSQL database server.
- `redis`: Redis cache server.
- `rabbitmq`: RabbitMQ broker.
- `web`: Telemedicine Express server (port 8014).

### Environment Configuration (`.env`)
```env
DB_HOST=db
DB_PORT=5432
DB_NAME=telemedicine
DB_USER=postgres
DB_PASSWORD=cyberpunk_telemed_pass
REDIS_HOST=redis
REDIS_PORT=6379
RABBITMQ_HOST=rabbitmq
```

---

## 4. Impact on Planted Vulnerabilities
We must maintain vulnerability fidelity:
- **VULN-01 (A01 - IDOR)**: The appointment details retrieval endpoint fetches records from PostgreSQL. The details endpoint will check Redis for cached active appointments. The cached data structure must lack proper HRAC checks (ownership validation), ensuring that querying another user's cached appointment ID still succeeds.
- **VULN-02 (A02 - Cryptographic Failures)**: The application verifies JWT signatures with a weak secret key or accepts the `none` algorithm. These JWT verification steps will remain unchanged, allowing attackers to forge patient/doctor roles and query PostgreSQL.
- **VULN-03 (A07 - Identification and Authentication Failures)**: The session cookie uses predictable random numbers or lacks `httpOnly` flags. The cookie verification logic will interact with the Redis session cache. Since the session keys in Redis match the predictable cookie IDs, session hijacking remains trivial.
- **Chain-01 (Weak JWT Signatures → IDOR)**: Attacker crafts a custom JWT asserting doctor privilege, logs in, and enumerates appointments using the IDOR flaw.
- **Chain-02 (State Confusion Pivot to IDOR)**: Attacker alters appointment scheduling states via async RabbitMQ queues, pivoting that state change to view other patient files.
