# Phase 01: Inventory & Gap Analysis

## Goal

Catalog every existing vulnerability, chain link, and decoy in app-10. Identify unannotated exploit surfaces. Map OWASP coverage gaps to inform Phase 2 and 3 vulnerability planting decisions. Create the no-touch reference inventory and the master plan documents.

## Scope

### Included
- [ ] Create `docs/plans/complexity/app-10-telecom-billing/` directory structure (5 phase directories)
- [ ] Create `vuln-inventory.md` — full catalog of existing state
- [ ] Create `expansion-plan.md` — master plan covering architecture, vulnerability strategy, phase summary
- [ ] Create `README.md` — app-level phase index linking all phases and key documents
- [ ] Search all source `.java` files for `VULNERABILITY` and `CHAIN LINK` annotations — verify 5 standalone + 3 chain link occurrences
- [ ] Catalog OWASP gaps: A02, A05, A06, A07, A08, A10 uncovered → A05 selected for Phase 2
- [ ] Identify unannotated exploit surfaces:
  - BillingController.getCustomerInvoices() — no ownership check (A01 IDOR candidate)
  - BillingService.getInvoicesByCustomer() — no audit producer call (A09 candidate)
  - HealthService.currentHealth() — exposes infra URLs to unauthenticated callers (A05 candidate)

### Excluded
- Any source file modifications — this phase is documentation-only
- Any .vulns or README changes — will happen in Phases 2-4

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Keep chain-01 untouched | AGENTS.md constraint: never remove or fix existing annotations. Chain-01 remains as the baseline single-file chain for comparison. |
| Add chain-02 rather than modify chain-01 | Adds independent cross-component depth without risking existing benchmark integrity. Allows agents to be tested on both single and multi-component chains. |
| Select A05 for new standalone | HealthService leak is already exploitable — needs only annotation, zero logic change. Fills a documented OWASP gap. |
| 5-phase structure | Follows generic-upgrade-guide.md template: Inventory → Standalone → Chain → Verify → Evaluate |

## Vulnerability Planting

None — inventory and planning phase only.

## Data Model Changes

None.

## API Contracts

None.

## Artifact Outputs

| File | Status |
|------|--------|
| `docs/plans/complexity/app-10-telecom-billing/README.md` | Created |
| `docs/plans/complexity/app-10-telecom-billing/expansion-plan.md` | Created |
| `docs/plans/complexity/app-10-telecom-billing/vuln-inventory.md` | Created |
| `phase-01/plan.md` | This file |
| `phase-01/TODO.md` | Created |

## Dependencies

- **Depends on**: Nothing — this is the first phase
- **Required by**: Phase 2 — needs OWASP gap analysis and no-touch file list
