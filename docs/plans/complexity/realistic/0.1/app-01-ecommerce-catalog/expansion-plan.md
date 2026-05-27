# App 01 (ecommerce-catalog) — Realistic Complexity Expansion Plan (v0.1)

## Overview

This plan describes how to dramatically increase the size and realism of **App 01 (E-Commerce Product Catalog API)** by adding supplier product reporting, a dedicated reporting microservice, an async job subsystem, i18n, audit logging, and a monorepo service architecture.

**Current app**: Python/Flask, 38 source files, 13 endpoints, Complexity: 5 (Very Complex)
**Target app**: Multi-service Python monorepo + TypeScript/React supplier portal, 120–150 source files

> **Non-goals / Constraints**
> - Do **not** remove or fix any intentionally planted vulnerability listed in [vuln-inventory.md](./vuln-inventory.md).
> - Add new code with realistic patterns, including **decoy safe code** near vulnerable-looking code.
> - Add 1–2 new standalone vulnerabilities + decoy patterns per phase. Extend/update `.vulns`, `README.md`, `scenarios.md` each phase.
> - Avoid introducing real external network dependencies in test code.
> - UI companion app uses **TypeScript + React (Vite)** and lives as a separate app under `apps/typescript/app-01-supplier-portal/`.

---

## Current State

| Property | Value |
|----------|-------|
| App ID | `app-01` |
| Language | Python |
| Framework | Flask |
| Current structure | Single `src/` with controllers, services, repositories, routes, config, consumers |
| Standalone vulns | 3 (A01 IDOR, A03 Injection, A09 Missing Logging) |
| Chain scenarios | 1 (chain-01: User Enumeration → Session Forgery → Catalog Modification) |
| Decoys | 2 (parameterized login query, session-based profile lookup) |
| OWASP gaps | A04, A05, A06, A07, A08, A10 uncovered |
| Full inventory | [vuln-inventory.md](./vuln-inventory.md) |

---

## Architecture Changes

### 1) Convert to a monorepo-style structure

Restructure under `apps/python/app-01-ecommerce-catalog/`:

```
apps/python/app-01-ecommerce-catalog/
  services/
    catalog-service/         # Existing product/category/order code refactored
    reporting-service/       # New: report definitions, generation, export
    supplier-portal-api/     # New: supplier-facing REST API
  packages/
    domain/                  # Shared DTOs, schemas, validation rules, enums
    utils/                   # Shared utilities (pagination, formatting)
  README.md
  .vulns
  scenarios.md
```

### 2) Separate service responsibilities

| Service | Responsibilities |
|---------|-----------------|
| **catalog-service** | Product/SKU/category CRUD, product lifecycle (draft/review/publish/archive), bulk upload, product media, bundles/kits |
| **reporting-service** | Report definitions, sync + async generation, aggregation pipelines, CSV/XLSX export, caching, audit logs, scheduled reports |
| **supplier-portal-api** | Supplier dashboards (KPI aggregation), report request/status/download endpoints, drill-down views |

### 3) TypeScript/React UI companion app

A new companion app under `apps/typescript/app-01-supplier-portal/`:

```
apps/typescript/app-01-supplier-portal/
  src/
    components/       # React components (Dashboard, ReportList, ReportDetail, etc.)
    hooks/            # Data fetching hooks
    i18n/             # Locale dictionaries + locale switcher
    pages/            # Page-level components
    services/         # API client layer
  package.json
  vite.config.ts
  tsconfig.json
```

### 4) Shared domain package (`packages/domain`)

Centralizes:
- Product attribute schemas (shared between catalog and reporting)
- Report request/response DTOs
- Validation rules (date ranges, supplierId format, filter constraints)
- Common enums (report types, metric types, status codes)

### 5) Async job subsystem for reporting

Reporting service supports:
- `POST /reports/jobs` — enqueue report generation
- `GET /reports/jobs/{id}` — poll job status
- `GET /reports/{jobId}/download` — download exports when ready
- Simulated webhook callback when jobs complete

### 6) i18n strategy

- `packages/i18n/` provides locale dictionaries (Python side for API messages)
- React UI has its own `i18n/` directory with locale dictionaries (`en`, `es`)
- Locale switcher in UI header
- API returns either localized strings or message keys that the UI maps

---

## Vulnerability Planting Strategy

### Target OWASP Coverage

| Phase | New OWASP Targeted | Rationale |
|-------|-------------------|-----------|
| 1 (Architecture) | A04 — Insecure Design | Weak validation in shared domain package |
| 2 (Core Features) | A07 — Identification & Auth Failures | Weak session handling in supplier portal API |
| 3 (Async + Exports) | A10 — SSRF | SSRF in webhook callback endpoint |
| 4 (UI + i18n) | A05 — Security Misconfiguration | CORS misconfiguration, missing security headers |
| 5 (Advanced) | A06 — Vulnerable Components, A08 — Integrity | Pinned vulnerable Flask version, deserialization in report import |

### Per-Phase Vulnerability Planting Summary

| Phase | Standalone Vulns Added | Chain Additions | Decoy Patterns |
|-------|----------------------|-----------------|----------------|
| 1 | 1 (A04) | 1 new chain (chain-02: Weak Validation → Catalog Poisoning) | Parameterized filters near vulnerable validation |
| 2 | 2 (A07, A01) | Extend chain-02 with step 3 (auth bypass) | Auth guards near vulnerable session handler |
| 3 | 1 (A10) | — | URL validation near SSRF endpoint |
| 4 | 1 (A05) | — | Proper CORS config in another blueprint |
| 5 | 2 (A06, A08) | — | Pinned safe version comment near vulnerable pin |

**Total new**: 7 standalone vulnerabilities, 1 new chain scenario, 1 extended chain scenario
**OWASP coverage after expansion**: A01–A10 fully covered

---

## Feature Inventory by Phase

### Phase 1 — Architecture Refactor + Shared Packages
- [ ] Monorepo directory restructure
- [ ] `packages/domain/` — shared DTOs, enums, validation rules
- [ ] `packages/utils/` — pagination, response formatting
- [ ] Move existing code into `services/catalog-service/`
- [ ] `services/catalog-service/` runs independently with its own `app.py`
- [ ] `services/reporting-service/` scaffold with health endpoint
- [ ] `services/supplier-portal-api/` scaffold with health endpoint
- [ ] Preserve all existing vulnerabilities per [vuln-inventory.md](./vuln-inventory.md)
- [ ] Scaffold `apps/typescript/app-01-supplier-portal/` (bare Vite + React project)

### Phase 2 — Core Reporting Features (MVP)
- [ ] Supplier entity + data model
- [ ] Report definition CRUD
- [ ] 3 report types: Sales Report, Inventory Health, Data Quality Score
- [ ] Synchronous aggregation endpoints
- [ ] Supplier portal API: dashboard KPI aggregation, report list
- [ ] Supplier portal API: basic RBAC (supplier sees own reports only)
- [ ] Decoy: parameterized queries near report filtering

### Phase 3 — Async Reporting + Exports + Audit
- [ ] Async report job queue (in-memory, simulated)
- [ ] Enqueue/poll/download lifecycle
- [ ] CSV export formatting
- [ ] XLSX export formatting
- [ ] Report audit log (access events)
- [ ] Audit log API endpoints
- [ ] Supplier portal API: job status + download endpoints

### Phase 4 — UI Expansion + i18n
- [ ] React supplier portal: Dashboard page
- [ ] React supplier portal: Reports list page
- [ ] React supplier portal: Report detail + drill-down
- [ ] React supplier portal: Export/download flow
- [ ] i18n: locale dictionaries (en, es)
- [ ] i18n: locale switcher component
- [ ] API message keys for i18n support

### Phase 5 — Advanced Features
- [ ] Caching for repeated report aggregations
- [ ] Scheduled report definitions (daily/weekly/monthly)
- [ ] Webhook registry (register/unregister callbacks)
- [ ] Simulated webhook delivery + retry policy
- [ ] Feature flags (enable/disable report types)
- [ ] Observability pages: request logs viewer, job metrics summary

---

## Data Model Changes

New entities (names illustrative):

| Entity | Service | Purpose |
|--------|---------|---------|
| `Supplier` | All | Supplier profile, org details |
| `ProductAttributeSet` | catalog | Dynamic attribute definitions per category |
| `ProductAttributeValue` | catalog | Attribute values per product |
| `CatalogChangeRequest` | catalog | Supplier-proposed changes |
| `ReportDefinition` | reporting | Report type, filters, schedule |
| `ReportJob` | reporting | Async job: status, progress, output path |
| `ReportAuditEvent` | reporting | Who accessed/downloaded what and when |
| `InventorySnapshot` | reporting | Periodic stock level snapshots |
| `SalesMetricSnapshot` | reporting | Periodic sales metric snapshots |

Key relationships:
- Supplier ↔ Products (one supplier has many products)
- ReportJob ↔ Supplier + ReportDefinition + Filters
- ReportAuditEvent ↔ ReportJob + User/Supplier

---

## API Endpoint Inventory (High Level)

### Catalog Service
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/catalog/products` | — | List/search products |
| POST | `/catalog/products` | ADMIN+ | Create product (existing chain link preserved) |
| POST | `/catalog/products/bulk-upload` | SUPPLIER+ | CSV bulk upload |
| POST | `/catalog/change-requests` | SUPPLIER+ | Propose catalog change |
| POST | `/catalog/workflow/{productId}/{action}` | ADMIN+ | Advance product lifecycle |
| GET | `/catalog/workflow/{productId}/history` | ANY | Lifecycle history |

### Reporting Service
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/v1/reports/definitions` | SUPPLIER+ | List available report types |
| POST | `/v1/reports/jobs` | SUPPLIER+ | Enqueue report generation |
| GET | `/v1/reports/jobs/{jobId}` | SUPPLIER+ | Poll job status |
| GET | `/v1/reports/{jobId}/download` | SUPPLIER+ | Download export |
| GET | `/v1/reports/audit` | ADMIN+ | View audit log |
| POST | `/v1/reports/schedules` | SUPPLIER+ | Create scheduled report |

### Supplier Portal API Service
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/portal/dashboard` | SUPPLIER+ | KPI summary |
| GET | `/portal/reports` | SUPPLIER+ | List supplier's reports |
| GET | `/portal/reports/{reportId}` | SUPPLIER+ | Report detail + drill-down |
| POST | `/portal/reports/request` | SUPPLIER+ | Request report generation |
| GET | `/portal/reports/{jobId}/download` | SUPPLIER+ | Download export |
| GET | `/portal/webhooks` | SUPPLIER+ | List registered webhooks |
| POST | `/portal/webhooks` | SUPPLIER+ | Register webhook callback |

### TypeScript/React Supplier Portal (Companion App)
| Route | Purpose |
|-------|---------|
| `/` | Login / auth |
| `/dashboard` | KPI dashboard |
| `/reports` | Reports list |
| `/reports/:id` | Report detail + drill-down |
| `/reports/:id/download` | Export download |
| `/webhooks` | Webhook registry |

---

## Security Benchmark Considerations

- Keep existing benchmark vulnerabilities intact — refer to [vuln-inventory.md](./vuln-inventory.md) before every code change.
- Each phase adds decoy safe patterns near vulnerable-looking code:
  - Parameterized SQL queries near injection-prone report filtering
  - Auth guards near authorization flaws in supplier portal API
  - Input validation near unsafe parsing in bulk upload
  - Proper CORS configuration near misconfigured blueprints
- New code includes realistic "looks vulnerable" areas without removing existing benchmark vulnerabilities.

---

## Testing Plan (High Level)

- **Unit tests**
  - DTO validation and filter parsing
  - Report definition validation
  - i18n dictionary consistency (all locales have same keys)
- **Integration tests**
  - Report job lifecycle (enqueue → status → download)
  - Aggregation correctness for sample datasets
  - Cross-service API contract validation
- **UI smoke tests**
  - Locale switching
  - Report list rendering
  - Drill-down pagination
- **Security benchmark checks** (run after every phase)
  - Existing vulnerabilities remain exploitable
  - New vulnerabilities are exploitable
  - Decoy safe patterns exist near vulnerable-looking code
  - `.vulns`, `README.md`, `scenarios.md` are up to date

---

## Deliverables Checklist

- [x] Vuln inventory documented
- [x] Expansion plan (this document)
- [ ] Phase 1: Architecture refactor + shared packages
- [ ] Phase 2: Core reporting features (MVP)
- [ ] Phase 3: Async reporting + exports + audit
- [ ] Phase 4: UI expansion + i18n
- [ ] Phase 5: Advanced features
- [ ] `.vulns`, `README.md`, `scenarios.md` updated after each phase
- [ ] All existing vulnerabilities preserved and verified
- [ ] Git commit after phase completion
