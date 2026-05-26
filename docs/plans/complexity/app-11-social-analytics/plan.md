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

## 4. Impact on Planted Vulnerabilities
- **VULN-01 (A03 - SQL Injection)**: The endpoint `/api/dashboards/search` remains vulnerable. The repository layer executes raw SQL string interpolation, exposing PostgreSQL-specific SQLi vulnerabilities.
- **VULN-02 (A05 - Security Misconfiguration)**: The `/api/debug/env` config dump endpoint remains active. It leaks credentials for PostgreSQL, Redis, Elasticsearch, and Kafka.
- **VULN-03 (A10 - Server-Side Request Forgery)**: The feed integration endpoint `/api/feed/import` takes user-supplied URLs. With Kafka, Elasticsearch, and Redis inside the private network, the attacker can use the SSRF to interact with internal components (e.g. accessing Elasticsearch REST API at `http://elasticsearch:9200` to dump search indices).
- **Chain-01 (Debug Leak → SSRF → Internal Pivot)**: Attacker reads database and broker configurations, uses the SSRF to pivot and modify Elasticsearch indices or alter Kafka settings.
- **Chain-02 (State Confusion Pivot to SSRF)**: Attacker exploits background state delays in Kafka consumer pipelines to bypass validation checks.
