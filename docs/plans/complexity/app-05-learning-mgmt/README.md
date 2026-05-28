# Complexity Upgrade Plan — app-05: Online Learning Management System

## Overview

Upgrade the LMS from stub-backed infrastructure (SQLite, in-memory Kafka mock, simulated MongoDB) to a Docker-orchestrated enterprise system with real PostgreSQL, MongoDB, Apache Kafka, auto-grading business logic, and student/instructor portal dashboards. Expands OWASP coverage from 3/10 to 8/10.

## Phase Index

| Phase | Title | Focus | New Vulns | Progress |
|-------|-------|-------|-----------|----------|
| [1](phase-01/plan.md) | Infrastructure + Docker Compose | Real PostgreSQL, MongoDB, Kafka; healthchecks; config swap | — | Planned |
| [2](phase-02/plan.md) | Polyglot Persistence + Core CRUD | Schema migrations, repository port, seed data, A04 planting | A04 | Planned |
| [3](phase-03/plan.md) | Business Logic + Auto-Grading | Prereq validator, grading engine, rate limiter, A09 planting | A09 | Planned |
| [4](phase-04/plan.md) | Real Kafka Streaming + Enterprise UI | Kafka producer/consumer, student/instructor dashboards, A10+A07 planting | A10, A07 | Planned |
| [5](phase-05/plan.md) | Advanced Features + Verification | Chain scenarios, decoys, metadata sync, full test pass | — | Planned |

## Key Documents

| Document | Description |
|----------|-------------|
| [expansion-plan.md](./expansion-plan.md) | Master plan with architecture changes, vulnerability strategy, data model, API inventory |
| [vuln-inventory.md](./vuln-inventory.md) | No-touch zone reference of existing vulnerabilities, chains, and decoys |

## OWASP Target

After completion: **A01, A02 (chain), A04, A05, A07, A08, A09, A10** — 8/10 categories covered.
