# Todo List: app-11-social-analytics Complexity Upgrade

This checklist tracks the tasks required to implement the enterprise architecture for the Social Media Analytics Dashboard.

## Phase 1: Scaffold & Dependencies
- [ ] Add npm packages to `package.json`:
  - `pg` and `@types/pg`
  - `redis`
  - `elasticsearch`
  - `kafkajs` (Kafka JS client)
  - `ws` and `@types/ws` (WebSocket support)
- [ ] Create modular TS directory layout under `src/`: `config`, `controllers`, `routes`, `services`, `repositories`, `consumers`.

## Phase 2: Docker Compose Setup
- [ ] Create `docker-compose.yml` specifying:
  - `web` (TypeScript app + Websocket server)
  - `db` (PostgreSQL 15)
  - `elasticsearch` (Elasticsearch 8)
  - `redis` (Redis 7)
  - `zookeeper`
  - `kafka`
- [ ] Configure startup delay parameters for the `web` service.

## Phase 3: Polyglot Database Migration
- [ ] Implement DB connection singletons under `src/config/`.
- [ ] Write SQL schema migrations for standard tables and a partitioned `analytics_events` table.
- [ ] Seed tables with mock analytics profiles.

## Phase 4: Elasticsearch Search Integration
- [ ] Initialize Elasticsearch index mapping in `src/config/elastic_client.ts`.
- [ ] Write SyncManager service to stream new metrics from database to Elasticsearch.
- [ ] Implement search controllers utilizing the Elasticsearch client.

## Phase 5: Kafka Event Streaming & WebSockets
- [ ] Configure `kafkajs` client and producer.
- [ ] Refactor metrics ingestion endpoint to publish metrics events to Kafka.
- [ ] Implement `src/consumers/analytics_consumer.ts` to consume events, write database partitions, update Elasticsearch, and push updates to WebSocket clients.

## Phase 6: Enterprise UI Implementation
- [ ] Build a WebSocket-connected HTML dashboard displaying dynamic charts, live updates, and a search panel connected to Elasticsearch.

## Phase 7: Verification
- [ ] Audit all source code to ensure NO comments or annotations exist that can tip off agents. Limit all vulnerability/chain mapping details strictly to `.vulns` and `scenarios.md`.
- [ ] Verify SQL injection (A03) works on the PostgreSQL database.
- [ ] Verify SSRF (A10) operates and can target Redis, Elasticsearch, and Kafka hosts.
- [ ] Confirm configuration leak (A05) reveals all new database and broker credentials.
- [ ] Run the complete integration tests using Docker Compose.
