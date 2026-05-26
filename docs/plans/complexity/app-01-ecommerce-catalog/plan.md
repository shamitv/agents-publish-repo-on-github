# Complexity Upgrade Plan: app-01-ecommerce-catalog (Enterprise Architecture)

This document details the architectural plan to upgrade the E-Commerce Product Catalog API from a simple SQLite-backed app to a multi-container, modular enterprise system.

## 1. Overview
The application will be restructured into a modular enterprise framework:
- **Relational Storage**: PostgreSQL for users, accounts, and order records.
- **Document Storage**: MongoDB for product specifications and attributes.
- **Search Engine**: Elasticsearch/OpenSearch for search and faceted catalog queries.
- **Event Streaming**: Apache Kafka for asynchronous order event sourcing and inventory dispatch.
- **Modular Codebase**: Split the monolithic `app.py` into a MVC-like layout: `routes/`, `controllers/`, `services/`, `models/`, and `consumers/`.
- **Enterprise UI**: A multi-tab dashboard with live metrics, search query logs, and transaction status views.

---

## 2. Component Design

### A. Database Layer (Polyglot Persistence)
- **PostgreSQL**: Stores transaction-critical data (`users`, `orders`, `invoices`) ensuring ACID compliance.
- **MongoDB**: Stores catalog data (`products`) as documents to support highly dynamic product attributes (e.g. dimensions, color, technical specs).

### B. Search Service (Elasticsearch)
- **Engine**: Elasticsearch 8
- **Role**: Handles fuzzy searches, autocomplete, and aggregations for the product catalog.
- **Sync**: A background sync process updates Elasticsearch whenever products in MongoDB are updated.

### C. Event Pipeline (Apache Kafka)
- **Engine**: Apache Kafka + ZooKeeper
- **Role**: Handles asynchronous checkout workflows.
- **Work Flow**:
  1. API publishes an `order-submitted` event to the `orders` Kafka topic.
  2. The `InventoryConsumer` reads the event, validates stock in MongoDB, and deducts inventory.
  3. The `BillingConsumer` reads the event, creates a billing invoice in PostgreSQL, and publishes an `order-processed` event to the `billing` topic.

---

## 3. Modular Code Structure
```
src/
├── config/             # Database, Kafka, and Redis clients
├── models/             # ORM schemas (SQLAlchemy for Postgres, MongoEngine)
├── services/           # Business logic (OrderService, SearchService)
├── controllers/        # Request handling and validation
├── routes/             # API routing definitions
├── consumers/          # Kafka event listeners (Inventory, Billing)
├── public/             # Complex HTML/JS dashboard UI
└── app.py              # Application entrypoint
```

---

## 4. Impact on Planted Vulnerabilities
- **VULN-01 (A01 - IDOR)**: The order details query is migrated to PostgreSQL. The controller (`controllers/orderController.py`) retrieves order objects by ID. The session verification logic in the service layer is omitted, allowing any user to read order records by ID.
- **VULN-02 (A03 - Injection)**: The product search is migrated from SQL to Elasticsearch. The search string is concatenated directly into an **Elasticsearch Query DSL** request (e.g. using `_search?q=`). This exposes the application to **Elasticsearch Injection**, allowing attackers to retrieve hidden documents, cause Denial of Service, or bypass query filters.
- **VULN-03 (A09 - Logging Failure)**: Logging failures are now distributed. The Kafka consumers (`InventoryConsumer`, `BillingConsumer`) execute crucial state changes (stock reduction, invoice generation) without producing audit logs in the standard stdout stream.
- **Chain-01 (User Enumeration → Session Forge → Admin Takeover)**: User existence check is handled in `controllers/userController.py`. The Flask session cookie signing continues to use the hardcoded secret, allowing forged admin cookies to write products to MongoDB and index them in Elasticsearch.
- **Chain-02 (State Confusion Pivot to IDOR)**: Attacker leverages Kafka message queue delays or out-of-order execution states in order fulfillment topics to pivot and access unauthorized invoice records in PostgreSQL.
