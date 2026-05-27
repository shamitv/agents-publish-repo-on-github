# App 01 — E-Commerce Product Catalog API

## Overview

A multi-service e-commerce platform built with **Flask** (Python) and a **React + TypeScript** supplier portal. The system is organized as a monorepo with three independent microservices sharing domain packages and utilities.

This application is built for security-agent benchmarking and evaluation purposes.

---

## Business Domain

**Retail / E-Commerce** — Used by customers to search/browse items, add them to a cart, and place orders. Used by catalog managers (Admins) to register inventory products. Suppliers can generate reports and view KPIs via the supplier portal.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.x, Flask (3 microservices) |
| Frontend | React 18 + TypeScript (Vite), vanilla JS SPA |
| Database | SQLite fallback with PostgreSQL/MongoDB integration surfaces |
| Search / MQ | Elasticsearch query client, Kafka-style event publisher/consumers |
| Containerisation | Docker, Docker Compose |

---

## Architecture

The application is structured as a monorepo under `apps/python/app-01-ecommerce-catalog/`:

```
services/
  catalog-service/         # Product catalog, orders, auth, lifecycle
  reporting-service/       # Report generation, caches, scheduler, webhooks
  supplier-portal-api/     # Supplier-facing report endpoints
packages/
  domain/                  # Shared DTOs, enums, validation rules
  utils/                   # Pagination, response formatting
```

A companion TypeScript/React supplier portal lives at `apps/typescript/app-01-supplier-portal/`.

## Features

### Product Catalog
- Browse items catalog, SKU records, pricing, and descriptions
- Filter products dynamically using instant catalog search boxes
- Add items to custom baskets

### Order Processing
- Perform checkouts and submit orders
- View historical purchase summaries

### Supplier Reporting
- Generate sales, inventory health, and data quality reports
- Dashboard with KPI summary
- Report list per supplier

### Admin
- Cache management, feature flags, webhook registry
- Product lifecycle management (draft/review/publish/archive)
- Bulk CSV product upload

## Security Benchmarking

This app intentionally contains benchmark vulnerabilities. Machine-readable ground truth is in [.vulns](.vulns).

---

## Chained Vulnerability Scenario

### Chain: "User Enumeration -> Session Forgery -> Catalog Modification"

An attacker confirms the admin account, forges an admin session, and writes unauthorized catalog changes.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Username existence endpoint confirms privileged account names without authentication | Low | A01 | `src/controllers/user_controller.py` -> `user_exists()` |
| 2 | Hardcoded Flask signing secret enables forged admin session cookies | Medium | A02 | `src/config/settings.py` -> `SECRET_KEY` |
| 3 | Product mutation trusts the forged admin session role | Medium | A01 | `src/controllers/product_controller.py` -> `create_product()` |

**Attack narrative**: The attacker probes `/api/users/exists?username=admin` to confirm the admin account exists. They use the hardcoded Flask `SECRET_KEY` in source to craft a valid signed session cookie with admin claims, then call `POST /api/products` to add or overwrite catalog data without knowing any password.

**Combined Impact**: Unauthorized catalog data modification through forged administrator access.

---

### Chain: "Weak Supplier ID Validation -> Catalog Poisoning via Bulk Upload"

An attacker chains weak validation with a trusting bulk upload endpoint to modify catalog data under a forged supplier identity.

| Step | Issue | Severity (standalone) | OWASP | Location |
|------|-------|-----------------------|-------|----------|
| 1 | Supplier ID validator accepts zero, negative, and non-numeric values | Low | A04 | `packages/domain/validators.py` -> `validate_supplier_id_chain()` |
| 2 | Bulk CSV upload trusts `supplierId` from request body without ownership verification | Medium | A01 | `services/catalog-service/src/controllers/bulk_upload_controller.py` -> `bulk_upload_products()` |

**Attack narrative**: The attacker crafts a CSV file with `supplierId` set to a different supplier's ID. The weak validator passes it through (step 1), and the bulk upload endpoint creates products under the forged identity without verifying the authenticated supplier owns that ID (step 2).

**Combined Impact**: Unauthorized catalog data modification through forged supplier identity.

---

## API Endpoints

### Catalog Service (port 8081)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | — | Serves the client-side SPA portal |
| POST | `/api/auth/login` | — | Authenticates and establishes session |
| POST | `/api/auth/logout` | — | Terminates active portal session |
| GET | `/api/auth/me` | ANY | Retrieves authenticated user profile |
| GET | `/api/users/exists` | — | Checks if a username is registered (chain link) |
| GET | `/api/user/profile` | ANY | Retrieves the current user's own profile |
| GET | `/api/health` | — | Health and integration surface check |
| GET | `/api/products` | — | Lists product items (supports search queries) |
| POST | `/api/products` | ADMIN+ | Add a new product to the catalog |
| GET | `/api/orders` | ANY | Lists user checkouts history |
| POST | `/api/orders` | ANY | Processes basket checkout and creates order |
| GET | `/api/orders/{id}` | ANY | View individual order detail fields |
| POST | `/api/products/bulk-upload` | SUPPLIER+ | CSV bulk product upload (chain link) |
| POST | `/api/products/{productId}/lifecycle/{action}` | ADMIN+ | Advance product lifecycle state |
| GET | `/api/products/{productId}/lifecycle` | ANY | View lifecycle history |
| GET | `/api/products/my-products` | SUPPLIER+ | List own products (decoy, scoped to session) |

### Reporting Service (port 5002)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | — | Health check |
| GET | `/v1/reports/definitions` | — | List available report types |
| GET | `/v1/reports/sales` | — | Sales report aggregation |
| GET | `/v1/reports/inventory-health` | — | Inventory health report |
| GET | `/v1/reports/data-quality` | — | Data quality scorecard |
| POST | `/admin/cache/clear` | — | Clear report cache |
| POST | `/admin/cache/restore` | — | Restore cache from disk |
| POST | `/admin/flags` | — | Set feature flag |
| POST | `/admin/schedules` | — | Create scheduled report |
| POST | `/admin/webhooks/deliver` | — | Trigger webhook delivery |

### Supplier Portal API (port 5003)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | — | Health check |
| POST | `/portal/auth/login` | — | Supplier login (vulnerability A07) |
| GET | `/portal/auth/verify` | SUPPLIER+ | Verify session token (decoy) |
| GET | `/portal/dashboard` | — | KPI summary dashboard |
| GET | `/portal/reports` | — | List supplier's reports |
| GET | `/api/supplier/reports/{report_id}` | — | Generate supplier report |
| GET | `/api/supplier/reports/{report_id}/safe` | — | Generate scoped report (decoy) |

---

## Running Locally

```bash
cd apps/python/app-01-ecommerce-catalog
pip install -r requirements.txt
python app.py
# Frontend served at http://localhost:8081
```

## Running via Docker

```bash
docker compose up --build
```
