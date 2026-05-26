# Audit Report: app-50 — Energy Utility Billing

**Language:** Java (Spring Boot)  
**Business Domain:** Energy / Utilities  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control (IDOR on Invoice)

**Severity:** Medium  
**Location:** `BillingController.java:21-27` — `getInvoice()`  
**Lines:**
```java
// VULNERABILITY A01: IDOR on invoice retrieval allows customers to read other customers' invoices
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A01`
- No ownership validation on invoice retrieval
- Any customer can view any invoice

### VULN-02: A03 — Injection (SQL Injection)

**Severity:** High  
**Location:** `MeterController.java:20-33` — `searchReadings()`  
**Lines:**
```java
// VULNERABILITY A03: Meter reading native query constructed via string concatenation with user parameters
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A03`
- String concatenation in native SQL query
- Full SQL injection capable of data exfiltration

### VULN-03: A05 — Security Misconfiguration (H2 Console)

**Severity:** Medium  
**Location:** `SecurityConfig.java:31-36` — `filterChain()`  
**Lines:**
```java
// VULNERABILITY A05: H2 web console enabled and permitted without authentication
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A05`
- H2 database console exposed without auth
- Direct database access via browser

### VULN-04: A10 — Server-Side Request Forgery

**Severity:** Medium  
**Location:** `IntegrationController.java:17-22` — `fetchSmartMeterData()`  
**Lines:**
```java
// VULNERABILITY A10: Smart meter endpoint fetches user-supplied URLs without validation
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A10`
- No URL validation on fetch endpoint
- Enables SSRF to internal services

---

## Chained Attack: chain-01

**Chain Name:** SSRF → H2 Console Access → Database Exfiltration  
**Combined Impact:** Database Exfiltration  
**Overall Chain Difficulty: HARD**

### Link 1: SSRF to Localhost (A10 — Medium)

**Difficulty: EASY**

- User-supplied URL fetched without validation
- Can target `http://localhost:8080/h2-console`

### Link 2: Unauthenticated H2 Console (A05 — Medium)

**Difficulty: MEDIUM**

- H2 console exposed without authentication
- SSRF POST can execute arbitrary SQL via JDBC connection

---

## Summary

App-50 is a Spring Boot energy billing system with IDOR on invoices, SQL injection in meter readings, unauthenticated H2 console, and SSRF. Chain: SSRF → H2 console → full database exfiltration.

**Overall Difficulty Score:** 3/5 (Hard)