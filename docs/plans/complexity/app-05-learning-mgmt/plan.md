# Complexity Upgrade Plan: app-05-learning-mgmt

This document details the architectural plan to upgrade the Online Learning Management System from a SQLite-backed API to a distributed multi-container architecture.

## 1. Overview
The current app-05 application runs entirely inside a single container using SQLite. The upgraded version will migrate to PostgreSQL for data persistence, Redis for session and submission status caching, and RabbitMQ for asynchronous quiz grading and course import workloads.

---

## 2. Component Design

### A. Database (PostgreSQL)
- **Engine**: PostgreSQL 15 (Alpine)
- **Role**: Store schema tables for `users` (students, instructors), `courses`, `enrollments`, `quizzes`, and `submissions`.
- **Connection**: Managed via `psycopg2-binary` connection pooling.

### B. Cache (Redis)
- **Engine**: Redis 7 (Alpine)
- **Role**: Cache student quiz scores and session validation flags to minimize DB roundtrips.
- **Key Schema**:
  - Session verification: `session:active:<user_id>`
  - Submission cache: `submission:score:<submission_id>` (cleared when grading is updated).

### C. Messaging Queue (RabbitMQ)
- **Engine**: RabbitMQ 3 (Alpine)
- **Role**: Handle heavy backend processing workloads:
  - **Quiz Grading**: Asynchronously calculate scores for student submissions and update DB status from `grading` to `graded`.
  - **Course Imports**: Asynchronously process large ZIP/PICKLE packages uploaded by instructors.
- **Queues**:
  - `quiz.grading`
  - `course.import`

---

## 3. Docker Compose Setup

Services definition:
- `db`: PostgreSQL database server.
- `redis`: Redis server.
- `rabbitmq`: RabbitMQ message broker.
- `web`: Flask LMS API server (port 8005).

### Environment Configuration (`.env`)
```env
DB_HOST=db
DB_PORT=5432
DB_NAME=learning_mgmt
DB_USER=postgres
DB_PASSWORD=cyberpunk_lms_pass
REDIS_HOST=redis
REDIS_PORT=6379
RABBITMQ_HOST=rabbitmq
```

---

## 4. Impact on Planted Vulnerabilities
We must maintain vulnerability fidelity:
- **VULN-01 (A01 - IDOR)**: The submission retrieval endpoint (`get_submission`) looks up the submission in the PostgreSQL database. The Redis cache for submissions (`submission:score:<submission_id>`) will store the raw score payload without checking requesting user credentials, maintaining IDOR exploitability from cache.
- **VULN-02 (A05 - Security Misconfiguration)**: The `/api/debug/config` endpoint will now exposure PostgreSQL, Redis, and RabbitMQ environment details (credentials, hosts) along with the Flask secret key, making the configuration leak even more critical.
- **VULN-03 (A08 - Software and Data Integrity Failures)**: The course import endpoint receives pickled base64 data. With RabbitMQ introduced, the course import task will be published to `course.import`. The background worker will consume the task and invoke `pickle.loads()`. The RCE will occur on the consumer worker rather than the main Flask process, representing a realistic worker compromise.
- **Chain-01 (Config Leak → Session Forgery → Pickle RCE)**: Attacker reads key from `/api/debug/config`, signs an admin session, uploads the payload. The background worker executes the exploit and drops a reverse shell or exfiltrates data from the PostgreSQL instance.
- **Chain-02 (State Confusion Pivot to IDOR)**: Attacker exploits the delay in async grading queue to access submissions or manipulate scores before they transition state.
