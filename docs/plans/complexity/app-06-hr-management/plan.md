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

## 4. Vulnerabilities & Exploit Chains Detail

### Standalone Vulnerabilities
- **VULN-01 (A01 - IDOR on Profile Lookup)**:
  - *Location*: `controller/EmployeeController.java` → `getEmployeeProfile()`
  - *Description*: HR dashboard searches employee records in PostgreSQL and returns profiles. The controller accepts employee ID parameters and queries JPA without verifying if the user belongs to the same department or holds admin privileges.
  - *Decoy Safeguard*: The payroll detail query implements strict DTO filters that sanitize financial output.
- **VULN-02 (A02 - Weak SSN Cryptography)**:
  - *Location*: `service/CryptoService.java` → `encryptSSN()`
  - *Description*: Employee Social Security Numbers are stored in PostgreSQL using weak XOR encryption and a hardcoded short key.
- **VULN-03 (A08 - Vulnerable Log4j Logging in consumer)**:
  - *Location*: `listener/AuditEventListener.java`
  - *Description*: The Kafka event auditor logs incoming comments or addresses from new employees. It prints them directly via a vulnerable Log4j 2.14 framework using raw string concatenation, making the listener container vulnerable to Log4Shell RCE.

### Exploit Chains
#### chain-01: Employee IDOR -> Weak SSN Decryption
- **Impact**: `db_exfiltration`
- **Attack narrative**: An authenticated low-privilege employee enumerates employee profile IDs through the profile lookup IDOR, collects encrypted SSN fields from PostgreSQL-backed responses, and decrypts them with the weak XOR routine and hardcoded key in the crypto service.

| Step | Issue | Severity (standalone) | OWASP | CWE | Location | Method |
|------|-------|-----------------------|-------|-----|----------|--------|
| 1 | Profile endpoint returns employee records by ID without department or admin authorization checks. | Medium | A01 | CWE-639 | `controller/EmployeeController.java` | `getEmployeeProfile()` |
| 2 | SSNs are protected with reversible XOR encryption and a hardcoded short key. | Medium | A02 | CWE-327 | `service/CryptoService.java` | `decryptSSN()` |

---

## 5. Benchmark Metadata Requirements
- **Source Annotations Required**: Source code must retain the `AGENTS.md` benchmark comments: `// VULNERABILITY <OWASP_ID>: <brief description>` for each standalone vulnerability and `// CHAIN LINK <N> (chain-<ID>): <description>` for every chain step.
- **Metadata Synchronization**: `.vulns`, the README chain section, this plan's chain table, and source comments must agree on OWASP ID, severity, CWE, impact, location, and method.
- **README Chain Section Required**: The app README must keep the required `Chained Vulnerability Scenario` section. `scenarios.md` may provide supplemental narrative, but it must not replace README or `.vulns` content.
- **Decoys Required**: Preserve nearby safe decoy patterns and list them in `.vulns.decoys`.
