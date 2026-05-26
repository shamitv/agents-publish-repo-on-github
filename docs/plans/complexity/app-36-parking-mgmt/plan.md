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

## 4. Impact on Planted Vulnerabilities
- **VULN-01 (A03 - SQL Injection)**: The spot search function `/api/spots/search` is migrated from SQL to Elasticsearch. The search string is concatenated directly into an **Elasticsearch Query DSL** query string parameter. This exposes the application to **Elasticsearch Injection**, allowing queries to bypass lot visibility filters or extract hidden records.
- **VULN-02 (A04 - Insecure Design)**: The cost manipulation flaw allows a user to request bookings by setting pricing variables to zero or negative values. The API will accept this payload and dispatch it via Kafka. The `BookingConsumer` reads the pricing variables from the event payload and writes them directly to PostgreSQL, creating free parking slots.
- **VULN-03 (A09 - Security Logging & Monitoring Failures)**: Reservations are processed and payments are handled inside the async `BookingConsumer` Kafka worker. The absence of audit logs for booking modifications and reversals remains inside this consumer listener class.
- **Chain-01 (SQLi → Cost Manipulation)**: Attacker exploits Elasticsearch injection on spot search to extract zone mappings, then logs in to execute free bookings using the cost manipulation endpoint.
- **Chain-02 (State Confusion Pivot to Injection)**: Attacker leverages race conditions between payment logs and booking confirmations in Kafka to bypass billing controls or inject queries.
