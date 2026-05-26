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

## 4. Impact on Planted Vulnerabilities
- **VULN-01 (A03 - SQL Injection)**: The rate plan catalog search is rewritten using a raw JDBC SQL command. The user input is directly concatenated, exposing PostgreSQL-specific SQLi vulnerabilities. Caching will be configured to bypass searches.
- **VULN-02 (A04 - Insecure Design)**: The tariff rates are updated via `/api/plans/update`. The controller accepts the cost parameters without negative validation. These parameters are read by the `TariffCalculator` service which computes invoice totals in the async `CdrConsumer`. The billing engine generates zero-fee invoices based on these calculations.
- **VULN-03 (A09 - Security Logging & Monitoring Failures)**: Invoices are processed and payment states modified inside the `CdrConsumer` Kafka thread. The lack of structured audit logging for billing adjustments and payment reversals persists inside the background listener class.
- **Chain-01 (SQLi → Cost Manipulation)**: Attacker exploits SQLi on plan search to extract customer database tables, then logs in to apply zero-fee rate plans.
- **Chain-02 (State Confusion Pivot to Injection)**: Attacker exploits race conditions between call-end events and billing calculations inside Kafka consumer loops to inject commands or alter calculations.
