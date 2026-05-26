# Complexity Upgrade Plan: app-11-social-analytics (Enterprise Architecture)

This document details the architectural plan to upgrade the Social Media Analytics Dashboard to an event-driven, multi-database TypeScript application.

## 1. Overview
The application will be restructured into a modular, clean-architecture codebase:
- **Polyglot & Timeseries Storage**: PostgreSQL for account details and dashboard setups; TimescaleDB or partitioned PostgreSQL tables for high-frequency social media metrics.
- **Search Service**: Elasticsearch for fuzzy searches on feed comments and user posts.
- **Event Streaming**: Apache Kafka for processing real-time social metrics events.
- **Modular Codebase**: Implement a TypeScript-structured directory: `routes/`, `controllers/`, `services/`, `repositories/`, `consumers/`.
- **Enterprise UI**: Portal dashboard displaying real-time analytics graphs, metric tracking logs, and a social feed search panel utilizing Websockets.

---

## 2. Component Design

### A. Database Layer (PostgreSQL & Timeseries Partitions)
- **PostgreSQL**: Stores accounts and dashboard details.
- **Timeseries Table**: A partitioned table `analytics_events` logs feed activities (`likes`, `comments`, `shares`, `timestamp`).

### B. Search Service (Elasticsearch)
- **Engine**: Elasticsearch 8
- **Role**: Index social feed comments to allow search and sentiment analysis.
- **Sync**: A sync daemon reads new metrics from the timeseries table and writes them to the Elasticsearch comments index.

### C. Event Streaming (Apache Kafka)
- **Engine**: Apache Kafka
- **Role**: Process high-volume analytics inputs.
- **Work Flow**:
  1. Social webhooks send events to the `/api/metrics/ingest` endpoint.
  2. The controller publishes the raw JSON to the `social-events` topic.
  3. The `AnalyticsConsumer` consumes events, writes them to the Timeseries table, indexes comments in Elasticsearch, and triggers live updates via Websockets.

---

## 3. Modular Code Structure
```
src/
├── config/             # DB, Kafka, Redis, and Elasticsearch clients
├── controllers/        # Express controllers (DashboardController)
├── routes/             # Router declarations mapping endpoints to controllers
├── services/           # AnalyticsEngine, SyncManager
├── repositories/       # Data-access objects wrapping PostgreSQL and Elastic queries
├── consumers/          # Kafka event listeners (AnalyticsConsumer)
├── public/             # HTML/JS dashboard UI using Chart.js and WebSockets
└── server.ts           # App entrypoint and WebSocket server
```

---

## 4. Vulnerabilities & Exploit Chains Detail

### Standalone Vulnerabilities
- **VULN-01 (A03 - SQL Injection on Dashboard Search)**:
  - *Location*: `src/repositories/DashboardRepository.ts` → `search()`
  - *Description*: Searches saved analytics dashboards using direct string concatenation inside a raw PostgreSQL client query.
  - *Decoy Safeguard*: The user login queries are fully parameterized.
- **VULN-02 (A05 - Debug Configurations Exposure)**:
  - *Location*: `src/controllers/configController.ts` → `getEnv()`
  - *Description*: Unauthenticated configuration route returns process environment variables, exposing database passwords, Redis URLs, and Kafka broker paths.
- **VULN-03 (A10 - Server-Side Request Forgery)**:
  - *Location*: `src/services/SyncManager.ts` → `importFeed()`
  - *Description*: Import endpoint queries feed settings from a user-supplied URL. It fails to validate internal hostname resolutions, enabling connections to internal Docker containers.

### Exploit Chains
#### chain-01: Debug Environment Leak -> Internal HTTP SSRF
- **Impact**: `lateral_movement`
- **Attack narrative**: An attacker reads the unauthenticated debug environment endpoint to discover internal Docker service names, ports, and credentials, then submits one of those internal HTTP URLs to the feed import SSRF so the application server fetches internal-only search or service endpoints from the trusted network.

| Step | Issue | Severity (standalone) | OWASP | CWE | Location | Method |
|------|-------|-----------------------|-------|-----|----------|--------|
| 1 | Debug environment route exposes internal service hostnames, ports, and credentials without authentication. | Low | A05 | CWE-200 | `src/controllers/configController.ts` | `getEnv()` |
| 2 | Feed importer fetches attacker-supplied HTTP URLs without hostname or private-network validation. | Medium | A10 | CWE-918 | `src/services/SyncManager.ts` | `importFeed()` |

---

## 5. Benchmark Metadata Requirements
- **Source Annotations Required**: Source code must retain the `AGENTS.md` benchmark comments: `// VULNERABILITY <OWASP_ID>: <brief description>` for each standalone vulnerability and `// CHAIN LINK <N> (chain-<ID>): <description>` for every chain step.
- **Metadata Synchronization**: `.vulns`, the README chain section, this plan's chain table, and source comments must agree on OWASP ID, severity, CWE, impact, location, and method.
- **README Chain Section Required**: The app README must keep the required `Chained Vulnerability Scenario` section. `scenarios.md` may provide supplemental narrative, but it must not replace README or `.vulns` content.
- **Decoys Required**: Preserve nearby safe decoy patterns and list them in `.vulns.decoys`.
