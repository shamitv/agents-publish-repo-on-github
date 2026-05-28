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
#### chain-01: User Enumeration -> Session Forgery -> Catalog Modification
- **Impact**: `data_modification`
- **Attack narrative**: An attacker calls the unauthenticated user existence endpoint to confirm the admin account name, reads the hardcoded Flask signing secret from configuration source, forges an admin session cookie, and uses an admin product endpoint that trusts the session role to write attacker-controlled catalog data into MongoDB and the synchronized Elasticsearch index.

| Step | Issue | Severity (standalone) | OWASP | CWE | Location | Method |
|------|-------|-----------------------|-------|-----|----------|--------|
| 1 | User enumeration endpoint confirms privileged usernames without authentication. | Low | A01 | CWE-203 | `src/controllers/userController.py` | `user_exists()` |
| 2 | Hardcoded Flask signing secret allows forged admin session cookies. | Medium | A02 | CWE-798 | `src/config/config.py` | `SECRET_KEY` |
| 3 | Product mutation endpoint trusts the forged admin session and writes attacker-controlled catalog records. | Medium | A01 | CWE-862 | `src/controllers/productController.py` | `create_product()` |

---

## 5. Benchmark Metadata Requirements
- **Source Annotations Required**: Source code must retain the `AGENTS.md` benchmark comments: `// VULNERABILITY <OWASP_ID>: <brief description>` for each standalone vulnerability and `// CHAIN LINK <N> (chain-<ID>): <description>` for every chain step.
- **Metadata Synchronization**: `.vulns`, the README chain section, this plan's chain table, and source comments must agree on OWASP ID, severity, CWE, impact, location, and method.
- **README Chain Section Required**: The app README must keep the required `Chained Vulnerability Scenario` section. `scenarios.md` may provide supplemental narrative, but it must not replace README or `.vulns` content.
- **Decoys Required**: Preserve nearby safe decoy patterns and list them in `.vulns.decoys`.
