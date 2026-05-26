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
#### chain-01: Weak Billing Admin Check -> Negative Rate Update -> Unlogged Credit Change
- **Impact**: `data_modification`
- **Attack narrative**: A customer reaches the billing plan update workflow through a weak billing-admin authorization check, submits a negative or zero-valued custom rate because the controller does not validate tariff bounds, and the payment adjustment flow applies the modified billing state without emitting audit logs that would reveal the unauthorized data change.

| Step | Issue | Severity (standalone) | OWASP | CWE | Location | Method |
|------|-------|-----------------------|-------|-----|----------|--------|
| 1 | Billing administration check trusts a request-controlled role or account flag. | Medium | A01 | CWE-862 | `controller/BillingController.java` | `updatePlanRates()` |
| 2 | Rate update accepts negative or zero-valued tariff parameters without validation. | Medium | A04 | CWE-20 | `controller/BillingController.java` | `updatePlanRates()` |
| 3 | Payment and credit state changes are applied without structured audit logging. | Low | A09 | CWE-778 | `service/PaymentGateway.java` | `applyCreditAdjustment()` |

---

## 5. Benchmark Metadata Requirements
- **Source Annotations Required**: Source code must retain the `AGENTS.md` benchmark comments: `// VULNERABILITY <OWASP_ID>: <brief description>` for each standalone vulnerability and `// CHAIN LINK <N> (chain-<ID>): <description>` for every chain step.
- **Metadata Synchronization**: `.vulns`, the README chain section, this plan's chain table, and source comments must agree on OWASP ID, severity, CWE, impact, location, and method.
- **README Chain Section Required**: The app README must keep the required `Chained Vulnerability Scenario` section. `scenarios.md` may provide supplemental narrative, but it must not replace README or `.vulns` content.
- **Decoys Required**: Preserve nearby safe decoy patterns and list them in `.vulns.decoys`.
