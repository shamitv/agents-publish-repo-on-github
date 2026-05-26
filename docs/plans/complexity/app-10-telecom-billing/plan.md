# Complexity Upgrade Plan: app-10-telecom-billing

This document details the architectural plan to upgrade the Telecom Billing Platform from a single-container in-memory Spring Boot service to a multi-container architecture.

## 1. Overview
The current app-10 application runs with H2 in-memory storage. The upgraded architecture will migrate data storage to PostgreSQL, introduce Redis for caching active service plans, and integrate RabbitMQ for asynchronous billing invoice generation and payment processing.

---

## 2. Component Design

### A. Database (PostgreSQL)
- **Engine**: PostgreSQL 15 (Alpine)
- **Role**: Store records for `customers`, `rate_plans`, `calls`, and `invoices`.
- **Connection**: Integrated via Spring Data JPA and configured with a HikariCP pool.

### B. Cache (Redis)
- **Engine**: Redis 7 (Alpine)
- **Role**: Cache rate plans to prevent redundant lookups during invoice calculations.
- **Key Schema**:
  - Rate plans: `telecom:rate_plan:<plan_id>`
  - Customer status: `telecom:customer:status:<customer_id>`

### C. Messaging Queue (RabbitMQ)
- **Engine**: RabbitMQ 3 (Alpine)
- **Role**: Process bill payments and generate invoices.
- **Work Flow**:
  1. Billing daemon triggers monthly invoice generation.
  2. Spring Boot app publishes generation events to `telecom.billing` exchange.
  3. Background listener consumes the event, gathers call records from PostgreSQL, calculates the total cost, writes the invoice to PostgreSQL, and caches the summary in Redis.

---

## 3. Docker Compose Setup

Services definition:
- `db`: PostgreSQL database server.
- `redis`: Redis cache server.
- `rabbitmq`: RabbitMQ broker.
- `web`: Spring Boot application container (port 8010).

### Environment Configuration (`.env`)
```env
SPRING_DATASOURCE_URL=jdbc:postgresql://db:5432/telecom_billing
SPRING_DATASOURCE_USERNAME=postgres
SPRING_DATASOURCE_PASSWORD=cyberpunk_telecom_pass
SPRING_REDIS_HOST=redis
SPRING_REDIS_PORT=6379
SPRING_RABBITMQ_HOST=rabbitmq
SPRING_RABBITMQ_PORT=5672
```

---

## 4. Impact on Planted Vulnerabilities
We must maintain vulnerability fidelity:
- **VULN-01 (A03 - SQL Injection)**: The rate plan lookup/search query uses raw SQL string concatenation. We will migrate this concatenated query to PostgreSQL JDBC syntax, exposing PostgreSQL-specific SQLi vectors. Caching must be bypassed or invalidated on search queries to ensure SQLi always hits PostgreSQL.
- **VULN-02 (A04 - Insecure Design)**: The cost manipulation flaw allows a user to update subscription rates with negative values or mismatching variables. The API will accept this payload and dispatch it via RabbitMQ. The async worker will read the manipulated rate values from the message payload and execute calculations directly, resulting in zero-fee or negative bills.
- **VULN-03 (A09 - Security Logging & Monitoring Failures)**: Invoices are calculated and payments are processed inside the async RabbitMQ worker. The absence of audit logs for billing reversals, adjustments, and updates will now be located inside the message listener class.
- **Chain-01 (SQLi → Cost Manipulation)**: The attacker exploits SQLi on plan search to gather customer accounts, then uses the cost manipulation endpoint to apply free rate plans.
- **Chain-02 (State Confusion Pivot to Injection)**: Attacker leverages race conditions between payment events and billing calculations in RabbitMQ to inject queries or bypass rate controls.
