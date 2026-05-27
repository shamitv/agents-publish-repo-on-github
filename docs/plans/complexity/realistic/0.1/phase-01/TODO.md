# Phase 01 TODO — Architecture Refactor + Shared Packages

## Pre-requisites
- [ ] Read vuln-inventory.md — confirm all no-touch files
- [ ] Read expansion-plan.md — confirm phase scope

## Monorepo Structure
- [ ] Create `apps/python/app-01-ecommerce-catalog/services/` directory
- [ ] Create `apps/python/app-01-ecommerce-catalog/packages/` directory
- [ ] Move `src/`, `static/`, `templates/`, `app.py` into `services/catalog-service/` verbatim
- [ ] Update imports in catalog-service to reference `packages/domain` via sys.path
- [ ] Verify `catalog-service/app.py` starts and responds to all existing endpoints

## Shared Packages
- [ ] Create `packages/domain/__init__.py`
- [ ] Create `packages/domain/schemas/product.py`
- [ ] Create `packages/domain/schemas/category.py`
- [ ] Create `packages/domain/schemas/order.py`
- [ ] Create `packages/domain/schemas/supplier.py`
- [ ] Create `packages/domain/schemas/report.py`
- [ ] Create `packages/domain/enums.py`
- [ ] Create `packages/domain/validators.py` (including vulnerable `validate_supplier_id` + safe `validate_date_range` decoy)
- [ ] Create `packages/utils/__init__.py`
- [ ] Create `packages/utils/pagination.py` (decoy: safe parameter parsing near vulnerable validator)
- [ ] Create `packages/utils/response.py`

## Reporting Service Scaffold
- [ ] Create `services/reporting-service/src/` structure
- [ ] Create `services/reporting-service/app.py` with health endpoint
- [ ] Create `services/reporting-service/requirements.txt`
- [ ] Verify health endpoint returns 200 at `http://localhost:5002/health`

## Supplier Portal API Scaffold
- [ ] Create `services/supplier-portal-api/src/` structure
- [ ] Create `services/supplier-portal-api/app.py` with health endpoint
- [ ] Create `services/supplier-portal-api/requirements.txt`
- [ ] Verify health endpoint returns 200 at `http://localhost:5003/health`

## TypeScript/React Scaffold
- [ ] Create `apps/typescript/app-01-supplier-portal/` directory
- [ ] Create `package.json` (react, react-dom, vite, TypeScript dev deps)
- [ ] Create `vite.config.ts`
- [ ] Create `tsconfig.json` and `tsconfig.node.json`
- [ ] Create `index.html`
- [ ] Create `src/main.tsx` (ReactDOM.createRoot)
- [ ] Create `src/App.tsx` (bare "Supplier Portal" placeholder)
- [ ] Run `npm install` in throwaway directory mode — `node_modules` must be gitignored
- [ ] Verify `npm run dev` starts without errors

## Vulnerability & Artifact Updates
- [ ] Plant A04 vulnerability in `packages/domain/validators.py` (`validate_supplier_id`)
- [ ] Add decoy `validate_date_range` in same file
- [ ] Add decoy `parse_pagination` in `packages/utils/pagination.py`
- [ ] Add chain-02 step 1 annotation comment
- [ ] Update `.vulns` — add VULN-04 standalone, add chain-02 components definition
- [ ] Update `README.md` — architecture section, monorepo description, endpoints table
- [ ] Update `scenarios.md` — add chain-02 narrative (step 1 only at this phase)

## Verification
- [ ] All 3 Python services start independently
- [ ] `catalog-service` existing endpoints respond correctly (CRUD products, search, orders, user exists)
- [ ] Existing vulnerabilities remain exploitable:
  - [ ] A01 IDOR on orders
  - [ ] A03 SQL/ES injection in product search
  - [ ] A09 missing audit logging in billing consumer
  - [ ] chain-01 all 3 steps functional
- [ ] New A04 vulnerability is exploitable (submit zero/negative/alpha supplierId via API)
- [ ] Decoy `validate_date_range` correctly rejects bad dates
- [ ] Decoy `parse_pagination` correctly clamps invalid values
- [ ] `node_modules` is gitignored (verify via `git status`)