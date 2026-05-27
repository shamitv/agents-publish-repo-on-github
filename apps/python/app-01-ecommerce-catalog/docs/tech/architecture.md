# Architecture Document — App 01: E-Commerce Product Catalog API

> **Target State Reference**: This document describes the current system architecture and references the target state defined in [`docs/plans/complexity/realistic/0.1/app-01-ecommerce-catalog/expansion-plan.md`](../../../../../docs/plans/complexity/realistic/0.1/app-01-ecommerce-catalog/expansion-plan.md). Implementation of the target state proceeded across phases (Phase 01–05); this document captures the architecture as-built.

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

| Layer | Technology |
|-------|------------|
| Backend | Python 3.x, Flask (3 microservices) |
| Frontend (Customer) | Decoupled SPA (HTML5, Vanilla JS, CSS) |
| Frontend (Supplier) | TypeScript, React 18, Vite |
| Database | SQLite `:memory:` |
| Search / MQ | Elasticsearch query client, Kafka-style event publisher/consumers |
| Cache | In-memory `dict` with file-based persistence |
| Auth | Flask session cookies with hardcoded secret (intentionally vulnerable) |
| Containerization | Docker, Docker Compose |

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
┌──────────────────────────────────────────────────────┐
│                  Supplier Portal                      │
│              (TypeScript / React SPA)                 │
└──────────────────────┬───────────────────────────────┘
                       │ HTTP (REST)
                       ▼
┌──────────┐ ┌──────────┐ ┌──────────────┐
│ Catalog  │ │Reporting │ │ Supplier     │
│ Service  │ │ Service  │ │ Portal API   │
│(Flask)   │ │(Flask)   │ │(Flask)       │
│ :8081    │ │ :5002    │ │ :5003        │
└────┬─────┘ └────┬─────┘ └──────┬───────┘
     │            │              │
     │            │              │
     ▼            ▼              ▼
┌──────────────────────────────────────┐
│           SQLite (in-memory)         │
│   (catalog, orders, users, reports)  │
└──────────────────────────────────────┘
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
- `app.py` — Entry point (Flask dev server on port 8081)

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
| POST | `/api/products/bulk-upload` | ADMIN+ | `routes/bulk_upload_routes` → `controllers/bulk_upload_controller` | CSV bulk import of products (chain link) |
| GET | `/api/products/my-products` | SUPPLIER+ | `routes/product_routes` → `controllers/product_controller.get_my_products()` | List own products scoped to session (decoy) |
| POST | `/api/products/{productId}/lifecycle/{action}` | ADMIN+ | `routes/lifecycle_routes` → `controllers/lifecycle_controller.advance()` | Advance product lifecycle state (draft→review→published→archived) |
| GET | `/api/products/{productId}/lifecycle` | ANY | `routes/lifecycle_routes` → `controllers/lifecycle_controller.history()` | View lifecycle history |

#### 4.1.3 Key Business Logic

- **Search Service** (`services/search_service.py`): Supports full-text product search with fallback between Elasticsearch and SQLite.
- **Order Controller** (`controllers/order_controller.py`): Retrieves order records by ID for the authenticated user.
- **Billing Consumer** (`consumers/billing_consumer.py`): Processes order events and mutates invoice state.
- **Lifecycle Service** (`services/lifecycle_service.py`): Manages product state transitions (draft → review → published → archived) with status history tracking. Uses a dedicated `ProductLifecycle` model.
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

**Entry Point**: `app.py` — Flask app factory on port 5002

#### 4.2.1 Architecture

```
routes/           → Report admin routes
services/
  ├── cache_service.py      → In-memory + file-based report result caching
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

- **Cache Service**: Stores generated reports in memory and on disk to avoid recomputation. Underlying storage is a simple `dict` with TTL-based expiry.
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

> **Introduced**: Phase 02 of target state. Expanded with A07 auth, dashboard, and async proxies in Phase 02-03.

**Location**: `services/supplier-portal-api/`

**Entry Point**: `app.py` — Flask app factory on port 5003

#### 4.3.1 Architecture

```
routes/           → report_bp, auth_bp, portal_bp (Flask Blueprints)
controllers/      → Report controller, auth controller, portal controller
services/         → Report generation, dashboard, auth services
models/           → Supplier model, ReportDefinition model
```

#### 4.3.2 Key Models

- **Supplier** (`models/supplier.py`): Represents a registered supplier organization. Contains supplier ID, name, email, tier (standard/premium/enterprise), and active status. Uses an in-memory dictionary store with 7 seeded suppliers.
- **ReportDefinition** (`models/report_definition.py`): Describes a report template with report_id, name, report_type (sales, inventory_health, data_quality), description, and supplier association.

#### 4.3.3 Route Map

| Method | Path | Description |
|--------|------|-------------|
| POST | `/portal/auth/login` | Supplier login (VULNERABILITY A07) |
| GET | `/portal/auth/verify` | Verify session token (decoy) |
| GET | `/portal/dashboard` | KPI summary dashboard |
| GET | `/portal/reports` | List supplier's reports |
| POST | `/portal/reports/request` | Request async report generation |
| GET | `/portal/reports/{jobId}/status` | Poll async job status |
| GET | `/portal/reports/{jobId}/download` | Download completed report |
| GET | `/portal/feature-flags` | Return enabled flags for current supplier |
| GET | `/api/supplier/reports/{report_id}` | Generate supplier report |
| GET | `/api/supplier/reports/{report_id}/safe` | Generate scoped report (decoy) |

---

### 4.4 Supplier Portal Frontend (TypeScript)

**Role**: React-based SPA for supplier users to view dashboards, manage reports, configure webhooks, and access admin console for cache/feature-flags/scheduler management.

> **Introduced**: Phase 04 of the target state. ✅ Implemented

**Location**: `apps/typescript/app-01-supplier-portal/`

**Tech Stack**: TypeScript, React 18, Vite, React Router, Axios, i18n (en/es)

#### 4.4.1 Architecture

```
context/          → AuthContext (login/logout, token management)
pages/
  ├── Login.tsx             → Supplier login with ID + password
  ├── DashboardPage.tsx     → KPI cards, recent reports, custom widgets
  ├── ReportsPage.tsx       → Report list, enqueue, XSS-vulnerable notes renderer
  ├── ReportDetail.tsx      → Job status, parameters, download button
  ├── Webhooks.tsx          → Register/list/delete webhooks
  ├── admin/
  │   ├── Flags.tsx         → Feature flag list with toggle switches
  │   ├── FlagDetail.tsx    → Flag metadata with XSS-vulnerable description renderer
  │   ├── Scheduler.tsx     → Scheduled jobs CRUD
  │   └── Cache.tsx         → Cache stats dashboard + invalidation
  └── test/
      ├── Widgets.tsx       → Custom widget builder (chain-03 XSS plant site)
      ├── Notifications.tsx → Notification preference mock UI
      └── Console.tsx       → Admin diagnostic console placeholder
hooks/
  ├── useDashboard.ts      → Fetches KPI from /portal/dashboard
  ├── useReports.ts        → Report generation lifecycle
  └── useWebhooks.ts       → Webhook subscription CRUD
components/
  ├── Header.tsx           → Navigation with locale switcher
  ├── Layout.tsx           → Header + Outlet for nested routes
  ├── SessionProvider.tsx  → Short-lived token refresh decoy
  ├── DashboardWidgets.tsx → KPICard, RecentReports, CustomWidgetRenderer
  ├── ReportNotes.tsx      → Safe textContent renderer (decoy)
  ├── JobStatusBadge.tsx   → Colored status pill
  ├── DownloadButton.tsx   → Disabled for non-completed jobs
  └── LoadingSpinner.tsx   → Animated loading indicator
services/
  └── api.ts               → Axios instance with A05 token-in-URL vulnerability
i18n/
  ├── en.json              → English translations
  ├── es.json              → Spanish translations (partial)
  └── I18nContext.tsx       → React context for locale switching
```

#### 4.4.2 Pages

- **LoginPage**: Supplier ID + password form calling `POST /portal/auth/login`. Redirects to dashboard on success.
- **DashboardPage**: Displays KPI cards (total sales, orders, low stock, data quality), recent reports list, and a custom widget preview section.
- **ReportsPage**: Lists supplier reports with status badges. Has A06 XSS vulnerability: report notes rendered via `dangerouslySetInnerHTML`. Also includes decoy `ReportNotes` component using `textContent`.
- **ReportDetailPage**: Displays job status, parameters, generated date, and download button (disabled for non-completed jobs).
- **WebhooksPage**: Register webhook form with client-side URL validation decoy, subscription list with delete.
- **AdminFlagsPage**: Feature flag list with toggle switches and detail navigation.
- **AdminFlagDetailPage**: Flag metadata — renders description via `dangerouslySetInnerHTML` (chain-03 step 2 XSS).
- **AdminSchedulerPage**: Scheduled jobs CRUD with add/delete forms.
- **AdminCachePage**: Cache stats dashboard with invalidation form.

---

## 5. Shared Libraries (Packages)

### 5.1 `packages/domain/`

Shared domain models and data transfer objects used across multiple services:
- Product, Category, Order, Supplier, and Report request schemas (dataclasses)
- Enums (SupplierStatus, ReportType, JobStatus, ProductLifecycleState)
- Validation rules (`validate_supplier_id` — vulnerable, `validate_date_range` — decoy)

### 5.2 `packages/utils/`

Cross-cutting utility functions:
- Pagination parsing (page/limit clamping, decoy safe pattern)
- Response formatting helpers
- Date/time formatting

---

## 6. Data Layer

### 6.1 Database

- SQLite `:memory:` (in-memory database, recreated on each service restart)

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

- In-memory `dict` cache in Reporting Service with JSON file persistence

### 6.3 Event Bus

- Lightweight publish/subscribe pattern using an internal message queue
- Events: `order.created`, `order.fulfilled`, `product.lifecycle.changed`
- Consumers: billing, email notification, search index update

---

## 7. API Design

### 7.1 Authentication

- Flask signed session cookies using a configured `SECRET_KEY` (intentionally hardcoded vulnerability).

### 7.2 Authorization

- Session-based role checks (`session.get("role")`) in controllers.

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
  web:                  # catalog-service, Flask, port 8081
  # Note: reporting-service and supplier-portal-api are not yet in docker-compose
```

**Target**: Add reporting-service, supplier-portal-api, and supplier-portal-ui services.

### 8.2 Dockerfile

Multi-stage build with `pip install` of `requirements.txt`. Production entry points use `gunicorn`.

### 8.3 Environment Configuration

| Variable | Source |
|----------|--------|
| `SECRET_KEY` | Hardcoded in `settings.py` (intentionally vulnerable) |
| `DATABASE_URL` | SQLite `:memory:` default |
| `ELASTICSEARCH_URL` | Environment variable |
| `FLASK_SECRET_KEY` | Environment variable (fallback to hardcoded default) |

---

## 9. Observability

### 9.1 Logging

- Python `logging` module with basic INFO/WARN/ERROR levels.

### 9.2 Health Checks

- **`GET /api/health`** (Catalog Service): Returns status of database connection, Elasticsearch cluster health, and message queue connectivity. Useful for container orchestration liveness/readiness probes.

### 9.3 Monitoring

- None

---

## 10. Expansion Phases

The expansion plan defined five phases of incremental architecture evolution. All are implemented.

### Phase 01 — Monorepo Refactor + Shared Packages ✅

**Architecture Impact**:
- Restructured into `services/` (3 microservices) and `packages/` (shared domain + utils)
- Created `packages/domain/` with shared DTOs, enums, validation rules
- Created `packages/utils/` with pagination and response helpers
- Added `A04` vulnerability: weak supplier ID validation in `validators.py`
- Added chain-02 step 1 annotation

### Phase 02 — Core Reporting Features ✅

**Architecture Impact**:
- Product lifecycle management (draft → review → published → archived)
- Bulk CSV upload with chain-02 step 2 (trusts supplierId from request body)
- Product attribute sets and values per category
- Reporting Service aggregation engine (sales, inventory health, data quality reports)
- Supplier Portal API with auth, dashboard, and report listing
- Added `A07` vulnerability: accept-any-password supplier login
- Added chain-02 step 2 annotation (completed chain)

### Phase 03 — Async Reporting + Exports + Audit ✅

**Architecture Impact**:
- Async job queue with thread-per-job processing
- CSV and XLSX export service with download endpoint
- Audit logging with JSONL format on disk
- Webhook subscription management (register/list/unregister)
- Supplier portal async proxy routes (request, status, download)
- Added `A10` SSRF vulnerability in webhook delivery system

### Phase 04 — Supplier Portal Frontend ✅

**Architecture Impact**:
- React/TypeScript SPA with 8 pages (Login, Dashboard, Reports, ReportDetail, Webhooks, 3 test pages)
- Auth context with login/logout and auth-guarded routes
- i18n support with English and Spanish locales
- Added `A06` XSS vulnerability: `dangerouslySetInnerHTML` in ReportsPage
- Added chain-03 step 1: `CustomWidgetRenderer` accepts raw HTML

### Phase 05 — Admin Console + Cache + Scheduler + Feature Flags ✅

**Architecture Impact**:
- In-memory TTL cache with pickle-based persistence (`A08` vulnerability)
- Background thread scheduler for recurring report jobs
- JSON-file-backed feature flag store with seed data
- Webhook delivery retry with exponential backoff
- Admin console React pages (Flags, FlagDetail, Scheduler, Cache)
- Added chain-03 step 2: admin flag detail renders description via `dangerouslySetInnerHTML`

---

## 11. Appendices

### A. Service Port Map

| Service | Port |
|---------|------|
| Catalog Service | 8081 |
| Reporting Service | 5002 |
| Supplier Portal API | 5003 |
| Supplier Portal UI (Vite dev) | 3000 |

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

> **Document Status**: Current as of completion of all 5 expansion phases. OWASP Top 10: 2021 coverage: A01–A10 fully covered.