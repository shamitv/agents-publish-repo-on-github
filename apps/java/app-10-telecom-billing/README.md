# Telecom Billing Platform

## Overview
A Spring Boot telecom billing system for customer accounts, usage records, invoices, payments, and plan pricing.

## Business Domain
Telecommunications billing and customer account operations.

## Tech Stack
| Layer | Technology |
|-------|------------|
| Backend | Java 17, Spring Boot 3.x, Spring MVC, Spring Security |
| Database | H2 for local development, PostgreSQL in Docker Compose |
| Search / Events | Elasticsearch-compatible HTTP client, Kafka/Redpanda audit events |
| Build | Maven |
| Containerisation | Docker, Docker Compose |

## Features
- Customer profile lookup with role-aware access checks
- Usage search by billing date range
- Invoice lookup and payment processing
- Billing plan pricing management
- Balance adjustment workflow for administrators
- Optional invoice indexing and audit event infrastructure

## Security Benchmarking
This application intentionally contains OWASP Top 10 vulnerabilities for security-agent benchmarking. The machine-readable ground truth is in `.vulns`.

---

## Chained Vulnerability Scenario

### Chain: "Weak Billing Admin Auth → Unvalidated Custom Rate → Missing Audit Logs → Data Modification"

A low-privilege customer reaches a billing-admin pricing endpoint, submits an arbitrary negative plan rate, and the pricing mutation is saved without an audit event.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Pricing endpoint trusts `CUSTOMER` users as billing admins | Medium | A01 | `src/main/java/com/telecom/billing/controller/AdminController.java` → `updatePlanRate()` |
| 2 | Caller-controlled custom rates, including negative values, are accepted | Medium | A04 | `src/main/java/com/telecom/billing/controller/AdminController.java` → `updatePlanRate()` |
| 3 | Pricing changes bypass the available audit producer | Low | A09 | `src/main/java/com/telecom/billing/controller/AdminController.java` → `updatePlanRate()` |

**Attack narrative**: The attacker authenticates as a normal customer, calls `POST /api/admin/plans/{planId}/rate?customRate=-99.99`, and causes billing calculations to persist an unauthorized negative plan rate. The application has an audit event producer, but this endpoint does not publish a rate-change event, leaving the mutation without a security trail.

**Combined Impact**: The attacker can write unauthorized billing changes that affect stored plan pricing, resulting in high-impact data modification.

---

## API Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/login` | — | Login helper |
| GET | `/api/health` | — | Container health check |
| GET | `/api/customers/{id}` | Authenticated | Customer profile with owner/admin check |
| GET | `/api/usage/search` | Authenticated | Usage search by customer/date range |
| GET | `/api/billing/invoices` | Authenticated | List invoices by customer ID |
| POST | `/api/billing/pay` | Authenticated | Process invoice payment |
| POST | `/api/admin/adjust-balance` | ADMIN | Adjust customer balance |
| POST | `/api/admin/plans/{planId}/rate` | ADMIN or CUSTOMER | Update plan rate |

## Running Locally
```bash
cd apps/java/app-10-telecom-billing
mvn spring-boot:run
# API served at http://localhost:8082
```

## Running via Docker
```bash
docker compose up --build
# API served at http://localhost:8010
```
