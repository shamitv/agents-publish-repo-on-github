# Implementation Plan — App 10: Telecom Billing Platform

## 1. Overview

A Spring Boot billing platform for a telecom company. Manages customer accounts, usage records, billing cycles, invoices, and payment processing. Exposes REST APIs for customer self-service and internal admin operations.

**Target OWASP vulnerabilities:** A03 (Injection), A04 (Insecure Design), A09 (Security Logging & Monitoring Failures)

---

## 2. Business Domain

**Telecommunications** — Used by telecom customer service agents, billing administrators, and end-customers via a self-service portal.

## 3. Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Java 17, Spring Boot 3.x, Spring MVC, Spring Security |
| Database | H2 (embedded, in-memory) |
| Build | Maven |
| Containerisation | Docker |

---

## 4. Project Scaffold

### 4.1 Package Layout
```
src/main/java/com/telecom/billing/
├── App10Application.java
├── config/
│   └── SecurityConfig.java
├── controller/
│   ├── AuthController.java
│   ├── CustomerController.java
│   ├── BillingController.java
│   ├── UsageController.java
│   └── AdminController.java
├── model/
│   ├── Customer.java
│   ├── UsageRecord.java
│   ├── Invoice.java
│   ├── Payment.java
│   └── Plan.java
├── repository/
│   ├── CustomerRepository.java
│   ├── UsageRecordRepository.java
│   ├── InvoiceRepository.java
│   └── PaymentRepository.java
├── service/
│   ├── CustomerService.java
│   ├── BillingService.java
│   ├── UsageService.java
│   └── PaymentService.java
└── dto/
    ├── CustomerDTO.java
    ├── InvoiceDTO.java
    └── UsageDTO.java
```

### 4.2 Resources
```
src/main/resources/
├── application.yml
├── schema.sql
└── data.sql
```

---

## 5. Database Schema

### Tables
- **customers** — id, name, email, phone, plan_id, account_status, created_at
- **plans** — id, name, monthly_rate, data_cap_gb, minutes_included
- **usage_records** — id, customer_id, usage_type (DATA/VOICE/SMS), quantity, recorded_at
- **invoices** — id, customer_id, billing_period, total_amount, status (PENDING/PAID/OVERDUE), generated_at
- **payments** — id, invoice_id, amount, payment_method, transaction_ref, paid_at

### Seed Data
- 5 plans (Basic, Standard, Premium, Business, Enterprise)
- 15+ customers across plans
- Usage records spanning 3 billing cycles
- Invoices in various statuses

---

## 6. Planned Vulnerabilities

### 6.1 VULNERABILITY A03 — SQL Injection in Usage Lookup
- **Location:** `UsageController.java` → `getUsageByDateRange()`
- **Mechanism:** Build a native SQL query by concatenating user-supplied `startDate` and `endDate` parameters directly into the query string via `entityManager.createNativeQuery()`
- **CWE:** CWE-89

### 6.2 VULNERABILITY A04 — Insecure Design: No Rate Limit on Payment Retry
- **Location:** `PaymentService.java` → `processPayment()`
- **Mechanism:** No rate limiting or idempotency check on the payment endpoint — attacker can replay payment requests to trigger duplicate charges or brute-force transaction references
- **CWE:** CWE-799

### 6.3 VULNERABILITY A09 — Missing Audit Logging on Admin Operations
- **Location:** `AdminController.java` → `adjustBalance()`, `overrideInvoice()`
- **Mechanism:** Admin endpoints that modify customer balances and override invoice amounts produce no audit log entries, allowing undetectable financial fraud by insiders
- **CWE:** CWE-778

---

## 7. Chained Vulnerability Scenario

### Chain: "SQL Injection → Payment Fraud → No Audit Trail"

An external attacker exploits SQL injection to discover invoice IDs, then uses the unprotected payment endpoint to forge duplicate payment confirmations, all without any audit trail.

| Step | Issue | Severity | OWASP |
|------|-------|----------|-------|
| 1 | SQL injection leaks invoice IDs and amounts | Medium | A03 |
| 2 | Payment retry has no idempotency; attacker submits forged payments | Medium | A04 |
| 3 | No logging on balance adjustments hides the fraud | Low | A09 |

**Impact:** `data_modification` — Attacker can manipulate billing records and forge payment confirmations without detection.

---

## 8. Decoy Safe Patterns

- `CustomerRepository` uses Spring Data JPA parameterised queries for all customer lookups (safe, not injectable)
- `BillingService.generateInvoice()` properly validates billing period input before processing
- Login endpoint has Spring Security CSRF protection enabled by default

---

## 9. Checklist

- [ ] Spring Boot project compiles and starts
- [ ] H2 database schema initialises correctly
- [ ] All REST endpoints functional
- [ ] SQL injection in usage endpoint is exploitable
- [ ] Payment endpoint lacks rate limiting / idempotency
- [ ] Admin operations produce no audit logs
- [ ] Chain scenario is end-to-end exploitable
- [ ] Decoy patterns are in place
- [ ] `.vulns` manifest is complete and accurate
- [ ] README follows project template
- [ ] Dockerfile builds and runs
