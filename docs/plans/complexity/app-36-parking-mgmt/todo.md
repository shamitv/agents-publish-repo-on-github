# Todo List: app-36-parking-mgmt Complexity Upgrade

This checklist tracks the tasks required to implement the enterprise architecture for the Parking Management System.

## Phase 1: Scaffold & Dependencies
- [ ] Add npm packages to `package.json`:
  - `pg`
  - `mongodb`
  - `redis`
  - `elasticsearch`
  - `kafkajs`
- [ ] Initialize modular codebase structure under `src/`: `config`, `controllers`, `routes`, `services`, `consumers`.

## Phase 2: Docker Compose Setup
- [ ] Create `docker-compose.yml` specifying:
  - `web` (Express app + background listeners)
  - `db` (PostgreSQL 15)
  - `mongodb` (MongoDB 6)
  - `elasticsearch` (Elasticsearch 8)
  - `redis` (Redis 7)
  - `zookeeper`
  - `kafka`
- [ ] Setup wait scripts for all database and broker services.

## Phase 3: Polyglot Database Migration
- [ ] Setup DB connection pools under `src/config/`.
- [ ] Write SQL schema migrations for PostgreSQL tables (`users`, `reservations`, `payments`).
- [ ] Setup MongoDB client configuration for parking lot layouts and dynamic rules.

## Phase 4: Business Logic & Rules
- [ ] Implement `src/services/DynamicPricing.js` computing fees based on occupancy density, hour range, and membership status.

## Phase 5: Elasticsearch Search Integration
- [ ] Initialize Elasticsearch index mapping in `src/config/elastic_client.js`.
- [ ] Write sync task to index parking spot lists into Elasticsearch.
- [ ] Implement search controllers utilizing the Elasticsearch client.
- [ ] Keep search string concatenation in the Elasticsearch Query DSL string to maintain the injection vulnerability (A03).

## Phase 6: Kafka Event Streaming
- [ ] Configure `kafkajs` client and producer.
- [ ] Refactor booking checkout API to publish booking events to Kafka.
- [ ] Implement `src/consumers/BookingConsumer.js` to process reservation events, run pricing math, update database tables, and clear Redis cache.

## Phase 7: Enterprise UI Implementation
- [ ] Build an interactive parking slot layout dashboard displaying vacancy updates, dynamic rate changes, and a spot search search panel.

## Phase 8: Verification
- [ ] Verify Elasticsearch Injection vulnerability (A03) works on the search API.
- [ ] Verify cost manipulation (A04) processes successfully through Kafka and produces incorrect billing states.
- [ ] Confirm absence of logs (A09) in the background listener.
- [ ] Run the complete integration tests using Docker Compose.

- [ ] Verify every standalone vulnerability has the required `// VULNERABILITY <OWASP_ID>: <brief description>` source annotation.
- [ ] Verify every chain component has the required `// CHAIN LINK <N> (chain-<ID>): <description>` source annotation.
- [ ] Verify `.vulns`, README chain table, and plan chain table agree on OWASP ID, severity, CWE, impact, location, and method.
- [ ] Verify nearby decoy safe patterns remain implemented and are listed in `.vulns.decoys`.
