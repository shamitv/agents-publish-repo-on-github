# Todo List: app-17-iot-dashboard Complexity Upgrade

This checklist tracks the tasks required to implement the enterprise architecture for the IoT Device Dashboard.

## Phase 1: Scaffold & Dependencies
- [ ] Add npm packages to `package.json`:
  - `pg`
  - `redis`
  - `@opensearch-project/opensearch` (OpenSearch client)
  - `kafkajs`
  - `ws` (WebSockets)
- [ ] Initialize modular codebase structure under `src/`: `config`, `controllers`, `routes`, `services`, `consumers`.

## Phase 2: Docker Compose Setup
- [ ] Create `docker-compose.yml` specifying:
  - `web` (Express app + WebSocket hub)
  - `db` (PostgreSQL 15)
  - `opensearch` (OpenSearch 2)
  - `redis` (Redis 7)
  - `zookeeper`
  - `kafka`
- [ ] Setup wait scripts for database, elastic, and broker services.

## Phase 3: Polyglot Database Migration
- [ ] Setup DB connection pools under `src/config/`.
- [ ] Write SQL schema migrations for standard tables and a partitioned `telemetry_streams` table.
- [ ] Seed tables with mock devices.

## Phase 4: OpenSearch Log Integration
- [ ] Initialize OpenSearch client and log index configuration in `src/config/opensearch.js`.
- [ ] Write logger service to write audit events to OpenSearch.

## Phase 5: Kafka Event Streaming & WebSockets
- [ ] Configure `kafkajs` client and producer.
- [ ] Refactor telemetry API to emit events to Kafka.
- [ ] Implement `src/consumers/TelemetryConsumer.js` to process events, update database partitions, push metrics to WebSockets, and log alerts to OpenSearch.

## Phase 6: Enterprise UI Implementation
- [ ] Build a WebSockets-enabled HTML panel displaying live telemetry charts, diagnostic query panel (connected to OpenSearch), and command consoles.

## Phase 7: Verification
- [ ] Verify plaintext device credentials leak (A02) displays PostgreSQL database values correctly.
- [ ] Verify SSRF (A10) operates and can target Redis, OpenSearch, and Kafka hosts.
- [ ] Confirm configuration leak (A05) reveals the new database and broker credentials.
- [ ] Run the complete integration tests using Docker Compose.

- [ ] Audit all source code to ensure NO comments or annotations exist that can tip off agents. Limit all vulnerability/chain mapping details strictly to `.vulns` and `scenarios.md`.
