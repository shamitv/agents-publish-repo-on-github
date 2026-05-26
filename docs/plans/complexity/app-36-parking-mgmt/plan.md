# Complexity Upgrade Plan: app-36-parking-mgmt (Enterprise Architecture)

This document details the architectural plan to upgrade the Parking Management System to a multi-database, event-driven JavaScript application.

## 1. Overview
The monolithic JavaScript application will be restructured into a modular, clean-architecture framework:
- **Polyglot Storage**: PostgreSQL for users, reservation tickets, and invoices; MongoDB for dynamic parking lot layouts and localized rules.
- **Search Service**: Elasticsearch for fuzzy search indexing on parking spots and zone features.
- **Event Streaming**: Apache Kafka for processing booking transactions and pricing updates.
- **Complex Business Logic**: Dynamic pricing algorithms based on hourly occupancy density, peak hour windows, and user membership levels (Standard, Premium, VIP).
- **Modular Codebase**: Split code into distinct packages: `routes/`, `controllers/`, `services/`, `consumers/`, `config/`.
- **Enterprise UI**: An admin map panel displaying spot availability status, invoice transaction histories, and dynamic rate graphs.

---

## 2. Component Design

### A. Database Layer (PostgreSQL & MongoDB)
- **PostgreSQL**: Stores relational tables (`users`, `reservations`, `payments`).
- **MongoDB**: Stores parking lot document layouts (dimensions, zone rules, restriction exceptions, vehicle clearance heights).

### B. Search Service (Elasticsearch)
- **Engine**: Elasticsearch 8
- **Role**: Index parking spots and zone rules to support rapid query lookup and location filters.
- **Sync**: A sync task updates the Elasticsearch spot index whenever changes are made in PostgreSQL/MongoDB.

### C. Event Streaming (Apache Kafka)
- **Engine**: Apache Kafka
- **Role**: Orchestrate reservation ticket processing.
- **Work Flow**:
  1. A user triggers a reservation checkout at `/api/reservations`.
  2. The controller publishes a `reservation-requested` event to the `parking-bookings` topic.
  3. The `BookingConsumer` reads the event, invokes the `DynamicPricing` service to calculate the fee, inserts the reservation record in PostgreSQL, and invalidates vacancy states in Redis.

---

## 3. Modular Code Structure
```
src/
├── config/             # DB, Kafka, Redis, and Elasticsearch clients
├── controllers/        # Express controllers (ReservationController, SpotController)
├── routes/             # Route mapping definitions
├── services/           # DynamicPricing, ZoneValidator
├── consumers/          # Kafka event listeners (BookingConsumer)
├── public/             # Interactive lot layout map and admin billing portal
└── server.js           # Server configuration and app setup
```

---

## 4. Vulnerabilities & Exploit Chains Detail

### Standalone Vulnerabilities
- **VULN-01 (A03 - Elasticsearch Query DSL Injection)**:
  - *Location*: `src/controllers/spotController.js` → `search()`
  - *Description*: User query strings are concatenated directly into the Elasticsearch search payload. This allows attackers to manipulate JSON parameters and bypass lot filtering constraints.
  - *Decoy Safeguard*: User authentication utilizes parameterized PostgreSQL parameters.
- **VULN-02 (A04 - Insecure Rate Update parameters)**:
  - *Location*: `src/controllers/reservationController.js` → `book()`
  - *Description*: The checkout API accepts rate variables supplied by the user without validation, allowing rates to be set to zero.
- **VULN-03 (A09 - Unlogged Ticket Cancellations)**:
  - *Location*: `src/consumers/BookingConsumer.js`
  - *Description*: The consumer worker updates ticket cancel states in PostgreSQL without generating logs.

### Exploit Chains
- **Chain-01 (EASY to Find & Exploit)**: *Elasticsearch Query Modification → Booking Cost Hijack*
  - *Narrative*: Attacker uses Elasticsearch DSL injection on the search endpoint to locate reserved spots and customer identifiers. They then submit a checkout request with pricing variables set to zero, executing a free reservation.
  - *Subtlety*: Low. The pricing parameter vulnerability is directly accessible on the booking endpoint.
- **Chain-02 (HARD to Find & Exploit)**: *Elasticsearch Index Injection → Async Price Engine Crash → Free Allocation*
  - *Narrative*: Attacker injects custom filter scripts into the product index using the Elasticsearch injection flaw. When the background `BookingConsumer` consumes a booking event and runs the `DynamicPricing` service, the pricing engine queries Elasticsearch to pull rate cards. The injected script causes the `DynamicPricing` service to throw an uncaught exception. Because the worker's transaction handler fails open, it logs the exception, registers the reservation with zero cost in PostgreSQL, and invalidates the Redis availability cache, allocating the spot to the attacker for free.
  - *Subtlety*: High. It requires exploiting an injection flaw to break a dependent search service, causing the background pricing consumer to fail open during event processing.
