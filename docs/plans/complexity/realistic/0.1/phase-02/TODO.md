# Phase 02 TODO — Core Reporting Features (MVP)

## Catalog Service — Product Lifecycle
- [ ] Create `services/catalog-service/src/models/lifecycle.py` — lifecycle states enum, transition rules
- [ ] Create `services/catalog-service/src/services/lifecycle_service.py` — state machine logic
- [ ] Create `services/catalog-service/src/controllers/lifecycle_controller.py`
  - [ ] `advance_lifecycle(product_id, action)` — ADMIN+ only
  - [ ] `get_lifecycle_history(product_id)` — any authenticated user
- [ ] Add routes: `/catalog/workflow/{id}/{action}`, `/catalog/workflow/{id}/history`
- [ ] Add sample products in each lifecycle state for testing

## Catalog Service — Bulk Upload (chain-02 step 2)
- [ ] Create `services/catalog-service/src/services/bulk_upload_service.py` — CSV parsing
- [ ] Create `services/catalog-service/src/controllers/catalog_controller.py` → `bulk_upload`
  - [ ] Plant CHAIN LINK 2 (chain-02) annotation: trusts `supplierId` from request body without ownership check
- [ ] Create decoy endpoint `get_my_products` — correctly scoped to session supplier_id
- [ ] Add route: `POST /catalog/products/bulk-upload`
- [ ] Add route: `GET /catalog/my-products` (decoy)

## Catalog Service — Attribute Sets
- [ ] Add `ProductAttributeSet` model (category_id, attr_name, data_type, required)
- [ ] Add `ProductAttributeValue` model (product_id, attr_set_id, value)
- [ ] Add seed data: 3-5 attribute definitions per category

## Reporting Service — Data Models
- [ ] Create `services/reporting-service/src/models/report_job.py` — ReportJob model
- [ ] Create `services/reporting-service/src/models/inventory_snapshot.py`
- [ ] Create `services/reporting-service/src/models/sales_metric_snapshot.py`
- [ ] Add seed data: 20-30 inventory snapshots, 50+ sales metric snapshots

## Reporting Service — Aggregation Engine
- [ ] Create `services/reporting-service/src/services/aggregation_service.py`
  - [ ] `get_sales_report(filters)` — top products by revenue/volume/margin
  - [ ] `get_inventory_health(filters)` — stock levels, low-stock alerts
  - [ ] `get_data_quality_report(filters)` — completeness scores per product
  - [ ] Decoy: `build_sales_filters(filters)` — parameterized SQL near aggregation queries

## Reporting Service — Controllers & Routes
- [ ] Create `services/reporting-service/src/controllers/report_controller.py`
  - [ ] `list_definitions()` — available report types
  - [ ] `sales_report()`, `inventory_health()`, `data_quality()`
- [ ] Add routes: `/v1/reports/definitions`, `/v1/reports/sales`, etc.

## Supplier Portal API — Auth (A07)
- [ ] Create `services/supplier-portal-api/src/services/auth_service.py`
  - [ ] `login(supplier_id, password)` — **VULNERABILITY A07**: accepts any password
- [ ] Create decoy: `verify_token(session)` — proper HMAC session verification
- [ ] Create `services/supplier-portal-api/src/controllers/auth_controller.py`
  - [ ] `login()` — POST /portal/auth/login
  - [ ] `verify()` — GET /portal/auth/verify (decoy)
- [ ] Add supplier user seed data (5-10 supplier accounts)

## Supplier Portal API — Dashboard & Reports
- [ ] Create `services/supplier-portal-api/src/services/dashboard_service.py`
  - [ ] `get_kpi_summary(supplier_id)` — aggregates from reporting-service
- [ ] Create `services/supplier-portal-api/src/controllers/portal_controller.py`
  - [ ] `dashboard()` — GET /portal/dashboard
  - [ ] `list_reports()` — GET /portal/reports
- [ ] Add routes

## Artifact Updates
- [ ] Update `.vulns` — add VULN-05 (A07), complete chain-02 step 2, add decoys
- [ ] Update `README.md` — new endpoints, product lifecycle, reporting features
- [ ] Update `scenarios.md` — complete chain-02 narrative, attack scenario

## Verification
- [ ] Sales report returns correct top products by revenue with sample data
- [ ] Inventory health correctly identifies low-stock products
- [ ] Data quality report computes correct completeness scores
- [ ] A07: login with any supplier ID + any password succeeds
- [ ] A07: login with non-existent supplier ID fails (404)
- [ ] chain-02 step 2: bulk upload accepts arbitrary `supplierId` in CSV
- [ ] chain-02 step 2 + step 1: attacker can upload products under any supplier ID
- [ ] Decoy `verify_token` rejects expired/manipulated sessions
- [ ] Decoy `get_my_products` only returns products for session supplier_id
- [ ] Existing vulnerabilities from all previous phases remain exploitable