# Audit Report: app-10 — Telecom Billing Platform

**Language:** Java (Spring Boot)  
**Business Domain:** Telecom / Billing  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection (SQL Injection)

**Severity:** High  
**Location:** `UsageController.java:20-31` — `getUsageByDateRange()`  
**Lines:**
```java
// VULNERABILITY A03: Usage search SQL query constructed using string concatenation with user-supplied date values
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A03`
- Date values concatenated directly into SQL
- Enables data exfiltration from other customers' invoices

### VULN-02: A04 — Insecure Design (No Rate Limiting)

**Severity:** Medium  
**Location:** `PaymentService.java:21-36` — `processPayment()`  
**Lines:**
```java
// VULNERABILITY A04: No rate limiting or idempotency check on payment processing
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A04`
- No idempotency key or rate limiting
- Allows replay attacks and payment fraud

### VULN-03: A09 — Logging Failures (No Audit Trail)

**Severity:** Low  
**Location:** `AdminController.java:21-32` — `adjustBalance()`  
**Lines:**
```java
// VULNERABILITY A09: Admin balance adjustment endpoint lacks audit logging
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A09`
- Balance modifications are not logged
- Undetectable database manipulation

---

## Chained Attack: chain-01

**Chain Name:** SQL Injection → Payment Fraud → No Audit Trail  
**Combined Impact:** Data Modification  
**Overall Chain Difficulty: MEDIUM**

### Link 1: SQLi Invoice Leak (A03 — Medium)

**Difficulty: EASY**

- SQLi in usage search leaks invoice and customer details

### Link 2: Payment Replay (A04 — Medium)

**Difficulty: EASY**

- Payment endpoint lacks idempotency controls
- Forged/replayed payment confirmations

### Link 3: Unlogged Admin Adjustments (A09 — Low)

**Difficulty: EASY**

- Balance adjustments leave no audit trail
- Fraudulent transactions undetectable

---

## Summary

App-10 is a Spring Boot telecom billing platform with SQLi, missing payment idempotency, and no audit logging on balance adjustments. Chain: SQLi leak invoices → replay payments → undetected fraud.

**Overall Difficulty Score:** 2/5 (Easy-Medium)