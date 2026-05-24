# Audit Report: app-08 — Warehouse Management System

**Language:** Java (Spring Boot)  
**Business Domain:** Warehousing / Logistics  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A05 — Security Misconfiguration (Actuator Exposure)

**Severity:** High  
**Location:** `application.properties:15-25`  
**Description:** Spring Boot Actuator endpoints (`env`, `heapdump`, `beans`, `mappings`) exposed publicly without authentication.

**Difficulty: EASY**

- `management.endpoints.web.exposure.include=*` enables all actuator endpoints
- No security constraint applied to actuator paths
- `/actuator/env` leaks environment variables (potentially including secrets)
- `/actuator/heapdump` can be downloaded and analyzed offline

### VULN-02: A03 — LDAP Injection

**Severity:** High  
**Location:** `EmployeeLdapService.java:15-22` — `searchEmployees()`  
**Description:** LDAP filter constructed via string concatenation with user-supplied search term.

**Difficulty: MEDIUM**

- LDAP injection less commonly exploited than SQLi
- Can enumerate directory entries, bypass auth, extract attributes
- Default error messages may reveal directory structure

### VULN-03: A10 — Server-Side Request Forgery (SSRF)

**Severity:** Critical  
**Location:** `ShippingService.java:12-35` — `generateLabel()`  
**Description:** Shipping label URL fetched server-side with no scheme, host, or port validation.

**Difficulty: EASY**

- Fetch arbitrary URLs from the server
- Can access cloud metadata endpoints (169.254.169.254)
- Can probe internal services, read local files via `file:///`

---

## Chained Attack: chain-01

**Chain Name:** LDAP Injection → Directory Disclosure → Inventory Tampering  
**Combined Impact:** Data Modification (Stock Manipulation)  
**Overall Chain Difficulty: MEDIUM-HARD**

### Link 1: LDAP Injection (A03 — Medium)

**Location:** `EmployeeLdapService.java` — `searchEmployees()`  
**Description:** LDAP filter built via string concatenation — enables enumeration of directory entries.

### Link 2: Verbose Error Messages (A05 — Low)

**Location:** `EmployeeController.java` — `search()`  
**Description:** LDAP exceptions containing internal DN paths returned verbatim in HTTP 500 error body.

### Link 3: Unprotected Inventory Adjustment (A01 — High)

**Location:** `InventoryController.java` — `adjustQuantity()`  
**Description:** POST endpoint requires only authentication, no role check — any worker account can modify stock.

---

## Summary

App-08 stands out for its SSRF vulnerability (unique among the apps so far) and LDAP injection (a less common injection type). The actuator exposure is a low-effort high-reward finding. Chain requires understanding LDAP directory structures, making it harder than average.

**Overall Difficulty Score:** 3/5 (Medium-Hard — LDAP injection and SSRF require specialized knowledge)