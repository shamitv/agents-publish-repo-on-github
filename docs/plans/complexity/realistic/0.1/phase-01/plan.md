# Phase 01: Architecture Refactor + Shared Packages

## Goal

Restructure app-01 from a flat `src/` monolith into a multi-service monorepo with shared domain packages, while preserving all existing vulnerabilities in their original locations.

## Scope

### Included
- [x] Monorepo directory structure under `apps/python/app-01-ecommerce-catalog/services/` and `packages/`
- [x] `packages/domain/` — shared DTOs, enums, validation rules (`ProductSchema`, `CategorySchema`, `OrderSchema`, `SupplierSchema`, `ReportRequestSchema`, `ReportJobStatus`)
- [x] `packages/utils/` — pagination helper, response format helper
- [x] Move existing `src/` code into `services/catalog-service/src/` verbatim (preserving all vulnerability comments)
- [x] `services/catalog-service/` has its own `app.py`, `requirements.txt`, `__init__.py`
- [x] `services/reporting-service/` scaffold with Flask app, health endpoint (`GET /health`)
- [x] `services/supplier-portal-api/` scaffold with Flask app, health endpoint (`GET /health`)
- [x] Scaffold `apps/typescript/app-01-supplier-portal/` (Vite + React + TypeScript, no pages yet)
- [x] All 3 Python services run independently (each on a separate port for dev)
- [x] Verify catalog-service passes existing startup + smoke tests

### Excluded
- No new business features — this phase is pure structural refactoring
- No i18n, no React pages, no async jobs
- No database changes beyond what catalog-service already uses

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Monorepo first, services second | Building services on top of shared packages avoids costly migration later |
| `packages/domain` uses plain Python dataclasses + `__init__.py` re-exports | No pip-install needed for local packages; services import via `sys.path` or relative imports |
| Catalog-service code is moved verbatim, not rewritten | Preserves vulnerability locations exactly as-is for benchmarking |
| Each service has its own `requirements.txt` | Allows independent dependency pinning (useful for A06 vulnerability in Phase 5) |
| Services run on distinct ports (5001, 5002, 5003) during dev | Avoids port conflicts; production reverse proxy is out of scope |
| TypeScript app uses Vite (not CRA) | Faster dev builds, modern; CRA is deprecated |

## Before / After Directory Structure

### Before
```
apps/python/app-01-ecommerce-catalog/
  src/
    controllers/     (user, product, category, order, search, billing)
    services/
    repositories/
    routes/
    config/
    consumers/
  static/
    js/
    css/
  templates/
  app.py
  .vulns
  README.md
  scenarios.md
```

### After
```
apps/python/app-01-ecommerce-catalog/
  services/
    catalog-service/
      src/
        controllers/   (moved verbatim)
        services/
        repositories/
        routes/
        config/
        consumers/
      static/
      templates/
      app.py
      requirements.txt
    reporting-service/
      src/
        controllers/
        services/
        repositories/
        routes/
        config/
      app.py
      requirements.txt
    supplier-portal-api/
      src/
        controllers/
        services/
        routes/
        config/
      app.py
      requirements.txt
  packages/
    domain/
      __init__.py       (re-exports all schemas)
      schemas/
        product.py
        category.py
        order.py
        supplier.py
        report.py
      enums.py
      validators.py
    utils/
      __init__.py
      pagination.py
      response.py
  .vulns
  README.md
  scenarios.md

apps/typescript/app-01-supplier-portal/
  src/
    main.tsx
    App.tsx
  public/
  package.json
  vite.config.ts
  tsconfig.json
  tsconfig.node.json
  index.html
```

## Vulnerability Planting

| # | Type | OWASP | CWE | Location | Description | Severity |
|---|------|-------|-----|----------|-------------|----------|
| 1 | Standalone | A04 | CWE-602 | `packages/domain/validators.py` → `validate_supplier_id` | Weak validation permits negative/zero IDs and alphabetic strings; no server-side enforcement of ID format | Medium |

**Source comment**: `# VULNERABILITY A04: validate_supplier_id accepts zero, negative, and non-numeric IDs without error`

### New Chain Scenario: chain-02

**Chain: Weak Supplier ID Validation → Catalog Poisoning via Bulk Upload → Auth Bypass on Change Approval**

| Step | OWASP | CWE | Location | Description | Severity (standalone) |
|------|-------|-----|----------|-------------|-----------------------|
| 1 | A04 | CWE-602 | `packages/domain/validators.py` → `validate_supplier_id` | Accepts zero/negative/non-numeric supplierId values | Low |
| 2 | A01 | CWE-639 | `services/catalog-service/src/controllers/catalog_controller.py` → `bulk_upload` | Bulk CSV upload trusts supplierId from request body without verifying supplier owns that ID | Medium |

**Chain ID**: `chain-02`
**Planted in**: Phase 1 (step 1) + Phase 2 (step 2)
**Combined Impact**: `data_modification` — attacker uses weak validation to submit bulk catalog changes under a forged supplier identity
**Note**: Only Step 1 is planted in Phase 1. Step 2 is planted in Phase 2. Step 3 (auth bypass) is planted in Phase 2.

## Decoy Patterns

| # | Location | Why it looks vulnerable | Why it is safe |
|---|----------|------------------------|----------------|
| 1 | `packages/domain/validators.py` → `validate_date_range` | Accepts user-supplied date strings; co-located with the vulnerable `validate_supplier_id` | Parses dates strictly via `datetime.fromisoformat()`, validates start < end, rejects malformed inputs |
| 2 | `packages/utils/pagination.py` → `parse_pagination` | Parses `?page=` and `?limit=` query params from raw request args | Clamps page ≥ 1, limit ∈ [1, 100], coerces to int safely |

## Data Model Changes

- New `SupplierSchema` in `packages/domain/schemas/supplier.py`:
  - `id: int`, `name: str`, `org_code: str`, `status: str` (active/suspended), `contact_email: str`
  - Used by all 3 services
- New `ReportRequestSchema` in `packages/domain/schemas/report.py`:
  - `supplier_id: int`, `report_type: str`, `filters: dict`, `date_range: dict`

## Artifact Updates

- `.vulns`: Add VULN-04 (A04) and chain-02 (step 1 only)
- `README.md`: Update architecture section, add monorepo description, update API endpoints table
- `scenarios.md`: Add chain-02 narrative (step 1 description only; rest added in Phase 2)

## Dependencies on Other Phases

- **Phase 2** depends on this phase (monorepo must exist before adding features)
- **Phase 4** depends on this phase (TypeScript scaffold created here)
- No dependencies on Phase 3, 5

## Testing Focus

- [ ] `catalog-service` starts and responds to existing endpoints
- [ ] `reporting-service` health endpoint returns 200
- [ ] `supplier-portal-api` health endpoint returns 200
- [ ] `packages/domain` schemas import correctly in all 3 services
- [ ] Existing vulnerabilities remain exploitable (run IDOR check, SQLi check, session-forgery chain)
- [ ] No regression in product CRUD or search