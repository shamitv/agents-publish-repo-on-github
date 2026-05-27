# Architecture Document — App 01: E-Commerce Product Catalog API

> **Target State Reference**: This document describes the current system architecture and references the target state defined in [`docs/plans/complexity/realistic/0.1/app-01-ecommerce-catalog/expansion-plan.md`](../../../../../docs/plans/complexity/realistic/0.1/app-01-ecommerce-catalog/expansion-plan.md). Implementation of the target state proceeds across phases (Phase 01–07); this document captures the architecture as-built and calls out planned changes in callout blocks.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Principles](#2-architecture-principles)
3. [Service Architecture](#3-service-architecture)
4. [Service Details](#4-service-details)
    - [4.1 Catalog Service](#41-catalog-service)
    - [4.2 Reporting Service](#42-reporting-service)
    - [4.3 Supplier Portal API](#43-supplier-portal-api)
    - [4.4 Supplier Portal Frontend (TypeScript)](#44-supplier-portal-frontend-typescript)
5. [Shared Libraries (Packages)](#5-shared-libraries-packages)
6. [Data Layer](#6-data-layer)
7. [API Design](#7-api-design)
8. [Security Architecture](#8-security-architecture)
9. [Deployment Architecture](#9-deployment-architecture)
10. [Observability](#10-observability)
11. [Target State Evolution](#11-target-state-evolution)
12. [Appendices](#12-appendices)

---

## 1. System Overview

The E-Commerce Product Catalog API is a multi-service retail catalog and order fulfillment platform built with **Python (Flask)** and a decoupled **TypeScript (React)** supplier frontend. The system manages product inventories, customer orders, supplier relationships, and report generation across three backend microservices and one frontend application.

### 1.1 Business Domain

**Retail / E-Commerce** — Used by:
- **Customers** to browse/search items, manage carts, and place orders
- **Catalog Managers (Admins)** to register and maintain inventory products
- **Suppliers** to manage their product listings, configure webhooks, and generate reports

### 1.2 Tech Stack

| Layer | Technology | Target State |
|-------|------------|-------------|
| Backend | Python 3.x, Flask | Same (Phase 07 adds Go sidecar) |
| Frontend (Customer) | Decoupled SPA (HTML5, Vanilla JS, CSS) | Unchanged |
| Frontend (Supplier) | TypeScript, React, Vite | Phase 04 |
| Database | SQLite (dev), PostgreSQL/MongoDB integration surfaces | PostgreSQL production (Phase 03) |
| Search / MQ | Elasticsearch query client, Kafka-style event publisher/consumers | Same |
| Cache | — | Redis cache tier (Phase 06) |
| Config | — | Etcd config store (Phase 07) |
| Auth | Flask session cookies with hardcoded secret | JWT + Auth0 (Phase 05) |
| Containerization | Docker, Docker Compose | Docker Compose with API gateway (Phase 05) |

---

## 2. Architecture Principles

- **Microservice decomposition by domain**: Catalog, Reporting, Supplier Portal — each independently deployable.
- **Shared domain packages**: Common data models and utilities extracted into `packages/domain` and `packages/utils` to avoid duplication.
- **Blueprint-based Flask modularity**: Each service uses Flask blueprints to separate route, controller, service, and model layers.
- **Event-driven integration**: A lightweight Kafka-style publisher/consumer pattern connects order events across services.
- **Decoy-safe code patterns**: Parameterized queries and session-bound lookups are intentionally placed near vulnerable code to benchmark detection-agent precision.

---

## 3. Service Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Supplier Portal                              │
│                    (TypeScript / React SPA)                         │
└──────────────────────┬──────────────────────────────────────────────┘
                       │ HTTP (REST)
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                        API Gateway                                  │
│                     (Target: Phase 05)                              │
│          JWT validation, tenant context injection, rate-limit       │
└────┬──────────────┬──────────────┬──────────────────┬───────────────┘
     │              │              │                  │
     ▼              ▼              ▼                  ▼
┌──────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────────────┐
│ Catalog  │ │Reporting │ │ Supplier     │ │ Notification     │
│ Service  │ │ Service  │ │ Portal API   │ │ Service          │
│(Flask)   │ │(Flask)   │ │(Flask)       │ │(Target: Phase 04)│
│ :5001    │ │ :5003    │ │ :5002        │ │ :5004            │
└────┬─────┘ └────┬─────┘ └──────┬───────┘ └──────────────────┘
     │            │              │
     │            │              │
     ▼            ▼              ▼
┌─────────────────────────────────────┐
│         PostgreSQL / SQLite         │
│  (catalog, orders, users, reports)  │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  Redis Cache (Target: Phase 06)     │
│  (session store, rate-limit buckets)│
└─────────────────────────────────────┘
```

---

## 4. Service Details

### 4.1 Catalog Service

**Role**: Primary product catalog and order fulfillment service. Handles customer-facing product browsing, cart/checkout, and order lifecycle.

**Location**: `services/catalog-service/`

**Entry Point**:
- `app.py` — Development entry point (Flask dev server on port 8081)
- `src/main.py` — `create_app()` factory for production use

#### 4.1.1 Layer Architecture

```
routes/           → Flask Blueprints (HTTP routing)
controllers/      → Request handling, session/role validation
services/         → Business logic, search, MQ publishing, lifecycle
repositories/     → Data access (SQL, Elasticsearch)
models/           → SQLAlchemy ORM models, lifecycle models
config/           → Settings, DB initialization
consumers/        → Kafka-style event consumers (billing, email, search)
static/           → Customer-facing SPA (HTML, JS, CSS)
```

#### 4.1.2 Route Map

| Method | Path | Auth | Layer | Description |
|--------|------|------|-------|-------------|
| GET | `/` | — | `routes/page_routes` | Serves customer SPA |
| POST | `/api/auth/login` | — | `routes/auth_routes` → `controllers/auth_controller` | Authenticates user |
| POST | `/api/auth/logout` | — | `routes/auth_routes` → `controllers/auth_controller` | Terminates session |
| GET | `/api/auth/me` | ANY | `routes/auth_routes` → `controllers/auth_controller` | Returns current user profile |
| GET | `/api/users/exists` | — | `routes/user_routes` → `controllers/user_controller.user_exists()` | **CHAIN LINK 1**: Confirms username existence without auth |
| GET | `/api/user/profile` | ANY | `routes/user_routes` → `controllers/user_controller` | Returns authenticated user's profile (session-bound, decoy) |
| GET | `/api/health` | — | `routes/health_routes` | Health check with integration surface status |
| GET | `/api/products` | — | `routes/product_routes` → `services/search_service.search()` | **VULN-02**: Product search with SQL/ES injection surface |
| POST | `/api/products` | ADMIN+ | `routes/product_routes` → `controllers/product_controller.create_product()` | **CHAIN LINK 3**: Product creation trusting forged session role |
| GET | `/api/orders` | ANY | `routes/order_routes` → `controllers/order_controller` | Lists user order history |
| POST | `/api/orders` | ANY | `routes/order_routes` → `controllers/order_controller` | Processes checkout |
| GET | `/api/orders/{id}` | ANY | `routes/order_routes` → `controllers/order_controller.get_order_details()` | **VULN-01**: IDOR — returns any order by ID without ownership check |
| POST | `/api/products/bulk` | ADMIN+ | `routes/bulk_upload_routes` → `controllers/bulk_upload_controller` | CSV bulk import of products |
| POST | `/api/products/{id}/lifecycle` | ADMIN+ | `routes/lifecycle_routes` → `controllers/lifecycle_controller` | Product retire/restore/relist (Phase 01) |
| POST | `/api/products/{id}/lifecycle/batch` | ADMIN+ | `routes/lifecycle_routes` → `controllers/lifecycle_controller` | Batch lifecycle operations |

#### 4.1.3 Key Business Logic

- **Search Service** (`services/search_service.py`): Supports full-text product search with fallback between Elasticsearch and SQLite. User input is interpolated directly into query strings — **VULN-02 (A03: Injection)**.
- **Order Controller** (`controllers/order_controller.py`): Retrieves order records by ID without verifying the authenticated user's ownership — **VULN-01 (A01: IDOR)**.
- **Billing Consumer** (`consumers/billing_consumer.py`): Processes order events and mutates invoice state without structured audit logging — **VULN-03 (A09: Insufficient Logging)**.
- **Lifecycle Service** (`services/lifecycle_service.py`): Manages product state transitions (active → retired → restored → relisted) with status history tracking. Uses a dedicated `ProductLifecycle` model.

#### 4.1.4 Dependencies

```
SQLAlchemy (DB ORM)
Elasticsearch client (product search)
Flask-Session (signed cookie sessions)
Kafka-style publisher (event bus)
```

---

### 4.2 Reporting Service

**Role**: Asynchronous report generation and export service. Handles scheduled report jobs, caching, and webhook delivery of completed reports.

> **Introduced**: Phase 02 of the target state expansion. Extracted from the initial monolith to support supplier-facing reporting capabilities.

**Location**: `services/reporting-service/`

**Entry Point**: `src/main.py` — Flask app factory on port 5003

#### 4.2.1 Architecture

```
routes/           → Report admin routes
services/
  ├── cache_service.py      → In-memory + file-based report result caching
  ├── feature_flags.py      → Feature flag evaluation (Phase 06)
  ├── scheduler.py          → Cron-style job scheduling for reports
  └── webhook_retry.py      → Retry logic for webhook delivery failures
models/           → ReportJob model
controllers/      → Admin routes for report management
exports/          → Generated report output files (CSV, JSON)
```

#### 4.2.2 Key Components

- **Cache Service**: Stores generated reports in memory and on disk to avoid recomputation. Underlying storage is a simple `dict` — **Target: Redis-backed cache tier in Phase 06**.
- **Scheduler**: Manages periodic report generation jobs using a lightweight in-process scheduler. Supports cron expressions.
- **Webhook Retry**: Implements exponential backoff for delivering reports to supplier-configured webhook endpoints. Tracks delivery attempts and failures in the `ReportJob` model.
- **Feature Flags**: Evaluates boolean feature flags to control rollout of new report types — **Phase 06 addition**.
- **Admin Routes**: Provides internal endpoints for managing report jobs, clearing caches, and toggling feature flags.

---

### 4.3 Supplier Portal API

**Role**: Supplier-facing REST API for managing report generation, webhook configuration, and supplier profile data.

> **Introduced**: Phase 02 of target state. Expanded with supplier registration and webhook self-service in Phase 03.

**Location**: `services/supplier-portal-api/`

**Entry Point**: `src/main.py` — Flask app factory on port 5002

#### 4.3.1 Architecture

```
routes/           → report_bp (Flask Blueprint)
controllers/      → Report controller (triggers generation, returns status)
services/         → Report generation orchestration
models/           → Supplier model, ReportDefinition model
```

#### 4.3.2 Key Models

- **Supplier** (`models/supplier.py`): Represents a registered supplier organization. Contains contact info, API key hash, webhook configuration, and active status. — **Phase 03 registration support**.
- **ReportDefinition** (`models/report_definition.py`): Describes a report template including query parameters, output format, schedule (cron), and webhook URL.

#### 4.3.3 Route Map

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/supplier/reports/generate` | API Key | Triggers report generation |
| GET | `/api/supplier/reports/{id}` | API Key | Returns report status/download |
| GET | `/api/supplier/reports` | API Key | Lists supplier's reports |

---

### 4.4 Supplier Portal Frontend (TypeScript)

**Role**: React-based SPA for supplier users to view dashboards, manage reports, and configure webhooks.

> **Introduced**: Phase 04 of the target state.

**Location**: `apps/typescript/app-01-supplier-portal/`

**Tech Stack**: TypeScript, React 18, Vite, React Router, i18n (en/es)

#### 4.4.1 Architecture

```
pages/
  ├── DashboardPage.tsx    → Supplier dashboard with KPI cards
  └── ReportsPage.tsx      → Report list, generation, status tracking
hooks/
  ├── useDashboard.ts      → Fetches dashboard data from API
  └── useReports.ts        → Manages report generation lifecycle
services/
  └── api.ts               → HTTP client wrapping fetch
components/
  └── Header.tsx           → Navigation with i18n language switcher
i18n/
  ├── en.json              → English translations
  ├── es.json              → Spanish translations
  └── I18nContext.tsx       → React context for i18n
```

---

## 5. Shared Libraries (Packages)

### 5.1 `packages/domain/`

Shared domain models and data transfer objects used across multiple services:
- Product domain objects
- Order domain objects
- User models
- Supplier contracts

### 5.2 `packages/utils/`

Cross-cutting utility functions:
- Event publishing helpers (Kafka-style)
- Serialization/deserialization
- Date/time formatting
- Common validation routines

---

## 6. Data Layer

### 6.1 Database

- **Current**: SQLite (single file for dev), with PostgreSQL-ready schema patterns
- **Target**: PostgreSQL for production (Phase 03+)

#### Schema Groups

| Group | Tables | Service Owner |
|-------|--------|---------------|
| Catalog | products, categories, skus, prices | Catalog Service |
| Orders | orders, order_items, invoices | Catalog Service |
| Users | users, roles, sessions | Catalog Service |
| Lifecycle | product_lifecycle, lifecycle_history | Catalog Service |
| Reports | report_jobs, report_definitions, scheduled_reports | Reporting Service |
| Suppliers | suppliers, supplier_products, webhook_configs | Supplier Portal API |

### 6.2 Caching

- **Current**: In-memory `dict` cache in Reporting Service
- **Target**: Redis cache tier (Phase 06) for:
  - Report result caching
  - Session store
  - Rate-limit buckets
  - Product catalog hot cache

### 6.3 Event Bus

- Lightweight publish/subscribe pattern using an internal message queue
- Events: `order.created`, `order.fulfilled`, `product.lifecycle.changed`
- Consumers: billing, email notification, search index update

---

## 7. API Design

### 7.1 Authentication

- **Current**: Flask signed session cookies using `SECRET_KEY` — **CHAIN LINK 2**: The key is hardcoded in `src/config/settings.py`, enabling session forgery.
- **Target**: JWT-based auth with Auth0/OIDC provider (Phase 05) plus API key authentication for service-to-service calls.

### 7.2 Authorization

- **Current**: Session-based role checks (`session.get("role")`) in controllers. Inconsistent enforcement across endpoints.
- **Decoy**: User profile endpoint reads `session["user_id"]` instead of accepting an external ID parameter (safe pattern in `user_controller.profile`).
- **Target**: API Gateway enforces tenant isolation via JWT claims context (Phase 05).

### 7.3 API Conventions

- RESTful endpoints with JSON request/response bodies
- Blueprint-based route organization per domain
- Error responses follow `{"error": "<message>", "code": <int>}` shape
- Health endpoint (`/api/health`) reports status of database, Elasticsearch, and message queue connections

---

## 8. Security Architecture

### 8.1 Vulnerability Inventory

The application is an **intentionally vulnerable benchmark** for security detection agents. All vulnerabilities are real, exploitable code.

| ID | OWASP | CWE | Severity | Location | Description |
|----|-------|-----|----------|----------|-------------|
| VULN-01 | A01 | CWE-639 | High | `catalog-service/controllers/order_controller.get_order_details` | IDOR: order lookup without ownership check |
| VULN-02 | A03 | CWE-943 | High | `catalog-service/services/search_service.search` | SQL/ES injection via raw query string interpolation |
| VULN-03 | A09 | CWE-778 | Medium | `catalog-service/consumers/billing_consumer.process_order_event` | Order events processed without audit logging |

### 8.2 Chained Attack Scenario

**Chain**: User Enumeration → Session Forgery → Catalog Modification (`chain-01`)

| Step | OWASP | CWE | Severity | File | Description |
|------|-------|-----|----------|------|-------------|
| 1 | A01 | CWE-203 | Low | `user_controller.user_exists()` | Unauthenticated username confirmation endpoint |
| 2 | A02 | CWE-798 | Medium | `config/settings.SECRET_KEY` | Hardcoded Flask signing key enables forged cookies |
| 3 | A01 | CWE-862 | Medium | `product_controller.create_product()` | Product creation trusts forgeable session role |

**Attack Path**: `GET /api/users/exists?username=admin` (Step 1) → forge signed cookie with hardcoded key (Step 2) → `POST /api/products` with forged admin session (Step 3).

**Combined Impact**: Unauthorized catalog data modification (`data_modification`).

### 8.3 Decoy Patterns (False-Positive Traps)

| ID | Location | Pattern | Why Safe |
|----|----------|---------|----------|
| DECOY-01 | `user_repository.login()` | Parameterized SQL next to injection vuln | Uses `%s` placeholders with tuple args |
| DECOY-02 | `user_controller.profile()` | Reads user ID from session | Uses `session["user_id"]`, not request params |

### 8.4 Target State Security Additions

| Phase | Addition | Description |
|-------|----------|-------------|
| 05 | JWT Auth + API Gateway | Replaces vulnerable session cookies with JWT; gateway validates tokens and injects tenant context |
| 05 | Tenant Isolation | API Gateway enforces tenant-scoped access for multi-tenant supplier data |
| 07 | Rate Limiting | Per-tenant rate limits with token bucket algorithm |
| 07 | PKI Infrastructure | Service mesh with mTLS for service-to-service communication |
| 07 | Auditing | Structured audit log for all security-relevant events |

---

## 9. Deployment Architecture

### 9.1 Containerization

```yaml
# docker-compose.yml (current)
services:
  catalog-service:      # Flask, port 5001 → 8081
  reporting-service:    # Flask, port 5003
  supplier-portal-api:  # Flask, port 5002
  supplier-portal-ui:   # Vite dev server, port 5173 → 5173 (Phase 04)
```

**Target**: Add API Gateway (Envoy/Kong), Redis, Etcd, Notification Service, and change port mappings.

### 9.2 Dockerfile

Multi-stage build with `pip install` of `requirements.txt`. Production entry points use `gunicorn`.

### 9.3 Environment Configuration

| Variable | Current Source | Target Source |
|----------|---------------|---------------|
| `SECRET_KEY` | Hardcoded in `settings.py` | Environment variable (Phase 05) |
| `DATABASE_URL` | SQLite default | PostgreSQL (Phase 03) |
| `ELASTICSEARCH_URL` | Environment variable | Etcd config store (Phase 07) |
| `REDIS_URL` | — | Environment variable (Phase 06) |
| `ETCD_ENDPOINTS` | — | Environment variable (Phase 07) |

---

## 10. Observability

### 10.1 Logging

- **Current**: Python `logging` module with basic INFO/WARN/ERROR levels. No structured logging.
- **Target**: Structured JSON logging with correlation IDs (Phase 05).

### 10.2 Health Checks

- **`GET /api/health`**: Returns status of database connection, Elasticsearch cluster health, and message queue connectivity. Useful for container orchestration liveness/readiness probes.

### 10.3 Monitoring

- **Current**: None
- **Target**: Prometheus metrics endpoint + Grafana dashboards (Phase 07)

---

## 11. Target State Evolution

The expansion plan defines seven phases of incremental architecture evolution. Below is a summary of each phase and its architectural impact.

### Phase 01 — Product Lifecycle Management ✅ (Implemented)

**Architecture Impact**:
- Added `lifecycle_routes`, `lifecycle_controller`, `lifecycle_service` to Catalog Service
- Added `ProductLifecycle` and `LifecycleHistory` models
- New endpoints: `POST /api/products/{id}/lifecycle`, batch lifecycle operations

### Phase 02 — Reporting & Supplier Portal 🟡 (Partially Implemented)

**Architecture Impact**:
- Created **Reporting Service** (`services/reporting-service/`) as a new microservice
- Created **Supplier Portal API** (`services/supplier-portal-api/`) as a new microservice
- Report generation with scheduling, caching, and webhook delivery
- Supplier-facing report query endpoints

### Phase 03 — Supplier Registration & Webhook Self-Service 🔜

**Architecture Impact**:
- Supplier model with registration flows
- Webhook configuration CRUD for suppliers
- PostgreSQL migration from SQLite

### Phase 04 — Notification Service & Supplier Frontend 🔜

**Architecture Impact**:
- **Notification Service** (new microservice, port 5004) for email and in-app notifications
- **Supplier Portal Frontend** (TypeScript/React, `apps/typescript/app-01-supplier-portal/`)
- Dashboard with KPI cards and report management UI

### Phase 05 — Auth Isolation & API Gateway 🔜

**Architecture Impact**:
- **API Gateway** (Envoy or custom) in front of all services
- JWT authentication replacing Flask session cookies
- Tenant context injection for multi-tenant supplier isolation
- Hardcoded `SECRET_KEY` replaced with environment variable

### Phase 06 — Feature Flags & Redis Cache 🔜

**Architecture Impact**:
- **Redis** cache tier for report results, sessions, rate-limit buckets
- Feature flag system for gradual feature rollout
- Cache invalidation on product/order state changes

### Phase 07 — Config Store & Rate Limiting 🔜

**Architecture Impact**:
- **Etcd** distributed config store replacing environment variables
- Per-tenant rate limiting with token bucket algorithm
- PKI infrastructure for mTLS between services
- Structured audit logging and Prometheus metrics

---

## 12. Appendices

### A. Service Port Map

| Service | Internal Port | External Port (Host) |
|---------|---------------|---------------------|
| Catalog Service | 5001 | 8081 |
| Supplier Portal API | 5002 | — (internal) |
| Reporting Service | 5003 | — (internal) |
| Notification Service | 5004 (Phase 04) | — (internal) |
| Supplier Portal UI | 5173 | 5173 (Phase 04) |
| API Gateway | — | 8080 (Phase 05) |

### B. File Map

```
apps/python/app-01-ecommerce-catalog/
├── .vulns                              # Vulnerability manifest (machine-readable)
├── README.md                           # User-facing documentation
├── scenarios.md                        # Chained vulnerability attack narratives
├── reference_guards.py                 # Decoy safe-pattern references
├── docker-compose.yml                  # Service orchestration
├── Dockerfile                          # Multi-stage build
├── packages/
│   ├── domain/                         # Shared domain objects
│   └── utils/                          # Cross-cutting utilities
├── services/
│   ├── catalog-service/                # Core product catalog & orders
│   │   ├── app.py                      # Dev entry point
│   │   ├── requirements.txt
│   │   ├── static/                     # Customer SPA assets
│   │   └── src/
│   │       ├── main.py                 # create_app() factory
│   │       ├── config/                 # Settings, DB init
│   │       ├── routes/                 # Flask blueprints
│   │       ├── controllers/            # Request handlers
│   │       ├── services/               # Business logic
│   │       ├── repositories/           # Data access layer
│   │       ├── models/                 # ORM models
│   │       └── consumers/              # Event consumers
│   ├── reporting-service/              # Async report generation
│   │   └── src/
│   │       ├── main.py
│   │       ├── routes/
│   │       ├── services/               # Cache, scheduler, webhooks, feature flags
│   │       ├── controllers/
│   │       ├── models/                 # ReportJob
│   │       └── exports/                # Generated reports
│   └── supplier-portal-api/            # Supplier-facing API
│       └── src/
│           ├── main.py
│           ├── routes/
│           ├── controllers/
│           ├── services/               # Report generation orchestration
│           └── models/                 # Supplier, ReportDefinition
├── tests/
│   ├── test_app.py
│   └── test_modular_contract.py
└── docs/
    └── tech/
        └── architecture.md             # This document
```

### C. Glossary

| Term | Definition |
|------|------------|
| IDOR | Insecure Direct Object Reference — accessing a resource by ID without verifying authorization |
| Chain Link | An individual step in a multi-step vulnerability chain |
| Decoy | Safe code intentionally placed near vulnerable code to test detection-agent precision |
| Phase | A discrete implementation step in the target-state expansion plan |
| Tenant | A logically isolated supplier organization within the multi-tenant system |
| SPA | Single Page Application — client-side rendered web application |
| Blueprint | Flask's modular component pattern for organizing routes and views |

---

> **Document Status**: Current as of Phase 02 implementation. Updated to reflect target state defined in `docs/plans/complexity/realistic/0.1/app-01-ecommerce-catalog/expansion-plan.md`.