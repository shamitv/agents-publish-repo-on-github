# Audit Report: app-08 — Warehouse Management System

**Language:** Java (Spring Boot)  
**Business Domain:** Logistics / Warehouse  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A05 — Security Misconfiguration (Exposed Actuators)

**Severity:** High  
**Location:** `application.properties:15-25`  
**Lines:**
```properties
# VULNERABILITY A05: Spring Boot Actuator endpoints exposed publicly without authentication
management.endpoints.web.exposure.include=*
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A05`
- `/actuator/env`, `/actuator/heapdump`, etc. are unauthenticated
- Leaks environment variables, heap dumps, and configuration

### VULN-02: A03 — Injection (LDAP Injection)

**Severity:** High  
**Location:** `EmployeeLdapService.java:15-22` — `searchEmployees()`  
**Lines:**
```java
// VULNERABILITY A03: LDAP filter constructed via string concatenation with user-supplied search term
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A03`
- LDAP filter built via string concatenation
- Can enumerate all employees or extract hidden attributes

### VULN-03: A10 — SSRF (Shipping Label Fetch)

**Severity:** Critical  
**Location:** `ShippingService.java:12-35` — `generateLabel()`  
**Lines:**
```java
// VULNERABILITY A10: Shipping label URL fetched server-side via HttpURLConnection with no validation
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A10`
- Fetches user-supplied URL via `HttpURLConnection`
- No scheme, host, or port validation
- Can access cloud metadata, internal services, local files

---

## Chained Attack: chain-01

**Chain Name:** LDAP Injection → Directory Structure Disclosure → Inventory Tampering  
**Combined Impact:** Data Modification  
**Overall Chain Difficulty: MEDIUM**

### Link 1: LDAP Injection (A03 — Medium)

**Difficulty: EASY**

- Injected LDAP filter enumerates directory entries, account names

### Link 2: Verbose LDAP Error Messages (A05 — Low)

**Difficulty: EASY**

- LDAP exceptions return internal DN paths in HTTP 500 error body
- Reveals directory structure to attacker

### Link 3: Unprotected Inventory Adjustment (A01 — High)

**Difficulty: EASY**

- `POST /api/inventory/{id}/adjust` requires only authentication, no role check
- Any discovered worker account can zero out stock counts

---

## Summary

App-08 is a Spring Boot warehouse manager with exposed actuators, LDAP injection, and SSRF in shipping label generation. Chain: inject LDAP → discover credentials → tamper with inventory.

**Overall Difficulty Score:** 2/5 (Easy-Medium)