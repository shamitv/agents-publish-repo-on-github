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

## 4. Vulnerabilities & Exploit Chains Detail

### Standalone Vulnerabilities
- **VULN-01 (A01 - IDOR on Order Details)**:
  - *Location*: `src/controllers/orderController.py` → `get_order_details()`
  - *Description*: The order retrieval API queries orders in PostgreSQL using user-supplied parameters. It lacks verification logic checking if the authenticated user's ID matches the order's buyer ID.
  - *Decoy Safeguard*: The user profile endpoint `/api/user/profile` strictly verifies session IDs and ownership flags, creating a false sense of security.
- **VULN-02 (A03 - Elasticsearch Query DSL Injection)**:
  - *Location*: `src/controllers/productController.py` → `search_products()`
  - *Description*: User-supplied search queries are concatenated directly into the Elasticsearch search payload query string (e.g. `_search?q=`). An attacker can inject Elasticsearch syntax to query hidden indices or bypass access filters.
  - *Decoy Safeguard*: The database login authentication query utilizes a fully parameterized query format.
- **VULN-03 (A09 - Missing Audit Logs in Event Consumer)**:
  - *Location*: `src/consumers/billing_consumer.py`
  - *Description*: Order checkouts and invoice generation trigger state changes in PostgreSQL, but the background consumer performs these operations without writing structured logs.

### Exploit Chains
- **Chain-01 (EASY to Find & Exploit)**: *User Enumeration → Session Forgery → Catalog Modification*
  - *Narrative*: An attacker uses the unauthenticated user check API (`/api/users/exists`) to confirm the admin username. They then read the hardcoded secret key from `config/config.py` and use it to forge a signed admin session cookie. With the admin session, the attacker posts a new product directly to MongoDB, which syncs to Elasticsearch.
  - *Subtlety*: Low. The hardcoded key is highly conspicuous and easily flagged by standard static analysis tools.
- **Chain-02 (HARD to Find & Exploit)**: *Elasticsearch Injection → Async State Confusion → IDOR Pivot*
  - *Narrative*: The attacker triggers an order placement via Kafka. They simultaneously perform an Elasticsearch Query DSL Injection on the catalog search endpoint to trigger an expensive nested search script, introducing a delay in the web worker. By exploiting this processing lag, the attacker sends a rapid sequence of order mutation events. The asynchronous database status writer in Kafka, confused by out-of-order state timestamps, updates the order status map incorrectly, allowing the attacker to access another user's invoice details using the IDOR flaw.
  - *Subtlety*: High. It requires exploiting distributed processing delays between Elasticsearch query threads, Kafka message consumers, and PostgreSQL state mapping.
