# Complexity Upgrade Plan: app-06-hr-management

This document details the architectural plan to upgrade the Enterprise HR Management System from an in-memory Spring Boot setup to a distributed multi-container environment.

## 1. Overview
The current Spring Boot application uses an in-memory database (such as H2) for employee and contract data. We will upgrade the application to use a PostgreSQL database for persistence, Redis to cache employee records, and RabbitMQ for asynchronous contract generation and payroll tasks.

---

## 2. Component Design

### A. Database (PostgreSQL)
- **Engine**: PostgreSQL 15 (Alpine)
- **Role**: Store persistent tables for `employees`, `users`, `departments`, and `payroll_records`.
- **Migration**: Database schema creation and initial seeding will be managed via Spring Boot Liquibase/Flyway migrations or raw SQL execution on startup.
- **Connection**: Managed via Spring Boot Data JPA with a HikariCP connection pool.

### B. Cache (Redis)
- **Engine**: Redis 7 (Alpine)
- **Role**: Cache employee profile queries to reduce DB hits for recurrent lookups.
- **Key Schema**:
  - Profile cache: `employee:profile:<id>`
  - Department listings: `department:employees:<dept_id>`

### C. Messaging Queue (RabbitMQ)
- **Engine**: RabbitMQ 3 (Alpine)
- **Role**: Asynchronous payroll calculation and contract generation.
- **Work Flow**:
  1. Admin requests payroll generation for a department via API.
  2. Spring Boot controller publishes a payroll task JSON to RabbitMQ `hr.payroll` queue.
  3. A background `@RabbitListener` worker consumes the message, runs the calculations, writes results to PostgreSQL, and invalidates the cached employee payroll status in Redis.

---

## 3. Docker Compose Setup

Services definition:
- `db`: PostgreSQL container with named volume `hr_db_data`.
- `redis`: Redis server container.
- `rabbitmq`: RabbitMQ message broker.
- `web`: Spring Boot jar-packed application container (port 8006).

### Environment Configuration (`.env`)
```env
SPRING_DATASOURCE_URL=jdbc:postgresql://db:5432/hr_management
SPRING_DATASOURCE_USERNAME=postgres
SPRING_DATASOURCE_PASSWORD=cyberpunk_hr_pass
SPRING_REDIS_HOST=redis
SPRING_REDIS_PORT=6379
SPRING_RABBITMQ_HOST=rabbitmq
SPRING_RABBITMQ_PORT=5672
```

---

## 4. Impact on Planted Vulnerabilities
We must maintain vulnerability fidelity:
- **VULN-01 (A01 - IDOR)**: Employee details are fetched by `id`. The Redis caching layer for `employee:profile:<id>` must cache the deserialized profile directly without verifying the requesting HR manager's authority, keeping the IDOR exploitable from the cache.
- **VULN-02 (A02 - Cryptographic Failures)**: Weak XOR encryption or hardcoded symmetric keys used to encrypt employee tax details (SSNs) must remain in the code. The encrypted data will be saved to the new PostgreSQL database, demonstrating how weak encryption impacts persistent databases.
- **VULN-03 (A08 - Software and Data Integrity Failures)**: The object deserialization endpoint receives raw Java serialized objects. The vulnerability remains in the Spring Boot endpoint, allowing attackers to exploit standard gadgets (e.g. CommonsCollections) to achieve remote code execution in the container.
- **Chain-01 (Weak Crypto → IDOR → Employee Record Leak)**: Attacker decrypts encrypted tax identifiers, iterates employee records via IDOR, and extracts the database records.
- **Chain-02 (State Confusion Pivot to IDOR)**: Attacker combines state changes in background payroll task queues to bypass authorization or extract records.
