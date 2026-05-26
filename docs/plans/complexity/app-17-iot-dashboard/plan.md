# Complexity Upgrade Plan: app-17-iot-dashboard (Enterprise Architecture)

This document details the architectural plan to upgrade the IoT Device Dashboard to a multi-database, event-driven JavaScript application.

## 1. Overview
The current monolithic JavaScript app will be split into a decoupled, modular MVC architecture:
- **Polyglot & Timeseries Storage**: PostgreSQL for device configuration; TimescaleDB or partitioned PostgreSQL tables for streaming telemetry counters.
- **Search & Logs Service**: OpenSearch / Elasticsearch for device audit trails and diagnostics search.
- **Event Streaming**: Apache Kafka for streaming high-frequency device telemetry data.
- **Modular Codebase**: Split code into distinct packages: `routes/`, `controllers/`, `services/`, `consumers/`, `config/`.
- **Enterprise UI**: Portal console displaying live telemetry metrics (via Line charts and WebSockets), device status logs, and a diagnostics query page.

---

## 2. Component Design

### A. Database Layer (PostgreSQL & TimescaleDB)
- **PostgreSQL**: Stores persistent tables (`users`, `devices`, `commands`).
- **Timeseries Table**: A partitioned table `telemetry_streams` logs sensor counts (`device_id`, `temperature`, `humidity`, `timestamp`).

### B. Search & Logs Service (OpenSearch)
- **Engine**: OpenSearch 2 / Elasticsearch 8
- **Role**: Index device logs, registration actions, and error reports for diagnostic lookup.
- **Sync**: Background synchronization logs events directly to OpenSearch.

### C. Event Streaming (Apache Kafka)
- **Engine**: Apache Kafka
- **Role**: Stream and process incoming sensor updates.
- **Work Flow**:
  1. IoT devices post sensor metrics to `/api/telemetry/log`.
  2. The controller publishes the metrics to the `iot-telemetry` topic.
  3. The `TelemetryConsumer` listens to the topic, writes records to the TimescaleDB partition, pushes telemetry updates to live WebSockets, and index alert triggers in OpenSearch.

---

## 3. Modular Code Structure
```
src/
├── config/             # DB, Kafka, Redis, and OpenSearch clients
├── controllers/        # Express controllers (DeviceController, TelemetryController)
├── routes/             # Route mapping declarations
├── services/           # CommandEngine, AlertManager
├── consumers/          # Kafka event listeners (TelemetryConsumer)
├── public/             # WebSocket-enabled admin telemetry console
└── server.js           # Server runner and WebSocket setups
```

---

## 4. Impact on Planted Vulnerabilities
- **VULN-01 (A02 - Cryptographic Failures)**: Plaintext API tokens are saved in PostgreSQL. Access control flaws in search endpoints allow unauthorized users to query these plaintext credentials.
- **VULN-02 (A05 - Security Misconfiguration)**: The debug endpoint `/api/debug/system` remains active. It leaks settings for PostgreSQL, Redis, Kafka, and OpenSearch.
- **VULN-03 (A10 - Server-Side Request Forgery)**: The firmware update function `/api/devices/update` requests files from a user-supplied URL. With OpenSearch and Kafka inside the network, this SSRF becomes highly dangerous, allowing attackers to query the OpenSearch index API (`http://opensearch:9200`) or manipulate Kafka broker settings.
- **Chain-01 (API Key Leak → SSRF → Internal Pivot)**: Attacker reads plaintext device credentials, uses the SSRF firmware update endpoint to pivot requests internally, and alters OpenSearch data or Kafka streams.
- **Chain-02 (State Confusion Pivot to IDOR)**: Attacker leverages Kafka message queue delays to bypass command-queue state checks and read other device configurations.
