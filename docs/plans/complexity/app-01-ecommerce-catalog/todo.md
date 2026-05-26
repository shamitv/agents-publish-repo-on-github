# Todo List: app-01-ecommerce-catalog Complexity Upgrade

This checklist tracks the tasks required to implement the enterprise full-stack architecture for the E-Commerce Product Catalog API.

## Phase 1: Scaffold & Dependencies
- [ ] Add dependency packages to `requirements.txt`:
  - `psycopg2-binary` (PostgreSQL client)
  - `pymongo` (MongoDB client)
  - `elasticsearch` (Elasticsearch client)
  - `kafka-python` (Kafka AMQP/event client)
- [ ] Initialize modular directories under `src/`: `config/`, `models/`, `services/`, `controllers/`, `routes/`, `consumers/`.

## Phase 2: Docker Compose Orchestration
- [ ] Create `docker-compose.yml` specifying:
  - `web` (LMS server + consumer thread workers)
  - `db` (PostgreSQL 15)
  - `mongodb` (MongoDB 6)
  - `elasticsearch` (Elasticsearch 8)
  - `zookeeper` (ZooKeeper helper)
  - `kafka` (Kafka broker)
- [ ] Configure wait scripts to ensure database, elastic, and broker ports are fully open.

## Phase 3: Polyglot Database Migration
- [ ] Implement database client connections in `src/config/`:
  - `db_postgres.py` for PostgreSQL connections.
  - `db_mongo.py` for MongoDB connections.
- [ ] Migrate order schemas to PostgreSQL.
- [ ] Migrate product specifications catalog to MongoDB.

## Phase 4: Elasticsearch Indexing
- [ ] Implement product sync listener to populate Elasticsearch documents.
- [ ] Implement product search controller in `src/controllers/productController.py` utilizing the Elasticsearch client.
- [ ] Keep search string concatenation in the Elasticsearch Query DSL string to maintain the injection vulnerability (A03).

## Phase 5: Kafka Event Streaming
- [ ] Configure Kafka Producer for ordering events in `src/config/kafka_client.py`.
- [ ] Refactor order checkout to publish to the `orders` topic.
- [ ] Implement `src/consumers/inventory_consumer.py` to process inventory updates.
- [ ] Implement `src/consumers/billing_consumer.py` to generate invoices.

## Phase 6: Enterprise UI Implementation
- [ ] Build a multi-view HTML dashboard in `src/public/` displaying product search, faceted filters, order tracking, and live processing statistics.

## Phase 7: Verification
- [ ] Verify Elasticsearch Injection vulnerability (A03) successfully extracts documents or alters search scope.
- [ ] Verify IDOR vulnerability (A01) bypasses session checks in the modularized order controller.
- [ ] Confirm absence of logs (A09) in Kafka consumer files.
