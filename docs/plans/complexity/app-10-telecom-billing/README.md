# Complexity Upgrade Plan — app-10: Telecom Billing Platform

## Overview

Upgrade exploit complexity by adding a new cross-component chain (chain-02) spanning 4 components across 3 layers, plus 1 new standalone A05 vulnerability and 2 decoys. Existing chain-01 (single-file, single-endpoint) is preserved untouched. Zero logic changes — annotations and metadata only.

## Architecture Components

| Component | Technology | Purpose | Role in Chain-02 |
|-----------|-----------|---------|-------------------|
| Usage Controller | Spring MVC | Usage record search by date range | Step 1 — SQLi reconnaissance |
| Billing Controller | Spring MVC | Invoice lookup + payment | Step 2 — IDOR bulk invoice read |
| Billing Service | Spring @Service | Invoice business logic | Step 3 — audit bypass on reads |
| Billing Audit Producer | Spring Kafka | Kafka audit event publishing | Bypassed — available but not called |
| Health Service | Spring @Service | Container health check | Standalone A05 — infra URL leak |

## Phase Index

| Phase | Title | Focus | New Vulns | New Decoys | Status |
|:-----:|-------|-------|:---------:|:----------:|--------|
| [1](phase-01/plan.md) | Inventory & Gap Analysis | Catalog existing vulns, chains, decoys; map OWASP gaps | — | — | Planned |
| [2](phase-02/plan.md) | Standalone A05 — Health Info Leak | Annotate health endpoint infra URL exposure | 1 (A05) | 1 | Planned |
| [3](phase-03/plan.md) | Chain-02 — Multi-Component Exploit Chain | SQLi → IDOR → Audit Bypass across 4 components | 2 (A01, A09) | 2 | Planned |
| [4](phase-04/plan.md) | Integration Verification & Metadata Sync | Tests, Docker smoke, master index update | — | — | Planned |
| [5](phase-05/plan.md) | Evaluation | Difficulty ratings, hint leakage validation | — | — | Planned |

## Key Documents

| Document | Description |
|----------|-------------|
| [expansion-plan.md](./expansion-plan.md) | Master plan: architecture, vulnerability strategy, phase summary |
| [vuln-inventory.md](./vuln-inventory.md) | No-touch zone: catalog of existing vulns, chains, decoys |
| [eval-report.md](./eval-report.md) | Difficulty ratings (1-5) + hint leakage validation |

## OWASP Coverage

| State | Covered Categories | Uncovered |
|-------|--------------------|-----------|
| Before | A01, A03, A04, A09 | A02, A05, A06, A07, A08, A10 |
| After | A01, A03, A04, A05, A09 | A02, A06, A07, A08, A10 |

## Constraints

- Never remove or fix existing `// VULNERABILITY` or `// CHAIN LINK` annotations
- Never remove or weaken existing decoy patterns
- Every new chain step must have real, exploitable code (annotations capture pre-existing exploitable code)
- Near every vulnerable code path, verify a decoy safe pattern exists
- Update `.vulns`, `README.md`, and `scenarios.md` after every phase
