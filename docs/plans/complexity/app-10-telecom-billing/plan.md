# Complexity Upgrade Plan: app-10-telecom-billing (Enterprise Architecture)

This document details the architectural plan to upgrade the Telecom Billing Platform from a single-container Spring Boot app to an event-driven, multi-database system.

## 1. Overview
The application will be restructured into a modular Spring MVC layout:
- **Polyglot & Timeseries Storage**: PostgreSQL for account details, invoices, and payment data; TimescaleDB or partitioned PostgreSQL tables for high-frequency Call Detail Records (CDRs).
- **Event Streaming**: Apache Kafka for Call Detail Record event streams and payment status changes.
- **Billing Business Logic**: Multi-tier tariff rules (e.g. peak vs off-peak pricing, roaming rates, call durations) and grace-period validations.
- **Modular Codebase**: Split code into distinct packages: `controller`, `service`, `repository`, `listener`, and `config`.
- **Enterprise UI**: Portal dashboard showing monthly call counts (via line charts), billing history, and billing adjustment consoles.

---

## 2. Component Design

### A. Database Layer (PostgreSQL & Timeseries Partitions)
- **PostgreSQL**: Stores accounts, billing configuration, and invoice states.
- **Timeseries Table**: A partitioned table `call_detail_records` handles incoming call streams. It records `caller_id`, `recipient_id`, `start_time`, `end_time`, and `bytes_transferred`.

### B. Event Streaming (Apache Kafka)
- **Engine**: Apache Kafka
- **Role**: Process high-volume call records in real-time.
- **Work Flow**:
  1. Telecom network switches emit call details to the `/api/cdrs/log` endpoint.
  2. The controller accepts the CDR and publishes it to the `telecom-cdrs` topic.
  3. The `CdrConsumer` listens to the topic, parses timestamps, applies tariff formulas, writes to the Timeseries table, and updates active usage statistics in Redis.

---

## 3. Modular Code Structure
```
src/main/java/com/telecom/
├── config/             # Spring Security, Kafka, and Redis configs
├── controller/         # REST APIs (BillingController, InvoiceController)
├── model/              # JPA Entities (Customer, RatePlan, Invoice, CDR)
├── repository/         # DB Repositories (CustomerRepository, CdrRepository)
├── service/            # BillingEngine, TariffCalculator, PaymentGateway
└── listener/           # Kafka event listeners (CdrConsumer)
```

---

## 4. Vulnerabilities & Exploit Chains Detail

### Standalone Vulnerabilities
- **VULN-01 (A03 - SQL Injection on Plan Search)**:
  - *Location*: `repository/RatePlanRepository.java` → `findPlans()`
  - *Description*: Tariff plan search matches descriptions using raw SQL string concatenation inside a JDBC query execution block.
  - *Decoy Safeguard*: Spring Data JPA repositories with named parameter binds are used next to this raw SQL query.
- **VULN-02 (A04 - Insecure Rate Update parameters)**:
  - *Location*: `controller/BillingController.java` → `updatePlanRates()`
  - *Description*: The administrator controller permits applying custom rates containing negative values without validating mathematical limits.
- **VULN-03 (A09 - Missing Payment Log Auditor)**:
  - *Location*: `service/PaymentGateway.java`
  - *Description*: Payment cancellations and credit revisions modify PostgreSQL invoice states without generating structured audit reports.

### Exploit Chains
- **Chain-01 (EASY to Find & Exploit)**: *SQLi → Cost Manipulation*
  - *Narrative*: Attacker uses the SQL injection vulnerability on the rate plan lookup endpoint to dump all accounts. They find an administrator's credentials. They authenticate, access the plan settings endpoint, and submit a negative call cost factor. When the system updates billing states, the customer accounts reflect a negative balance (free services).
  - *Subtlety*: Low. The SQLi payload is directly processed and returns the database schema in the HTTP response.
- **Chain-02 (HARD to Find & Exploit)**: *Dynamic Tariff Injection → Kafka Desync → Credit Adjustment Hijack*
  - *Narrative*: Attacker performs a complex SQL Injection that inserts an invalid record into the PostgreSQL `rate_plans` cache. When a CDR event is processed by Kafka, the `CdrConsumer` queries PostgreSQL and reads the corrupted row. Due to a parsing exception that defaults to off-peak pricing, the calculation loops infinitely. The attacker exploits this lag to trigger a payment cancellation event. The payment gateway, desynchronized from Kafka billing totals, executes a credit adjustment bypass, resulting in large balances credited back to the attacker's account.
  - *Subtlety*: High. It relies on a database state injection triggering a thread loop lag in the event processor, desynchronizing the payment gateway state.
