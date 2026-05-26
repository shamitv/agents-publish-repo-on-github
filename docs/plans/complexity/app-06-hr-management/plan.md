# Complexity Upgrade Plan: app-06-hr-management (Enterprise Architecture)

This document details the architectural plan to upgrade the Enterprise HR Management System to a modular, multi-database Java application incorporating Elasticsearch and Apache Kafka.

## 1. Overview
The H2-backed Spring Boot system will be upgraded to a real enterprise-tier layout:
- **Relational Storage**: PostgreSQL for employee, user, and department records.
- **Search Service**: Elasticsearch for fuzzy search indexing on employee profiles and audit logs.
- **Message Broker**: Apache Kafka for asynchronous employee lifecycle events.
- **Onboarding Workflow**: Implement a state machine (Draft → Verified → Background Checked → Active).
- **Modular Codebase**: Split code into distinct packages: `controller`, `service`, `repository`, `dto`, `listener`, and `config`.
- **Enterprise UI**: An admin dashboard displaying onboarding pipelines, audit trails fetched from Elasticsearch, and employee search interfaces.

---

## 2. Component Design

### A. Database Layer (PostgreSQL)
- **Engine**: PostgreSQL 15 (Alpine)
- **Role**: Store ACID-compliant employee and onboarding tables.
- **Connection**: Managed via HikariCP connection pool with Spring Data JPA.

### B. Search Service (Elasticsearch)
- **Engine**: Elasticsearch 8 (Alpine)
- **Role**: Index employee data for fast search and aggregation, and index audit log entries.
- **Sync**: Spring Boot JPA `@PostPersist` and `@PostUpdate` lifecycle hooks publish updates to Elasticsearch.

### C. Message Broker (Apache Kafka)
- **Engine**: Apache Kafka + ZooKeeper
- **Role**: Distribute HR events asynchronously.
- **Work Flow**:
  1. HR admin triggers onboarding status changes.
  2. Spring Boot app publishes an event containing employee details to the `employee-lifecycle` topic.
  3. The `AuditEventListener` consumes the event, format-logs the payload via Logback/Log4j, and writes the index record to Elasticsearch.

---

## 3. Modular Code Structure
```
src/main/java/com/hr/
├── config/             # Spring Security, Kafka, and Elasticsearch configs
├── controller/         # REST APIs (EmployeeController, AuthController)
├── dto/                # Request and Response payloads
├── model/              # JPA Entities (Employee, User, OnboardingState)
├── repository/         # Spring Data JPA repositories
├── service/            # Workflow engine and audit log handlers
└── listener/           # Kafka @KafkaListener event consumers
```

---

## 4. Impact on Planted Vulnerabilities
- **VULN-01 (A01 - IDOR)**: The employee controller (`controller/EmployeeController.java`) exposes profile retrieval. The service layer reads from the PostgreSQL database or the Redis cache. Ownership validation check is omitted, allowing any authenticated user to fetch other employee records.
- **VULN-02 (A02 - Cryptographic Failures)**: SSNs are encrypted with a weak crypto utility before persistence. The encrypted strings will be saved in PostgreSQL and indexed in Elasticsearch in their weak form.
- **VULN-03 (A08 - Software and Data Integrity Failures / Log4j RCE)**: When the `AuditEventListener` consumes an onboarding event, it logs the user-supplied details (such as address or comments) using an unescaped format string in a vulnerable logger package (e.g. Log4j 2.14). This exposes the background Kafka worker thread to RCE via lookup strings (Log4Shell).
- **Chain-01 (Weak Crypto → IDOR → Employee Record Leak)**: Attacker decrypts IDs and extracts SSNs via the unauthenticated/unvalidated lookup endpoints.
- **Chain-02 (State Confusion Pivot to IDOR)**: State machine transitions for onboarding are updated asynchronously. Attacker exploits state conditions in the Kafka event loop to view records during transition states.
