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
- **Chain-01 (EASY to Find & Exploit)**: *Config Leak → SSRF*
  - *Narrative*: Attacker fetches the unauthenticated `/api/debug/env` endpoint to read internal container names and ports. They then make an SSRF call to `/api/feed/import`, supplying an internal URI to access internal microservice details or metadata endpoints.
  - *Subtlety*: Low. The config leak is cleartext, and the SSRF executes synchronously.
- **Chain-02 (HARD to Find & Exploit)**: *SSRF Index Alteration → Elasticsearch Injection → SQLi Pivot*
  - *Narrative*: Attacker uses the SSRF vulnerability to send POST requests directly to the internal Elasticsearch instance at `http://elasticsearch:9200`. The payload modifies the comment index mappings. When the `AnalyticsConsumer` queries Elasticsearch via the search dashboard, the modified index injects a query string payload. This string is then passed to the PostgreSQL repository layer where it is concatenated, causing a SQL injection that exfiltrates administrative account hashes.
  - *Subtlety*: High. The attack spans from SSRF to Elasticsearch index modification, leading to a SQL injection pivot when the database reads values out of the modified search index.
