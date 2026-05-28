# App 06 (hr-management) — Complexity Upgrade Expansion Plan

## Overview

Upgrade the Enterprise HR Management System from an H2-backed Spring Boot prototype to a fully Docker-orchestrated PostgreSQL system with a formalized onboarding workflow state machine, Elasticsearch search injection coverage, and auditable payroll pipeline. Expands OWASP coverage from 3/10 to 7/10 by formalizing an unannotated audit endpoint and planting A04, A03, and A09 vulnerabilities.

> **Non-goals / Constraints**
> - Do **not** remove or fix any planted vulnerability in [vuln-inventory.md](./vuln-inventory.md).
> - Add 1–2 new standalone vulnerabilities per phase, plus new chained scenarios.
> - Add decoy safe code near vulnerable-looking code.
> - Update `.vulns`, `README.md`, `scenarios.md` each phase.
> - Avoid introducing real external network dependencies beyond Docker Compose.

---

## Current State

| Property | Value |
|----------|-------|
| App ID | `app-06` |
| Language | Java |
| Framework | Spring Boot 3.2.5 |
| Build tool | Maven |
| File count | 41 source files, 29 Java classes |
| Endpoints | 20 (13 REST + 7 Thymeleaf web) |
| Standalone vulns | 4 (A01 IDOR, A02 weak XOR, 2x A08 deser + Log4j) |
| Chain scenarios | 1 (chain-01: Payroll IDOR → Weak XOR → DB Exfiltration) |
| Decoys | 3 (BCrypt encoder, parameterized JPA, protected report endpoint) |
| OWASP gaps | A03, A04, A05, A06, A07, A09, A10 |
| Infrastructure | Docker Compose with PostgreSQL 16, Redpanda/Kafka, Elasticsearch 8 |
| Database | H2 in-memory (runtime), PostgreSQL configured in Docker |
| Tests | 5 JUnit 5 tests (context load, XOR round-trip, BCrypt decoy, structure, manifest) |

---

## Architecture Changes

### Selected Components (per generic guide Step 2)

| Component | Current State | Upgrade Action | New Vuln Target |
|-----------|---------------|----------------|-----------------|
| PostgreSQL | Configured in Docker, H2 at runtime | Switch profile to real PostgreSQL | — |
| Onboarding Workflow | **Missing** | Build state machine with endpoints | A04 insecure design |
| Elasticsearch Search | Client exists, safe | Add raw query path | A03 injection |
| Audit Logging | Sparse (only Kafka audit consumer) | Add missing audit in onboarding | A09 logging failure |
| Password Hash Endpoint | `getEmployeeAudit()` exists, unannotated | Formalize as VULN-08 | A01 extended |

### Existing code preserved verbatim

All existing vulnerability-bearing files (`PayrollController.java`, `Employee.java`, `EmployeeImportService.java`, `PayrollAuditConsumer.java`) are no-touch zones. Only new files and the `EmployeeController.java` (to formalize the audit endpoint annotation) are modified.

---

## Vulnerability Planting Strategy

### Per-Phase Summary

| Phase | New Vulns | Chain Additions | Decoy Patterns |
|-------|-----------|-----------------|----------------|
| 1 | — | — | — |
| 2 | A04 (state bypass), formalize audit endpoint (A01) | chain-02 step 1, chain-03 step 1 | Proper state validation on read-only endpoint |
| 3 | A03 (ES injection), A09 (missing audit) | chain-02 step 2 | Parameterized ES query, stdout logging stub |
| 4 | — | chain-03 step 2 (weak session) | Session hardening on a different auth path |

**Total new**: 4 standalone vulnerabilities, 2 new chain scenarios, 1 formalized unannotated finding
**OWASP coverage after upgrade**: A01, A02, A03, A04, A05, A08, A09 — 7/10 covered

---

## Phase Summary

| Phase | Title | Scope | New Vulns |
|-------|-------|-------|-----------|
| 1 | PostgreSQL Migration + Infra Hardening | Switch H2→PostgreSQL, verify Kafka/ES with real Docker, seed data, healthchecks | — |
| 2 | Onboarding State Machine | `OnboardingRequest` entity, workflow service, controller endpoints. Formalize audit endpoint annotation. Plant A04 | A04, formalize audit A01 |
| 3 | Search Injection + Audit Gap | Raw query concat in `EmployeeSearchClient`, missing audit in onboarding workflow, decoys | A03, A09 |
| 4 | UI Enhancement + Chains + Verification | Onboarding pipeline dashboard, finalize chain-02/chain-03, tests, metadata sync, eval | — |

---

## Data Model Changes

### New JPA Entity

| Entity | Table | Fields | Purpose |
|--------|-------|--------|---------|
| `OnboardingRequest` | `onboarding_requests` | id, employeeId, currentState (enum: DRAFT/VERIFIED/BACKGROUND_CHECKED/ACTIVE/REJECTED), requestedBy, reviewedBy, createdAt, updatedAt | Workflow state tracking |

### Existing Entities (no changes)

`Employee`, `Department`, `LeaveRequest` — preserved verbatim.

---

## API Endpoint Inventory

### New Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/onboarding` | HR_ADMIN | Create onboarding request |
| GET | `/api/onboarding/{id}` | HR_ADMIN | Get onboarding status |
| PUT | `/api/onboarding/{id}/transition` | HR_ADMIN | Advance state (Draft→Verified→Background Check→Active) |
| GET | `/api/onboarding` | HR_ADMIN | List all onboarding requests |

### Existing Endpoints (preserved)

All 20 existing endpoints remain unchanged.

---

## Security Benchmark Considerations

- Keep existing benchmark vulnerabilities intact — refer to [vuln-inventory.md](./vuln-inventory.md) before every code change.
- Each phase adds decoy safe patterns near vulnerable-looking code:
  - Phase 2: Proper state validation on a read-only onboarding endpoint
  - Phase 3: Parameterized ES query in same class as A03; stdout logging stub near A09
  - Phase 4: Session hardening on a different auth path
- New code includes realistic "looks vulnerable" areas without removing existing benchmark vulnerabilities.

---

## Deliverables Checklist

- [x] Vuln inventory documented ([vuln-inventory.md](./vuln-inventory.md))
- [x] Expansion plan (this document)
- [ ] Phase 1: PostgreSQL Migration + Infra Hardening
- [ ] Phase 2: Onboarding State Machine
- [ ] Phase 3: Search Injection + Audit Gap
- [ ] Phase 4: UI Enhancement + Chains + Verification
- [ ] `.vulns`, `README.md`, `scenarios.md` updated after each phase
- [ ] All existing vulnerabilities preserved and verified
- [ ] Git commit after phase completion
