# Phase 02 TODO — Core Reporting Features (MVP)

## Catalog Service — Product Lifecycle (completed before Phase 2 execution)
- [x] Create `services/catalog-service/src/models/lifecycle.py` — lifecycle states enum, transition rules
- [x] Create `services/catalog-service/src/services/lifecycle_service.py` — state machine logic
- [x] Create `services/catalog-service/src/controllers/lifecycle_controller.py`
  - [x] `advance_lifecycle(product_id, action)` — ADMIN+ only
  - [x] `get_lifecycle_history(product_id)` — any authenticated user
- [x] Add routes: `/api/products/{product_id}/lifecycle/{action}`, `/api/products/{product_id}/lifecycle` (note: paths differ from plan spec but functionality matches)

## Catalog Service — Bulk Upload (chain-02 step 2)
- [x] Plant CHAIN LINK 2 (chain-02) annotation in `bulk_upload_controller.py`: trusts `supplierId` from CSV without ownership check
- [x] Add `supplier_id` column to products table schema and seed data
- [x] Create decoy endpoint `get_my_products` in `product_controller.py` — correctly scoped to session supplier_id
- [x] Add route: `POST /api/products/bulk-upload`
- [x] Add route: `GET /api/products/my-products` (decoy)

## Catalog Service — Attribute Sets
- [x] Add `ProductAttributeSet` model (category, attr_name, data_type, required)
- [x] Add `ProductAttributeValue` model (product_id, attr_id, value)
- [x] Add seed data: 3-5 attribute definitions per category

## Reporting Service — Data Models
- [x] Create `services/reporting-service/src/models/report_job.py` — ReportJob model (completed before Phase 2)
- [x] Create `services/reporting-service/src/models/inventory_snapshot.py` — 25 seed records
- [x] Create `services/reporting-service/src/models/sales_metric_snapshot.py` — 55 seed records
- [x] Add seed data: 25 inventory snapshots, 55+ sales metric snapshots

## Reporting Service — Aggregation Engine
- [x] Create `services/reporting-service/src/services/aggregation_service.py`
  - [x] `get_sales_report(filters)` — top products by revenue/volume/margin
  - [x] `get_inventory_health(filters)` — stock levels, low-stock alerts
  - [x] `get_data_quality_report(filters)` — completeness scores per product
  - [x] Decoy: `build_sales_filters(filters)` — parameterized SQL near aggregation queries

## Reporting Service — Controllers & Routes
- [x] Create `services/reporting-service/src/controllers/report_controller.py`
  - [x] `list_definitions()` — available report types
  - [x] `sales_report()`, `inventory_health()`, `data_quality()`
- [x] Add routes: `/v1/reports/definitions`, `/v1/reports/sales`, `/v1/reports/inventory-health`, `/v1/reports/data-quality`

## Supplier Portal API — Auth (A07)
- [x] Create `services/supplier-portal-api/src/services/auth_service.py`
  - [x] `login(supplier_id, password)` — **VULNERABILITY A07**: accepts any password
- [x] Create decoy: `verify_token(session)` — proper HMAC session verification
- [x] Create `services/supplier-portal-api/src/controllers/auth_controller.py`
  - [x] `login()` — POST /portal/auth/login
  - [x] `verify()` — GET /portal/auth/verify (decoy)
- [x] Add supplier user seed data (7 supplier accounts)

## Supplier Portal API — Dashboard & Reports
- [x] Create `services/supplier-portal-api/src/services/dashboard_service.py`
  - [x] `get_kpi_summary(supplier_id)` — aggregates from report generation service
- [x] Create `services/supplier-portal-api/src/controllers/portal_controller.py`
  - [x] `dashboard()` — GET /portal/dashboard
  - [x] `list_reports()` — GET /portal/reports
- [x] Add routes

## Artifact Updates
- [x] Update `.vulns` — add VULN-05 (A07), complete chain-02 step 2, add decoys
- [x] Update `README.md` — new endpoints, product lifecycle, reporting features
- [x] Update `scenarios.md` — complete chain-02 narrative, attack scenario

## Verification
- [x] Sales report returns correct top products by revenue with sample data
- [x] Inventory health correctly identifies low-stock products
- [x] Data quality report computes correct completeness scores
- [x] A07: login with any supplier ID + any password succeeds
- [x] A07: login with non-existent supplier ID fails (404)
- [x] chain-02 step 2: bulk upload accepts arbitrary `supplierId` in CSV
- [x] chain-02 step 2 + step 1: attacker can upload products under any supplier ID
- [x] Decoy `verify_token` returns success for any token
- [x] Decoy `get_my_products` only returns products for session supplier_id
- [x] Existing vulnerabilities from all previous phases remain exploitable
