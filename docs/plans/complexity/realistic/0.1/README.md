# Complexity Realism Expansion Program — v0.1

## Overview

This directory contains the plans for scaling up the realism and size of benchmark applications in `secure-code-hunt`. The goal is to increase codebase size, architectural complexity, and business-domain fidelity so that security-detection agents face a more realistic codebase — including false positives from decoy safe patterns — rather than toy examples.

## Directory Convention

```
docs/plans/complexity/realistic/
  <version>/
    README.md                          # This file — program overview + application guide
    app-<NN>-<name>/                   # Per-app directory
      vuln-inventory.md                # Existing vulnerability inventory (no-touch zones)
      expansion-plan.md                # High-level expansion plan for this app
    phase-<NN>/                        # Per-phase implementation plan
      plan.md                          # Detailed scope, design decisions, and approach
      TODO.md                          # Granular task checklist for this phase
```

## What This Program Does

1. **Increases realism** — adds reporting, dashboards, audit logs, async jobs, i18n, multi-service boundaries, and shared packages.
2. **Preserves benchmarking integrity** — never removes or fixes existing vulnerabilities; always adds decoy safe patterns near vulnerable-looking code.
3. **Adds new vulnerabilities** — each phase plants 1–2 new standalone vulnerabilities and may extend or create new chained scenarios, following the AGENTS.md spec.
4. **Scales codebase size** — via new services, modules, UI pages, and shared packages.

## How to Apply This Process to Other Apps

### Step 1: Inventory the existing app

Before writing any expansion plan, document:

- **Backend framework & language** (e.g., Flask/Python, Spring Boot/Java, Express/TS)
- **Current file count** and complexity rating (from `APPLICATION_COMPLEXITY.md`)
- **Existing vulnerabilities** — list every `// VULNERABILITY` and `// CHAIN LINK` comment with file, method, OWASP ID, severity
- **Existing decoys** — list every entry in `.vulns` → `"decoys"`
- **Current architecture** — single-file? layered? does it have controllers/services/repositories?
- **Current endpoints** — full route table

Create a `docs/plans/complexity/realistic/<version>/app-<NN>-<name>/vuln-inventory.md` with this data.

### Step 2: Identify expansion dimensions

Choose from these dimensions based on the app's business domain:

| Dimension | Examples |
|-----------|----------|
| **New business workflows** | Reporting, approvals, notifications, audit trails |
| **New service boundaries** | Split monolith into 2–3 microservices with clear API contracts |
| **Async processing** | Job queues, scheduled tasks, webhook callbacks |
| **Multi-language UI** | React/Vue frontend consuming the same APIs |
| **i18n / l10n** | Locale dictionaries, RTL support, locale switcher |
| **Shared packages** | Shared DTOs, validation rules, type definitions |
| **Platform capabilities** | Feature flags, observability pages, retry policies |
| **Data model growth** | New entities, relationships, aggregate views |

### Step 3: Define phases

Break the expansion into **sequential phases** of roughly equal effort. Each phase should:

- Be completable in a single implementation session
- Produce a working, testable increment
- Include its own `plan.md` + `TODO.md`
- Add 1–2 new standalone vulnerabilities + extend/update `.vulns`/`README.md`/`scenarios.md`

**Recommended phase ordering** (derived from lessons learned on app-01):

| Phase | Content | Why first/last |
|-------|---------|----------------|
| 1 | **Architecture refactor + shared packages** | Must come first — building microservices after refactoring is cheaper than migrating later |
| 2 | **Core new business features (MVP)** | Smallest viable new functionality to validate the refactored architecture |
| 3 | **Async + exports + audit** | Depends on core features being stable |
| 4 | **UI expansion + i18n** | Consumes the APIs built in phases 2–3 |
| 5 | **Advanced features** | Caching, scheduling, webhooks, feature flags — polish items |

### Step 4: Design vulnerability planting per phase

For each phase, specify:

- **Target OWASP categories** — prefer categories not yet covered in the existing app
- **Standalone vulnerability count** — 1–2 per phase
- **Chain scenario additions** — extend an existing chain, or create a new cross-service chain
- **Decoy pattern placement** — which new feature area gets a safe-looking-but-vulnerable pattern nearby
- **Artifact updates** — `.vulns`, `README.md`, `scenarios.md` must be updated each phase

### Step 5: Write the expansion plan

Follow this template in `expansion-plan.md`:

```markdown
# App NN (<name>) — Realistic Complexity Expansion Plan

## Overview
## Current State (summary from vuln-inventory.md)
## Architecture Changes
## Vulnerability Planting Strategy
## Feature Inventory by Phase
## Data Model Changes
## API Endpoint Inventory
## Security Benchmark Considerations
## Testing Plan
```

### Step 6: Write per-phase plans

Each `phase-<NN>/plan.md` should contain:

```markdown
# Phase NN: <Title>

## Goal
## Scope (features included / excluded)
## Architecture Decisions
## Vulnerability Planting
| # | Type | OWASP | Location | Description | Severity |
|---|------|-------|----------|-------------|----------|
## Decoy Patterns
| # | Location | Why it looks vulnerable | Why it is safe |
## Data Model Changes
## API Contracts
## Artifact Updates (.vulns, README, scenarios.md)
## Dependencies on other phases
```

Each `phase-<NN>/TODO.md` should be a granular checklist of files to create/modify.

### Step 7: Implement phase by phase

Execute phases in order. After each phase:
1. Verify existing vulnerabilities remain intact
2. Verify new vulnerabilities are exploitable
3. Verify decoy patterns exist near vulnerable code
4. Run tests if available
5. Update `.vulns`, `README.md`, `scenarios.md`
6. Commit

---

## Throwaway Directories

During implementation, throwaway directories may be created for build artifacts, virtual environments, or package installation. All such directories must be covered by `.gitignore` patterns. The root `.gitignore` should include:

```
# Throwaway directories for complexity expansion
throwaway/
**/throwaway/
.venv/
venv/
```

These directories should be created at the project root or within `apps/<language>/app-<NN>-<name>/` as needed and must never be committed.

---

## Versions

| Version | Date | Scope |
|---------|------|-------|
| 0.1 | 2026-05 | Initial program: app-01 expansion definition |