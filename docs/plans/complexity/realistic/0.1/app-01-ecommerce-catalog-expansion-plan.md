# App 01 (ecommerce-catalog) — Realistic Complexity Expansion Plan (v0.1)

## Overview
This plan describes how to dramatically increase the size and realism of **App 01 (ecommerce-catalog)** by adding supplier product reporting, a dedicated reporting microservice, multi-language UIs, internationalization (i18n), and a monorepo/service architecture refactor.

> **Non-goals / Constraints**
- Do **not** remove or “fix” any intentionally planted vulnerabilities already present in the benchmark.
- Add new code with realistic patterns, including **decoy safe code** near vulnerable-looking code to preserve benchmarking value.
- Avoid introducing real external network dependencies in test code.

---

## Target Outcomes
1. **Codebase size increase** via new services, modules, UI pages, and shared packages.
2. **More realistic business workflows**: supplier catalog management + reporting + exports + auditability.
3. **Architecture realism**: monorepo + service boundaries + shared domain packages.
4. **UI realism**: multiple frontends (different languages) + i18n dictionaries + locale switching.

---

## High-Level Architecture Changes

### 1) Convert to a monorepo-style structure
Restructure under a monorepo root for App 01:

- `apps/app-01-ecommerce-catalog/`
  - `services/`
    - `catalog-service/`
    - `reporting-service/`
    - `supplier-portal-service/`
  - `packages/`
    - `domain/` (shared DTOs, schemas, validation rules)
    - `ui/` (shared UI components, if applicable)
    - `i18n/` (locale dictionaries + locale utilities)
  - `README.md` (service overview + local run instructions)

### 2) Separate service responsibilities
- **Catalog Service**
  - Product/SKU/category management
  - Supplier product data ingestion
  - Catalog workflow (draft/review/publish/archive)
  - Bulk upload + validation
- **Reporting Service**
  - Report definitions
  - Report generation (sync + async)
  - Aggregation pipelines (metrics by SKU/category/date)
  - Exports (CSV/XLSX)
  - Caching and audit logs
- **Supplier Portal Service**
  - Supplier dashboards and report pages
  - Report request UI
  - Drill-down views and exports UI

### 3) Shared domain package
Create `packages/domain` to centralize:
- Product attribute schemas
- Report request/response DTOs
- Validation rules (date ranges, supplierId format, filter constraints)
- Common enums (report types, metric types, status codes)

### 4) Async job subsystem for reporting
Reporting service supports:
- Enqueue report jobs
- Poll job status
- Download exports when ready
- Emit webhook-like events (simulated) when jobs complete

### 5) i18n strategy
- `packages/i18n` provides:
  - locale dictionaries (e.g., `en`, `es`, `fr` or `en`, `hi`, `de`)
  - locale selection utilities
- UI consumes dictionaries for labels, headings, and table column names.
- Backend returns either:
  - localized strings, or
  - message keys that the UI maps via dictionaries.

### 6) Multi-language UI builds
Add at least two UI implementations:
- **UI A**: TypeScript-based frontend (e.g., React/Vite)
- **UI B**: JavaScript-based frontend (e.g., vanilla JS or another lightweight framework)

Both UIs consume the same service APIs.

---

## Functionality Additions (Detailed)

## A) Supplier Product Reporting & Analytics (12+ features)
1. **Supplier Dashboard (KPIs)**
   - Views, add-to-cart, conversion, returns
2. **Sales Report**
   - Filters: date range, SKU/category, channel
   - Export: CSV/XLSX
3. **Inventory Health Report**
   - Stockouts, low-stock, reorder recommendations
4. **Pricing Competitiveness Report**
   - Compare supplier pricing vs marketplace averages
5. **Category Compliance Report**
   - Missing attributes, taxonomy mismatches
6. **Defect/Return Reasons Report**
   - Reason codes + trend analysis
7. **SLA Report**
   - Fulfillment time, late shipment rate
8. **Promotion Impact Report**
   - Before/after metrics for promotions
9. **Data Quality Score**
   - Completeness + consistency scoring
10. **Drill-down Views**
   - Chart → underlying rows with pagination
11. **Report Audit Log**
   - Track report access and downloads
12. **Supplier-specific Report Visibility**
   - RBAC rules for who can view which reports

---

## B) Reporting Microservice Capabilities (8+ features)
1. **Versioned reporting API**
   - Example: `/v1/reports/...`
2. **Aggregation pipelines**
   - Server-side grouping by SKU/category/date
3. **Caching layer**
   - Cache repeated queries by supplierId + filters
4. **Async report generation**
   - `POST /reports/jobs` enqueue
   - `GET /reports/jobs/{id}` status
   - `GET /reports/{jobId}/download` export
5. **Scheduled reports**
   - Daily/weekly/monthly report definitions
6. **Audit logging**
   - Store report access events
7. **Export formatting**
   - CSV + XLSX generation
8. **Drill-down pagination**
   - Row-level filtering and paging

---

## C) Catalog Expansion to Feed Reporting (8+ features)
1. **Supplier-managed product attributes**
   - Dynamic attribute sets per category
2. **Product lifecycle workflow**
   - Draft → Review → Published → Archived
3. **Catalog change requests**
   - Supplier proposes changes; admin approves
4. **Bulk upload & validation**
   - CSV import with row-level error reporting
5. **Product media management**
   - Image/video metadata + ordering
6. **Product bundles/kits**
   - Bundle pricing rules and component mapping
7. **Simple recommendation engine**
   - Cross-sell rules based on category/brand
8. **Customer reviews & ratings**
   - Adds reporting signals (e.g., return correlation)

---

## D) UI Expansion + Multi-language + i18n (8+ features)
1. **Supplier portal pages**
   - Dashboard
   - Reports list
   - Report detail + drill-down
   - Export/download
2. **Admin console pages**
   - Approvals
   - Supplier management
   - Audit log viewer
3. **i18n**
   - Locale switcher
   - Translated UI labels and table headers
4. **Two UI builds**
   - TS UI build
   - JS UI build
5. **Accessibility improvements**
   - ARIA labels, keyboard navigation, focus management

---

## E) Platform/Operational Realism (6+ features)
1. **Feature flags**
   - Enable/disable modules and report types
2. **Background job framework abstraction**
   - Job queue interface + worker simulation
3. **Observability pages**
   - Request logs viewer
   - Job metrics summary
4. **Notifications**
   - In-app notifications (simulated email-like UI)
5. **Webhook registry**
   - Register “report ready” callbacks (simulated)
6. **Retry policy simulation**
   - For webhook delivery attempts

---

## Data Model / Domain Changes (High Level)
Add entities (names illustrative):
- `Supplier`, `SupplierOrg`
- `ProductAttributeSet`, `ProductAttributeValue`
- `CatalogChangeRequest`
- `ReportJob`, `ReportDefinition`, `ReportAuditEvent`
- `InventorySnapshot`, `SalesMetricSnapshot`

Key relationships:
- Supplier ↔ products
- ReportJob ↔ supplier + report definition + filters
- AuditEvent ↔ report job + user

---

## API Endpoint Inventory (High Level)
### Catalog Service
- `GET /catalog/products`
- `POST /catalog/products` (supplier ingestion)
- `POST /catalog/products/bulk-upload`
- `POST /catalog/change-requests`
- `POST /catalog/workflow/{productId}/{action}`

### Reporting Service
- `GET /v1/reports/definitions`
- `POST /v1/reports/jobs`
- `GET /v1/reports/jobs/{jobId}`
- `GET /v1/reports/{jobId}/download`
- `GET /v1/reports/audit`
- `POST /v1/reports/schedules`

### Supplier Portal Service
- `GET /portal/dashboard`
- `GET /portal/reports`
- `GET /portal/reports/{reportId}`
- `POST /portal/reports/request`
- `GET /portal/reports/{jobId}/download`

---

## Security Benchmark Considerations (Important)
When implementing new endpoints/modules:
- Keep existing benchmark vulnerabilities intact.
- Add **decoy safe patterns** near vulnerable-looking code:
  - parameterized queries near injection-prone code
  - auth guards near authorization flaws
  - input validation near unsafe parsing
- Ensure new code includes realistic “looks vulnerable” areas without removing the benchmark’s planted vulnerabilities.

---

## Implementation Phases (No Code)

### Phase 1 — MVP (Catalog workflow + basic reporting)
- Catalog workflow: draft/review/publish
- Report definitions (basic)
- Synchronous report endpoints
- Supplier portal: dashboard + report list

### Phase 2 — Async reporting + exports + audit logs
- Report job queue + status polling
- CSV/XLSX exports
- Audit log storage + UI viewer

### Phase 3 — Drill-down + caching + scheduled reports + webhooks
- Drill-down endpoints with pagination
- Caching for repeated aggregations
- Scheduled report definitions
- Webhook registry + simulated delivery

### Phase 4 — UI expansion + i18n + multi-language builds
- Add admin console UI
- Add locale dictionaries + locale switcher
- Implement TS UI and JS UI builds

### Phase 5 — Monorepo/service refactor + shared packages
- Move code into monorepo structure
- Introduce `packages/domain` and `packages/i18n`
- Add feature flags and observability pages

---

## Testing Plan (High Level)
- **Unit tests**
  - DTO validation and filter parsing
  - report definition validation
- **Integration tests**
  - report job lifecycle (enqueue → status → download)
  - aggregation correctness for sample datasets
- **UI smoke tests**
  - locale switching
  - report list rendering
  - drill-down pagination
- **Security benchmark checks**
  - ensure planted vulnerabilities remain
  - ensure decoy safe patterns exist near vulnerable-looking code

---

## Deliverables Checklist
- [ ] Monorepo/service architecture plan applied (structure + boundaries)
- [ ] Catalog workflow implemented
- [ ] Reporting service implemented (sync + async)
- [ ] Exports + audit logs implemented
- [ ] Supplier portal UI implemented (dashboard + reports)
- [ ] Admin console UI implemented
- [ ] i18n dictionaries + locale switcher implemented
- [ ] Multi-language UI builds implemented
- [ ] Feature flags + observability pages implemented
- [ ] Scheduled reports + webhook simulation implemented