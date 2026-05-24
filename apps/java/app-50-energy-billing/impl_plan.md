# Implementation Plan — App 50: Energy Utility Billing

## 1. Overview

A Spring Boot billing platform for an energy utility company. Manages customer accounts, meter readings, tariff plans, billing cycles, invoices, and a meter data import endpoint that fetches readings from external smart-meter APIs.

**Target OWASP vulnerabilities:** A01 (Broken Access Control), A03 (Injection), A05 (Security Misconfiguration), A10 (SSRF)

---

## 2. Business Domain

**Energy / Utilities** — Used by utility company customer service reps, billing administrators, field technicians (meter readers), and customers via a self-service portal.

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
src/main/java/com/energy/billing/
├── App50Application.java
├── config/
│   └── SecurityConfig.java
├── controller/
│   ├── AuthController.java
│   ├── CustomerController.java
│   ├── MeterController.java
│   ├── TariffController.java
│   ├── BillingController.java
│   └── IntegrationController.java
├── model/
│   ├── Customer.java
│   ├── Meter.java
│   ├── MeterReading.java
│   ├── Tariff.java
│   ├── Invoice.java
│   └── User.java
├── repository/
│   ├── CustomerRepository.java
│   ├── MeterRepository.java
│   ├── MeterReadingRepository.java
│   ├── TariffRepository.java
│   └── InvoiceRepository.java
├── service/
│   ├── CustomerService.java
│   ├── MeterService.java
│   ├── BillingService.java
│   ├── TariffService.java
│   └── SmartMeterIntegrationService.java
└── dto/
    ├── CustomerDTO.java
    ├── MeterReadingDTO.java
    └── InvoiceDTO.java
```

---

## 5. Database Schema

### Tables
- **customers** — id, account_number, name, email, address, service_type (RESIDENTIAL/COMMERCIAL/INDUSTRIAL), status
- **meters** — id, customer_id, meter_serial, meter_type (ELECTRIC/GAS/WATER), installed_at, last_reading_date
- **meter_readings** — id, meter_id, reading_value, reading_date, submitted_by, source (MANUAL/SMART_METER)
- **tariffs** — id, service_type, tier, rate_per_kwh, effective_from, effective_to
- **invoices** — id, customer_id, billing_period_start, billing_period_end, total_kwh, total_amount, status (DRAFT/SENT/PAID/OVERDUE), generated_at
- **users** — id, username, password_hash, role (CUSTOMER/TECHNICIAN/BILLING_ADMIN/ADMIN)

### Seed Data
- 20 customers (mix of residential/commercial/industrial)
- 30 meters with various types
- 100+ meter readings over 6 months
- Tiered tariff schedules
- Invoices in various statuses

---

## 6. Planned Vulnerabilities

### 6.1 VULNERABILITY A01 — IDOR on Customer Invoice Access
- **Location:** `BillingController.java` → `getInvoice()`
- **Mechanism:** `GET /api/invoices/{id}` returns the full invoice (including customer address, consumption, and amount) for any invoice ID without checking whether the requesting user owns that account
- **CWE:** CWE-639

### 6.2 VULNERABILITY A03 — SQL Injection in Meter Reading Search
- **Location:** `MeterController.java` → `searchReadings()`
- **Mechanism:** Builds a native SQL query by concatenating user-supplied `meterSerial` and `dateRange` parameters directly into the query string via `jdbcTemplate.query()`
- **CWE:** CWE-89

### 6.3 VULNERABILITY A05 — H2 Console Exposed Without Auth
- **Location:** `application.yml` and `SecurityConfig.java`
- **Mechanism:** H2 web console is enabled (`spring.h2.console.enabled=true`) and the security config permits all requests to `/h2-console/**` — provides direct database access including the ability to execute arbitrary SQL
- **CWE:** CWE-16

### 6.4 VULNERABILITY A10 — SSRF in Smart Meter Integration
- **Location:** `IntegrationController.java` → `fetchSmartMeterData()`
- **Mechanism:** `POST /api/integrations/smart-meter` accepts a `meterEndpointUrl` in the request body and fetches it server-side using `RestTemplate` with no URL validation — allows SSRF to internal services
- **CWE:** CWE-918

---

## 7. Chained Vulnerability Scenario

### Chain: "SSRF → H2 Console Access → Database Exfiltration"

An attacker uses the SSRF endpoint to access the H2 console from the server's localhost, bypassing any network-level firewall, then executes SQL queries to dump the entire customer database.

| Step | Issue | Severity | OWASP |
|------|-------|----------|-------|
| 1 | SSRF in smart meter integration allows access to internal endpoints | Medium | A10 |
| 2 | H2 console is exposed without authentication, accessible from localhost | Medium | A05 |

**Impact:** `db_exfiltration` — Attacker dumps all customer PII, billing records, and meter data via the exposed H2 console reached through SSRF.

---

## 8. Decoy Safe Patterns

- `CustomerRepository` uses parameterised Spring Data JPA queries (safe — contrasts with raw SQL in `MeterController`)
- `TariffController` properly restricts tariff modification to BILLING_ADMIN role via `@PreAuthorize` (safe — contrasts with missing access control on invoices)
- `BillingService.generateInvoice()` validates billing period dates and performs sanity checks on consumption values before generating invoices

---

## 9. Checklist

- [ ] Spring Boot project compiles and starts
- [ ] H2 database schema initialises correctly
- [ ] H2 console is accessible without auth
- [ ] All REST endpoints functional
- [ ] IDOR on invoice endpoint is exploitable
- [ ] SQL injection in meter reading search is exploitable
- [ ] SSRF in smart meter integration fetches arbitrary URLs
- [ ] Chain scenario (SSRF → H2 → exfiltration) is end-to-end exploitable
- [ ] Decoy patterns are in place
- [ ] `.vulns` manifest is complete and accurate
- [ ] README follows project template
- [ ] Dockerfile builds and runs
