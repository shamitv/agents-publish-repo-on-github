# Master Complexity Upgrade Plan

This document serves as the wrapper plan for upgrading 8 selected benchmark applications in the secure-code-hunt repository to modeled enterprise full-stack architectures.

---

## 1. Upgrade Objectives

The goal of this phase is to scale the target applications from simple in-memory/SQLite monoliths to multi-container, modular environments. This upgrade:
1. **Models Real-World Complexity**: Implements polyglot persistence, event-driven task queues, fuzzy search services, and dynamic business rule calculations.
2. **Evaluates Advanced Security Scenarios**: Tests the ability of AI detection agents to trace exploit chains across distributed services (e.g. databases, event consumers, cache backends).
3. **Maintains Benchmark Metadata Compliance**: Preserves the annotation, README, `.vulns`, and decoy requirements defined in the repository `AGENTS.md` contribution spec.

---

## 2. Directory Index of Application Upgrade Plans

Below is the index of the 8 selected applications, their architectural upgrades, and links to their individual plans and checklists:

| App ID | Application Name | Language / Tech Stack | Core Upgrades | Detailed Plan | Implementation Checklist |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **01** | E-Commerce Product Catalog API | Python (Flask) | Postgres, MongoDB, Elasticsearch, Kafka, MVC, Dashboard | [Plan](app-01-ecommerce-catalog/plan.md) | [Checklist](app-01-ecommerce-catalog/todo.md) |
| **05** | Online Learning Management System | Python (Flask) | Postgres, MongoDB, Kafka, Blueprints, Auto-Grading Rules | [Plan](app-05-learning-mgmt/plan.md) | [Checklist](app-05-learning-mgmt/todo.md) |
| **06** | Enterprise HR Management System | Java (Spring Boot) | Postgres, Elasticsearch, Kafka, MVC, Log4j RCE Listener | [Plan](app-06-hr-management/plan.md) | [Checklist](app-06-hr-management/todo.md) |
| **10** | Telecom Billing Platform | Java (Spring Boot) | Postgres, TimescaleDB, Kafka, MVC, Multi-Tier Tariffs | [Plan](app-10-telecom-billing/plan.md) | [Checklist](app-10-telecom-billing/todo.md) |
| **11** | Social Media Analytics Dashboard | TypeScript (Express) | Postgres, Timeseries, Elasticsearch, Kafka, MVC, WebSockets | [Plan](app-11-social-analytics/plan.md) | [Checklist](app-11-social-analytics/todo.md) |
| **14** | Telemedicine Appointment System | TypeScript (Express) | Postgres, MongoDB, Kafka, MVC, Calendar validation | [Plan](app-14-telemedicine/plan.md) | [Checklist](app-14-telemedicine/todo.md) |
| **17** | IoT Device Dashboard | JavaScript (Express) | Postgres, InfluxDB, OpenSearch, Kafka, MVC, WebSockets | [Plan](app-17-iot-dashboard/plan.md) | [Checklist](app-17-iot-dashboard/todo.md) |
| **36** | Parking Management System | JavaScript (Express) | Postgres, MongoDB, Elasticsearch, Kafka, Dynamic Pricing | [Plan](app-36-parking-mgmt/plan.md) | [Checklist](app-36-parking-mgmt/todo.md) |

---

## 3. Global Constraints & Standards

Every upgraded application must adhere to the following standards:

### Benchmark Metadata Compliance
- **Source Annotations Required**: Standalone vulnerabilities must retain source comments in the form `// VULNERABILITY <OWASP_ID>: <brief description>`.
- **Chain Link Annotations Required**: Every chain component must retain a source comment in the form `// CHAIN LINK <N> (chain-<ID>): <description>`.
- **Manifest Source of Truth**: `.vulns` remains the machine-readable ground-truth manifest for standalone vulnerabilities, chained attacks, and decoys.
- **README Chain Section Required**: Each app `README.md` must keep the `Chained Vulnerability Scenario` section required by `AGENTS.md`, including the chain table and attack narrative.
- **Supplemental Scenarios Only**: `scenarios.md` may add extra internal narrative, but it must not replace required README or `.vulns` content.

### Docker Compose Orchestration
- All upgraded applications must be configured as a multi-container suite inside a `docker-compose.yml` file.
- Containers must utilize healthchecks to manage startup dependency sequences (e.g. blocking the application container until database and broker ports accept connections).

### Polyglot & Search Integration
- Relational tables (users, logs, billing) must be stored in PostgreSQL.
- Flexible structures (catalogs, notes) must be stored in MongoDB.
- Timeseries logs (telemetry, call records) must use partitioned tables or InfluxDB.
- Searches must pass through Elasticsearch or OpenSearch queries.
