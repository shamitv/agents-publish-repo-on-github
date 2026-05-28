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
├── routes/             # Route mapping definitions
├── services/           # CommandEngine, AlertManager
├── consumers/          # Kafka event listeners (TelemetryConsumer)
├── public/             # WebSocket-enabled admin telemetry console
└── server.js           # Server runner and WebSocket setups
```

---

## 4. Vulnerabilities & Exploit Chains Detail

### Standalone Vulnerabilities
- **VULN-01 (A02 - Plaintext API Tokens)**:
  - *Location*: `src/controllers/deviceController.js`
  - *Description*: Device credentials and API keys are stored in plaintext in the PostgreSQL database and returned in debug responses.
  - *Decoy Safeguard*: User account passwords are hashed with high-entropy Bcrypt.
- **VULN-02 (A05 - Debug Configuration Leak)**:
  - *Location*: `src/routes/debug.js`
  - *Description*: System profiling endpoint `/api/debug/system` dumps active environment variables, leaking Kafka, PostgreSQL, and OpenSearch connection strings.
- **VULN-03 (A10 - SSRF in Firmware Updater)**:
  - *Location*: `src/services/commandEngine.js`
  - *Description*: The firmware download client fetches files from a user-supplied URL parameter without checking internal IP restrictions.

### Exploit Chains
#### chain-01: Debug Config Leak -> Internal HTTP SSRF -> Plaintext Device Token Exposure
- **Impact**: `lateral_movement`
- **Attack narrative**: An attacker reads the unauthenticated system debug endpoint to learn internal service addresses, passes an internal HTTP URL to the firmware updater SSRF, and uses the server-side request to retrieve internal device/debug data that exposes plaintext device API tokens for use against other device-management endpoints.

| Step | Issue | Severity (standalone) | OWASP | CWE | Location | Method |
|------|-------|-----------------------|-------|-----|----------|--------|
| 1 | System debug endpoint exposes service topology and credentials without authentication. | Low | A05 | CWE-200 | `src/routes/debug.js` | `systemProfile()` |
| 2 | Firmware updater fetches attacker-supplied HTTP URLs without blocking internal hosts. | Medium | A10 | CWE-918 | `src/services/commandEngine.js` | `downloadFirmware()` |
| 3 | Device debug response exposes plaintext device API tokens from PostgreSQL. | Medium | A02 | CWE-312 | `src/controllers/deviceController.js` | `getDeviceDebug()` |

---

## 5. Benchmark Metadata Requirements
- **Source Annotations Required**: Source code must retain the `AGENTS.md` benchmark comments: `// VULNERABILITY <OWASP_ID>: <brief description>` for each standalone vulnerability and `// CHAIN LINK <N> (chain-<ID>): <description>` for every chain step.
- **Metadata Synchronization**: `.vulns`, the README chain section, this plan's chain table, and source comments must agree on OWASP ID, severity, CWE, impact, location, and method.
- **README Chain Section Required**: The app README must keep the required `Chained Vulnerability Scenario` section. `scenarios.md` may provide supplemental narrative, but it must not replace README or `.vulns` content.
- **Decoys Required**: Preserve nearby safe decoy patterns and list them in `.vulns.decoys`.
