# Complexity Upgrade Plan — app-06: Enterprise HR Management System

## Overview

Upgrade the HR system from H2-backed Spring Boot to real PostgreSQL with a formalized onboarding workflow state machine, Elasticsearch injection coverage, and auditable payroll pipeline. Expands OWASP coverage from 3/10 to 7/10.

## Architecture Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Primary DB | PostgreSQL 16 (via Docker) | Employee, department, leave, onboarding data |
| Search | Elasticsearch 8 | Employee profile search |
| Event Bus | Redpanda (Kafka API) | Payroll audit events |
| State Machine | Custom Java (enum + service) | Onboarding workflow |

## Phase Index

| Phase | Title | Focus | New Vulns | Status |
|-------|-------|-------|-----------|--------|
| [1](phase-01/plan.md) | PostgreSQL Migration + Infra Hardening | H2→PostgreSQL, verify Kafka/ES, seed data | — | ⬜ Not started |
| [2](phase-02/plan.md) | Onboarding State Machine | Workflow service, A04 planting, formalize audit endpoint | A04, formalize A01 | ⬜ Not started |
| [3](phase-03/plan.md) | Search Injection + Audit Gap | ES injection A03, missing audit A09 | A03, A09 | ⬜ Not started |
| [4](phase-04/plan.md) | UI Enhancement + Chains + Verification | Onboarding dashboard, chain finalization, metadata sync | — | ⬜ Not started |

## Key Documents

| Document | Description |
|----------|-------------|
| [expansion-plan.md](./expansion-plan.md) | Master plan with architecture, vulnerability strategy, API inventory |
| [vuln-inventory.md](./vuln-inventory.md) | No-touch zone reference of existing vulnerabilities, chains, and decoys |

## OWASP Coverage

Before: A01, A02, A08 — 3/10
After: A01, A02, A03, A04, A05, A08, A09 — 7/10 (+A07 via chain)
