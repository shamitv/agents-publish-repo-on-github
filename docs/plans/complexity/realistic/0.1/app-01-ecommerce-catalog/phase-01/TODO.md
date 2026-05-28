# Phase 01 TODO — Architecture Refactor + Shared Packages

## Pre-requisites
- [x] Read vuln-inventory.md — confirm all no-touch files
- [x] Read expansion-plan.md — confirm phase scope

## Monorepo Structure
- [x] Create `apps/python/app-01-ecommerce-catalog/services/` directory
- [x] Create `apps/python/app-01-ecommerce-catalog/packages/` directory
- [x] Move `src/`, `static/`, `templates/`, `app.py` into `services/catalog-service/` verbatim
- [x] Update imports in catalog-service to reference `packages/domain` via sys.path
- [x] Verify `catalog-service/app.py` starts and responds to all existing endpoints

## Shared Packages
- [x] Create `packages/domain/__init__.py`
- [x] Create `packages/domain/schemas/product.py`
- [x] Create `packages/domain/schemas/category.py`
- [x] Create `packages/domain/schemas/order.py`
- [x] Create `packages/domain/schemas/supplier.py`
- [x] Create `packages/domain/schemas/report.py`
- [x] Create `packages/domain/enums.py`
- [x] Create `packages/domain/validators.py` (including vulnerable `validate_supplier_id` + safe `validate_date_range` decoy)
- [x] Create `packages/utils/__init__.py`
- [x] Create `packages/utils/pagination.py` (decoy: safe parameter parsing near vulnerable validator)
- [x] Create `packages/utils/response.py`

## Reporting Service Scaffold
- [x] Create `services/reporting-service/src/` structure
- [x] Create `services/reporting-service/app.py` with health endpoint
- [x] Create `services/reporting-service/requirements.txt`
- [x] Verify health endpoint returns 200 at `http://localhost:5002/health`

## Supplier Portal API Scaffold
- [x] Create `services/supplier-portal-api/src/` structure
- [x] Create `services/supplier-portal-api/app.py` with health endpoint
- [x] Create `services/supplier-portal-api/requirements.txt`
- [x] Verify health endpoint returns 200 at `http://localhost:5003/health`

## TypeScript/React Scaffold (completed before Phase 1 execution by prior work)
- [x] Create `apps/typescript/app-01-supplier-portal/` directory
- [x] Create `package.json` (react, react-dom, vite, TypeScript dev deps)
- [x] Create `vite.config.ts`
- [x] Create `tsconfig.json` and `tsconfig.node.json` (tsconfig.node.json not present — non-blocking)
- [x] Create `index.html`
- [x] Create `src/main.tsx` (ReactDOM.createRoot)
- [x] Create `src/App.tsx` (bare "Supplier Portal" placeholder)
- [x] Run `npm install` in throwaway directory mode — `node_modules` must be gitignored
- [x] Verify `npm run dev` starts without errors

## Vulnerability & Artifact Updates
- [x] Plant A04 vulnerability in `packages/domain/validators.py` (`validate_supplier_id`)
- [x] Add decoy `validate_date_range` in same file
- [x] Add decoy `parse_pagination` in `packages/utils/pagination.py`
- [x] Add chain-02 step 1 annotation comment
- [x] Update `.vulns` — add VULN-04 standalone, add chain-02 components definition
- [x] Update `README.md` — architecture section, monorepo description, endpoints table
- [x] Update `scenarios.md` — add chain-02 narrative (step 1 only at this phase)

## Verification
- [x] All 3 Python services start independently
- [x] `catalog-service` existing endpoints respond correctly (CRUD products, search, orders, user exists)
- [x] Existing vulnerabilities remain exploitable:
  - [x] A01 IDOR on orders
  - [x] A03 SQL/ES injection in product search
  - [x] A09 missing audit logging in billing consumer
  - [x] chain-01 all 3 steps functional
- [x] New A04 vulnerability is exploitable (submit zero/negative/alpha supplierId via API)
- [x] Decoy `validate_date_range` correctly rejects bad dates
- [x] Decoy `parse_pagination` correctly clamps invalid values
- [x] `node_modules` is gitignored (verify via `git status`)
