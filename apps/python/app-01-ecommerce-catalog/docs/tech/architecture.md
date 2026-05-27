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
8. [Deployment Architecture](#8-deployment-architecture)
9. [Observability](#9-observability)
10. [Target State Evolution](#10-target-state-evolution)
11. [Appendices](#11-appendices)

---

## 1. System Overview

The E-Commerce Product Catalog API is a multi-service retail catalog and order fulfillment platform built with **Python (Flask)** and a decoupled **TypeScript (React)** supplier frontend. The system manages product inventories, customer orders, supplier relationships, and report generation across three backend microservices and one frontend application.

### 1.1 Business Domain

**Retail / E-Commerce** — Used by:
- **Customers** to browse/search items, manage carts, and place orders
- **Catalog Managers (Admins)** to register and maintain inventory products, manage product lifecycles, and perform bulk uploads
- **Suppliers** to manage their product listings, configure webhooks, view dashboards, and generate reports
- **System Administrators** to manage cache, scheduler jobs, feature flags, and webhook retries via an admin console

### 1.2 Tech Stack

| Layer | Technology | Target State |
|-------|------------|-------------|
| Backend | Python 3.x, Flask | Same (Phase 07 adds Go sidecar) |
| Frontend (Customer) | Decoupled SPA (HTML5, Vanilla JS, CSS) | Unchanged |
| Frontend (Supplier) | TypeScript, React 18, Vite | Phase 04 ✅ Implemented |
| Database | SQLite (dev), PostgreSQL-ready schema patterns | PostgreSQL production (Phase 03) |
| Search / MQ | Elasticsearch query client, Kafka-style event publisher/consumers | Same |
| Cache | In-memory `dict` with file-based persistence | Redis cache tier (Phase 06) |
| Config | — | Etcd config store (Phase 07) |
| Auth | Flask session cookies with hardcoded secret | JWT + Auth0 (Phase 05) |
| Containerization | Docker, Docker Compose | Docker Compose with API gateway (Phase 05) |

---

## 2. Architecture Principles

- **Microservice decomposition by domain**: Catalog, Reporting, Supplier Portal — each independently deployable.
- **Shared domain packages**: Common data models and utilities extracted into `packages/domain` and `packages/utils` to avoid duplication.
- **Blueprint-based Flask modularity**: Each service uses Flask blueprints to separate route, controller, service, and model layers.
- **Event-driven integration**: A lightweight Kafka-style publisher/consumer pattern connects order events across services.
- **Async job subsystem**: Reporting service provides an enqueue/poll/download lifecycle for asynchronous report generation with webhook callbacks.
- **Admin console**: Reporting service exposes administrative endpoints for cache management, scheduler, feature flags, and webhook retry delivery.

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

### Inter-Service Communication

- **Synchronous**: RESTful HTTP calls between services for direct queries (e.g., Supplier Portal API calling Catalog Service for product data)
- **Asynchronous**: Kafka-style internal message queue for event-driven operations (e.g., `order.created` events consumed by billing, email, and search index consumers)
- **Webhook delivery**: Reporting Service delivers completed report notifications to supplier-configured webhook URLs via HTTP POST with exponential-backoff retry

---

## 4. Service Details

### 4.1 Catalog Service

**Role**: Primary product catalog and order fulfillment service. Handles customer-facing product browsing, cart/checkout, order lifecycle, product lifecycle management, and bulk upload.

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
| GET | `/api/users/exists` | — | `routes/user_routes` → `controllers/user_controller.user_exists()` | Confirms username existence |
| GET | `/api/user/profile` | ANY | `routes/user_routes` → `controllers/user_controller` | Returns authenticated user's profile (session-bound) |
| GET | `/api/health` | — | `routes/health_routes` | Health check with integration surface status |
| GET | `/api/products` | — | `routes/product_routes` → `services/search_service.search()` | Product search with text query |
| POST | `/api/products` | ADMIN+ | `routes/product_routes` → `controllers/product_controller.create_product()` | Creates a new product listing |
| GET | `/api/orders` | ANY | `routes/order_controller` | Lists user order history |
| POST | `/api/orders` | ANY | `routes/order_controller` | Processes checkout |
| GET | `/api/orders/{id}` | ANY | `routes/order_controller.get_order_details()` | Returns order details by ID |
| POST | `/api/products/bulk` | ADMIN+ | `routes/bulk_upload_routes` → `controllers/bulk_upload_controller` | CSV bulk import of products |
| POST | `/api/products/{id}/lifecycle` | ADMIN+ | `routes/lifecycle_routes` → `controllers/lifecycle_controller` | Product retire/restore/relist (Phase 01) |
| POST | `/api/products/{id}/lifecycle/batch` | ADMIN+ | `routes/lifecycle_routes` → `controllers/lifecycle_controller` | Batch lifecycle operations |

#### 4.1.3 Key Business Logic

- **Search Service** (`services/search_service.py`): Supports full-text product search with fallback between Elasticsearch and SQLite.
- **Order Controller** (`controllers/order_controller.py`): Retrieves order records by ID for the authenticated user.
- **Billing Consumer** (`consumers/billing_consumer.py`): Processes order events and mutates invoice state.
- **Lifecycle Service** (`services/lifecycle_service.py`): Manages product state transitions (active → retired → restored → relisted) with status history tracking. Uses a dedicated `ProductLifecycle` model.
- **Bulk Upload Controller** (`controllers/bulk_upload_controller.py`): Accepts CSV file uploads for batch product creation. Parses CSV rows and creates products via the service layer.

#### 4.1.4 Dependencies

```
SQLAlchemy (DB ORM)
Elasticsearch client (product search)
Flask-Session (signed cookie sessions)
Kafka-style publisher (event bus)
```

---

### 4.2 Reporting Service

**Role**: Asynchronous report generation and export service. Handles scheduled report jobs, caching, webhook delivery, feature flag management, and administrative operations including cache management, scheduler job orchestration, and webhook retry delivery.

> **Introduced**: Phase 02 of the target state expansion. Expanded with admin console, cache service, scheduler, feature flags, and webhook retry in Phase 05.

**Location**: `services/reporting-service/`

**Entry Point**: `src/main.py` — Flask app factory on port 5003

#### 4.2.1 Architecture

```
routes/           → Report admin routes
services/
  ├── cache_service.py      → In-memory + file-based report result caching
  │                          (Target: Redis-backed cache tier in Phase 06)
  ├── feature_flags.py      → Feature flag evaluation and management
  │                          (JSON-file-backed store with metadata support)
  ├── scheduler.py          → Cron-style job scheduling for reports
  │                          (in-process background thread)
  └── webhook_retry.py      → Retry logic for webhook delivery failures
                              (exponential backoff, delivery tracking)
models/           → ReportJob model
controllers/
  └── admin_routes.py       → Admin console endpoints for cache, scheduler,
                              feature flags, and webhook management
exports/          → Generated report output files (CSV, JSON)
```

#### 4.2.2 Key Components

- **Cache Service**: Stores generated reports in memory and on disk to avoid recomputation. Underlying storage is a simple `dict` with TTL-based expiry. Supports save/restore operations — **Target: Redis-backed cache tier in Phase 06**.
- **Feature Flag Store**: Manages boolean feature flags with metadata (description, owner) backed by a JSON file on disk. Provides CRUD operations and toggle support. Used to control rollout of new report types.
- **Scheduler**: Manages periodic report generation jobs using a lightweight in-process background thread. Supports interval-based scheduling with configurable task types and parameters.
- **Webhook Retry**: Implements exponential backoff for delivering reports to supplier-configured webhook endpoints. Tracks delivery attempts and failures with per-delivery status.
- **Admin Routes**: Provides endpoints for managing cache (stats, entries, invalidate, save, restore), scheduler jobs (list, add, get, delete, start, stop), feature flags (CRUD + toggle), and webhook deliveries (list, create, retry, view pending/failed).

#### 4.2.3 Admin Console Route Map

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/admin/cache/stats` | Cache hit/miss ratio and entry count |
| GET | `/api/admin/cache/entries` | List all cache entries with remaining TTL |
| POST | `/api/admin/cache/invalidate` | Invalidate cache entries matching a key pattern |
| POST | `/api/admin/cache/save` | Persist cache to disk (JSON) |
| POST | `/api/admin/cache/restore` | Restore cache from file (pickle format) |
| GET | `/api/admin/flags` | List all feature flags |
| POST | `/api/admin/flags` | Create a new feature flag |
| GET | `/api/admin/flags/<key>` | Get a single flag with metadata |
| POST | `/api/admin/flags/<key>/toggle` | Toggle a flag's enabled/disabled state |
| DELETE | `/api/admin/flags/<key>` | Delete a feature flag |
| GET | `/api/admin/scheduler/jobs` | List all scheduled jobs |
| POST | `/api/admin/scheduler/jobs` | Add a new recurring job |
| GET | `/api/admin/scheduler/jobs/<job_id>` | Get a single job's details |
| DELETE | `/api/admin/scheduler/jobs/<job_id>` | Delete a scheduled job |
| POST | `/api/admin/scheduler/start` | Start the scheduler background thread |
| POST | `/api/admin/scheduler/stop` | Stop the scheduler background thread |
| GET | `/api/admin/webhooks/deliveries` | List all webhook deliveries |
| POST | `/api/admin/webhooks/deliveries` | Create a webhook delivery to a URL |
| POST | `/api/admin/webhooks/deliveries/<id>/retry` | Retry a failed webhook delivery |
| GET | `/api/admin/webhooks/pending-failed` | List pending/failed deliveries |

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

- **Supplier** (`models/supplier.py`): Represents a registered supplier organization. Contains supplier ID, name, email, tier (standard/premium/enterprise), and active status. Uses an in-memory dictionary store with three seeded suppliers.
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

> **Introduced**: Phase 04 of the target state. ✅ Implemented

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

#### 4.4.2 Pages

- **DashboardPage**: Displays supplier KPI summary cards (total products, active orders, report count, pending webhooks). Fetches data via `useDashboard` hook → `/portal/dashboard` API.
- **ReportsPage**: Lists supplier's generated reports with status indicators. Supports triggering new report generation and navigating to report details. Uses `useReports` hook → `/portal/reports` API.

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

- **Current**: In-memory `dict` cache in Reporting Service with JSON file persistence
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

- **Current**: Flask signed session cookies using a configured `SECRET_KEY`.
- **Target**: JWT-based auth with Auth0/OIDC provider (Phase 05) plus API key authentication for service-to-service calls.
- **Supplier Portal API**: Uses simple API key authentication.

### 7.2 Authorization

- **Current**: Session-based role checks (`session.get("role")`) in controllers.
- **Target**: API Gateway enforces tenant isolation via JWT claims context (Phase 05).

### 7.3 API Conventions

- RESTful endpoints with JSON request/response bodies
- Blueprint-based route organization per domain
- Error responses follow `{"error": "<message>", "code": <int>}` shape
- Health endpoint (`/api/health`) reports status of database, Elasticsearch, and message queue connections

---

## 8. Deployment Architecture

### 8.1 Containerization

```yaml
# docker-compose.yml (current)
services:
  catalog-service:      # Flask, port 5001 → 8081
  reporting-service:    # Flask, port 5003
  supplier-portal-api:  # Flask, port 5002
  supplier-portal-ui:   # Vite dev server, port 5173 → 5173 (Phase 04)
```

**Target**: Add API Gateway (Envoy/Kong), Redis, Etcd, Notification Service, and change port mappings.

### 8.2 Dockerfile

Multi-stage build with `pip install` of `requirements.txt`. Production entry points use `gunicorn`.

### 8.3 Environment Configuration

| Variable | Current Source | Target Source |
|----------|---------------|---------------|
| `SECRET_KEY` | Hardcoded in `settings.py` | Environment variable (Phase 05) |
| `DATABASE_URL` | SQLite default | PostgreSQL (Phase 03) |
| `ELASTICSEARCH_URL` | Environment variable | Etcd config store (Phase 07) |
| `REDIS_URL` | — | Environment variable (Phase 06) |
| `ETCD_ENDPOINTS` | — | Environment variable (Phase 07) |

---

## 9. Observability

### 9.1 Logging

- **Current**: Python `logging` module with basic INFO/WARN/ERROR levels. No structured logging.
- **Target**: Structured JSON logging with correlation IDs (Phase 05).

### 9.2 Health Checks

- **`GET /api/health`** (Catalog Service): Returns status of database connection, Elasticsearch cluster health, and message queue connectivity. Useful for container orchestration liveness/readiness probes.

### 9.3 Monitoring

- **Current**: None
- **Target**: Prometheus metrics endpoint + Grafana dashboards (Phase 07)

---

## 10. Target State Evolution

The expansion plan defines seven phases of incremental architecture evolution. Below is a summary of each phase and its architectural impact, with current implementation status.

### Phase 01 — Product Lifecycle Management ✅ (Implemented)

**Architecture Impact**:
- Added `lifecycle_routes`, `lifecycle_controller`, `lifecycle_service` to Catalog Service
- Added `ProductLifecycle` and `LifecycleHistory` models
- New endpoints: `POST /api/products/{id}/lifecycle`, batch lifecycle operations

### Phase 02 — Reporting & Supplier Portal ✅ (Implemented)

**Architecture Impact**:
- Created **Reporting Service** (`services/reporting-service/`) as a new microservice
- Created **Supplier Portal API** (`services/supplier-portal-api/`) as a new microservice
- Report generation with scheduling, caching, and webhook delivery
- Supplier-facing report query endpoints
- Supplier model with in-memory store and tier-based differentiation (standard/premium/enterprise)

### Phase 03 — Supplier Registration & Webhook Self-Service 🔜

**Architecture Impact**:
- Supplier model with registration flows (partial: Supplier model exists in-memory)
- Webhook configuration CRUD for suppliers (partial: webhook delivery exists in admin routes)
- PostgreSQL migration from SQLite

### Phase 04 — Notification Service & Supplier Frontend ✅ (Partially Implemented)

**Architecture Impact**:
- **Supplier Portal Frontend** (TypeScript/React, `apps/typescript/app-01-supplier-portal/`) ✅ Implemented
  - Dashboard with KPI cards and report management UI
  - i18n support with English and Spanish locales
  - React hooks for data fetching (`useDashboard`, `useReports`)
- **Notification Service** (new microservice, port 5004) 🔜 Not yet implemented

### Phase 05 — Auth Isolation, API Gateway & Admin Console ✅ (Partially Implemented)

**Architecture Impact**:
- **Admin Console** in Reporting Service ✅ Implemented
  - Cache management endpoints (stats, entries, invalidate, save, restore)
  - Feature flag CRUD and toggle
  - Scheduler job management (list, add, get, delete, start, stop)
  - Webhook delivery management (list, create, retry, pending/failed)
- **Feature Flag System** ✅ Implemented
  - JSON-file-backed `FeatureFlagStore` with metadata support
  - Validation for flag keys
- **Scheduler** ✅ Implemented
  - In-process background thread with interval-based scheduling
  - Job lifecycle (add, get, delete, start, stop)
- **Webhook Retry** ✅ Implemented
  - Exponential backoff delivery with status tracking
- **API Gateway** 🔜 Not yet implemented
- **JWT Authentication** 🔜 Not yet implemented

### Phase 06 — Feature Flags & Redis Cache 🔜

**Architecture Impact**:
- **Redis** cache tier for report results, sessions, rate-limit buckets
- Cache invalidation on product/order state changes
- Feature flag system already in place; would be enhanced with remote evaluation

### Phase 07 — Config Store & Rate Limiting 🔜

**Architecture Impact**:
- **Etcd** distributed config store replacing environment variables
- Per-tenant rate limiting with token bucket algorithm
- PKI infrastructure for mTLS between services
- Structured audit logging and Prometheus metrics

---

## 11. Appendices

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
│   ├── reporting-service/              # Async report generation & admin console
│   │   └── src/
│   │       ├── main.py
│   │       ├── routes/
│   │       ├── services/
│   │       │   ├── cache_service.py    # In-memory + file cache
│   │       │   ├── feature_flags.py    # Flag store with metadata
│   │       │   ├── scheduler.py        # In-process job scheduler
│   │       │   └── webhook_retry.py    # Exponential backoff delivery
│   │       ├── controllers/
│   │       │   └── admin_routes.py     # Admin console endpoints
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
| SSRF | Server-Side Request Forgery — tricking a server into making requests to unintended locations |
| XSS | Cross-Site Scripting — injecting malicious scripts into web content |
| RCE | Remote Code Execution — executing arbitrary code on a remote system |
| TTL | Time-To-Live — the lifespan of a cache entry before it expires |
| Exponential Backoff | A retry strategy where wait time increases exponentially between attempts |

---

> **Document Status**: Current as of Phase 05 (Admin Console) implementation. Updated to reflect target state defined in `docs/plans/complexity/realistic/0.1/app-01-ecommerce-catalog/expansion-plan.md`.