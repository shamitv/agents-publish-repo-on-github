# Audit Report: app-29 — Vehicle Fleet Management

**Language:** Java (Spring Boot)  
**Business Domain:** Transportation / Fleet Management  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection (LDAP Injection)

**Severity:** Medium  
**Location:** `DriverService.java:19-25` — `lookupDriverByLicense()`  
**Lines:**
```java
// VULNERABILITY A03: LDAP query constructed via string concatenation with user-provided parameters
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A03`
- LDAP filter built via string concatenation
- Allows LDAP injection attacks

### VULN-02: A06 — Vulnerable Components (Log4j 2.14.1)

**Severity:** Critical  
**Location:** `pom.xml:33-46` — `dependencies`  
**Lines:**
```xml
<!-- VULNERABILITY A06: Log4j pinned to vulnerable version 2.14.1 (CVE-2021-44228) -->
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A06`
- Log4j 2.14.1 for remote code execution via JNDI injection
- Query inputs logged verbatim

### VULN-03: A10 — Server-Side Request Forgery

**Severity:** Medium  
**Location:** `IntegrationController.java:16-21` — `fetchExternalVehicleData()`  
**Lines:**
```java
// VULNERABILITY A10: SSRF in external vehicle endpoint allows fetching arbitrary server-side resources
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A10`
- No URL validation on user-supplied fetch URLs
- Can probe internal services and cloud metadata

---

## Chained Attack: chain-01

**Chain Name:** Log4Shell → SSRF → Lateral Movement  
**Combined Impact:** Lateral Movement  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Log4Shell via Search (A06 — Medium)

**Difficulty: MEDIUM**

- Query inputs logged via Log4j 2.14.1
- JNDI expression triggers RCE

### Link 2: SSRF to Cloud Metadata (A10 — Medium)

**Difficulty: EASY**

- Unvalidated URL fetch endpoint
- Can query `169.254.169.254` for cloud IAM credentials

---

## Summary

App-29 is a Spring Boot fleet management system with LDAP injection, Log4j 2.14.1, and SSRF. Chain: Log4Shell RCE → SSRF to cloud metadata → credential theft.

**Overall Difficulty Score:** 2/5 (Easy-Medium)