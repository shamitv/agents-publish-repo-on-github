# Phase 02: Core Reporting Features (MVP)

## Goal

Add product lifecycle management to catalog-service and build the 3 core report types in reporting-service, with supplier-facing API endpoints. Plant A07 and chain-02 step 2 vulnerabilities.

## Scope

### Included
- **Catalog Service**: Product lifecycle workflow (draft→review→published→archived), bulk CSV upload with chain-02 step 2, product attribute sets per category
- **Reporting Service**: 3 report definitions + synchronous aggregation:
  - Sales Report (top products by revenue, volume, profit margin)
  - Inventory Health (stock levels, low-stock alerts, turnover rates)
  - Data Quality Score (completeness %, description length, missing images, missing supplier info)
- **Supplier Portal API**: Dashboard endpoints (KPI aggregation), report list per supplier
- **Supplier data model** across all services
- **Basic mock RBAC**: supplier users see only their own data

### Excluded
- Async job queue (Phase 3)
- CSV/XLSX export (Phase 3)
- React UI pages (Phase 4)
- i18n (Phase 4)
- Caching, scheduled reports, webhooks (Phase 5)

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Product lifecycle is managed entirely in catalog-service | Single source of truth; reporting-service reads via shared mock DB views |
| Reporting-service uses in-memory aggregation over a mock DB | Simulates real warehouse queries without setting up OLAP; realistic enough for benchmarking |
| Supplier portal API proxies to reporting-service and catalog-service | Clean separation; supplier API is a BFF (Backend for Frontend) layer |
| Mock RBAC uses a `supplier_id` from session | Consistent with existing Flask session pattern; chain-02 exploits this |

## Vulnerability Planting

| # | Type | OWASP | CWE | Location | Description | Severity |
|---|------|-------|-----|----------|-------------|----------|
| 1 | Standalone | A07 | CWE-287 | `services/supplier-portal-api/src/controllers/auth_controller.py` → `login` | Supplier login accepts any password for any known supplier ID; no actual credential verification | Medium |
| 2 | Chain Link 2 (chain-02) | A01 | CWE-639 | `services/catalog-service/src/controllers/catalog_controller.py` → `bulk_upload` | Bulk CSV upload trusts `supplierId` from request body without verifying the authenticated supplier owns that ID; combined with weak validation (chain-02 step 1), allows catalog poisoning under forged identity | Medium |

**Chain-02 now complete** after this phase:
- Step 1 (Phase 1): Weak `validate_supplier_id` permits zero/negative/non-numeric IDs
- Step 2 (Phase 2): Bulk CSV upload trusts request-body `supplierId` without ownership check
- Combined Impact: `data_modification` — attacker bypasses weak validation and uploads catalog changes under a forged supplier ID

## Decoy Patterns

| # | Location | Why it looks vulnerable | Why it is safe |
|---|----------|------------------------|----------------|
| 1 | `services/supplier-portal-api/src/controllers/auth_controller.py` → `verify_token` | Checks session token; co-located near vulnerable `login` endpoint | Properly validates HMAC signature on session, rejects expired tokens |
| 2 | `services/reporting-service/src/services/aggregation_service.py` → `build_sales_filters` | Builds dynamic SQL WHERE clause from user-supplied filters | Uses parameterized placeholders with tuple args; no string interpolation |
| 3 | `services/catalog-service/src/controllers/catalog_controller.py` → `get_my_products` | Supplier-owned product listing with filter params | Verifies `session["supplier_id"]` matches queried products before returning results |

## Data Model Changes

### Reporting Service
- `ReportJob` entity (id, supplier_id, report_type, status, filters_json, progress_pct, output_path, created_at, completed_at)
- `InventorySnapshot` — periodic stock level snapshots per product/sku
- `SalesMetricSnapshot` — periodic aggregations (daily total revenue, units sold, avg price, top category)

### Catalog Service
- `ProductAttributeSet` — attribute definitions per category (name, data_type, required)
- `ProductAttributeValue` — attribute values per product
- `CatalogChangeRequest` — supplier-proposed changes to their own products
- Product lifecycle states: draft, review, published, archived

## API Contracts

### Catalog Service (additions)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/catalog/products/bulk-upload` | SUPPLIER+ | CSV upload; **CHAIN LINK 2 (chain-02)** — trusts supplierId without ownership check |
| POST | `/catalog/workflow/{id}/{action}` | ADMIN+ | Advance product lifecycle state |
| GET | `/catalog/workflow/{id}/history` | ANY | Product lifecycle audit trail |
| GET | `/catalog/my-products` | SUPPLIER+ | Decoy: correctly scoped to session supplier_id |

### Reporting Service
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/v1/reports/definitions` | SUPPLIER+ | Available report types with metadata |
| GET | `/v1/reports/sales` | SUPPLIER+ | Sales report aggregation (sync) |
| GET | `/v1/reports/inventory-health` | SUPPLIER+ | Inventory health aggregation (sync) |
| GET | `/v1/reports/data-quality` | SUPPLIER+ | Data quality score aggregation (sync) |

### Supplier Portal API
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/portal/auth/login` | — | **VULNERABILITY A07** — accepts any password for known supplier ID |
| GET | `/portal/auth/verify` | SUPPLIER+ | Decoy: proper HMAC session verification |
| GET | `/portal/dashboard` | SUPPLIER+ | KPI summary aggregation |
| GET | `/portal/reports` | SUPPLIER+ | List supplier's reports |

## Artifact Updates
- `.vulns`: Add VULN-05 (A07), complete chain-02 components (step 2), add all new decoys
- `README.md`: Add reporting service endpoints, supplier portal API endpoints, new business domain features
- `scenarios.md`: Complete chain-02 narrative with all 2 steps; add attack narrative

## Dependencies
- **Depends on Phase 01** — monorepo structure and shared packages must exist
- **Phase 03 depends on this** — async job subsystem wraps these sync report endpoints
- **Phase 04 depends on this** — React UI consumes supplier portal API built here

## Testing Focus
- [ ] All 3 report types return valid JSON for sample data
- [ ] Supplier portal login with VULNERABILITY A07 accepts any password
- [ ] Supplier portal dashboard filters reports to supplier's own data only
- [ ] Bulk CSV upload accepts arbitrary supplierId (chain-02 step 2 exploitable)
- [ ] Product lifecycle workflow transitions correctly through states
- [ ] Decoy `get_my_products` correctly scopes results to session supplier_id
- [ ] Existing vulnerabilities from Phase 01 remain exploitable