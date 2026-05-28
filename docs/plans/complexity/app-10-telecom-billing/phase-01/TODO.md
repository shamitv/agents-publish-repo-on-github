# Phase 01 TODO — Inventory & Gap Analysis

## Pre-requisites
- [ ] Read AGENTS.md — confirm annotation and metadata rules
- [ ] Read generic-upgrade-guide.md — confirm artifact templates

## Directory Scaffold
- [ ] Create `docs/plans/complexity/app-10-telecom-billing/`
- [ ] Create `docs/plans/complexity/app-10-telecom-billing/phase-01/`
- [ ] Create `docs/plans/complexity/app-10-telecom-billing/phase-02/`
- [ ] Create `docs/plans/complexity/app-10-telecom-billing/phase-03/`
- [ ] Create `docs/plans/complexity/app-10-telecom-billing/phase-04/`
- [ ] Create `docs/plans/complexity/app-10-telecom-billing/phase-05/`

## Annotation Audit
- [ ] Grep all `.java` files for `VULNERABILITY` — confirm 7 matches across 3 files:
  - [ ] UsageController.java (1 match — A03 SQLi)
  - [ ] AdminController.java (5 matches — A01, A04×2, A09×2)
  - [ ] PaymentService.java (1 match — A04 design flaw)
- [ ] Grep all `.java` files for `CHAIN LINK` — confirm 3 matches:
  - [ ] AdminController.java — CHAIN LINK 1, 2, 3 (all chain-01)
- [ ] Verify no annotations exist in: BillingController, BillingService, HealthService, CustomerController, AuthController, PlanPricingService, UsageService, InvoiceSearchClient, PlanRateCache, configs, models, repos

## vuln-inventory.md
- [ ] Write app profile section (app_id, name, language, framework, file count, complexity)
- [ ] Catalog standalone vulnerabilities table:
  - [ ] VULN-01: A03 SQLi — `UsageController.java` → `getUsageByDateRange()` — High
  - [ ] VULN-02: A04 design — `PaymentService.java` → `processPayment()` — Medium
  - [ ] VULN-03: A01 access — `AdminController.java` → `updatePlanRate()` — Medium
  - [ ] VULN-04: A04 validation — `AdminController.java` → `updatePlanRate()` — Medium
  - [ ] VULN-05: A09 audit — `AdminController.java` → `adjustBalance()` — Low
- [ ] Catalog chain-01 links table:
  - [ ] Step 1: A01 — `AdminController.java` → `updatePlanRate()` — Medium
  - [ ] Step 2: A04 — `AdminController.java` → `updatePlanRate()` — Medium
  - [ ] Step 3: A09 — `AdminController.java` → `updatePlanRate()` — Low
- [ ] Catalog decoys table:
  - [ ] `SecurityConfig.java` — BCryptPasswordEncoder
  - [ ] `CustomerController.java` — owner/admin principal check
  - [ ] `BillingAuditProducer.java` — working audit producer
- [ ] Document unannotated exploit surfaces:
  - [ ] `BillingController.java` → `getCustomerInvoices()` — no ownership check → A01 candidate
  - [ ] `BillingService.java` → `getInvoicesByCustomer()` — no audit call → A09 candidate
  - [ ] `HealthService.java` → `currentHealth()` — exposes Kafka/ES URLs → A05 candidate
- [ ] OWASP coverage gap analysis — list uncovered categories: A02, A05, A06, A07, A08, A10
- [ ] No-touch files section — list AdminController, UsageController, PaymentService, SecurityConfig, CustomerController, BillingAuditProducer as no-touch for logic changes

## expansion-plan.md
- [ ] Overview section — 1-2 sentence summary
- [ ] Non-goals / Constraints section
- [ ] Current State table
- [ ] Architecture Changes section — no new infra, leveraging existing Kafka + ES + cache
- [ ] Selected Components for Chain-02 table — UsageController, BillingController, BillingService, BillingAuditProducer
- [ ] Vulnerability Planting Strategy table — per phase
- [ ] Phase Summary table — 5 phases
- [ ] Chain-02 Design section — ASCII flow diagram + component list + difficulty rationale
- [ ] Data Model Changes — "None"
- [ ] API Endpoint Inventory — existing endpoints with new roles
- [ ] Security Benchmark Considerations

## Plan Index README
- [ ] Overview paragraph
- [ ] Architecture Components table
- [ ] Phase Index table — all 5 phases with status "Planned"
- [ ] Key Documents table — links to expansion-plan, vuln-inventory, eval-report
- [ ] OWASP Coverage section — Before vs After
- [ ] Constraints section

## Commit
- [ ] `git add -A && git commit -m "docs(app-10): create complexity upgrade plan, vuln inventory, and phase scaffold"`
