# Audit Report: app-27 — Hotel Reservation System

**Language:** Java (Spring Boot)  
**Business Domain:** Hospitality / Travel  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection (JPQL Injection)

**Severity:** High  
**Location:** `RoomController.java:20-29` — `searchRooms()`  
**Lines:**
```java
// VULNERABILITY A03: JPQL query constructed via string concatenation with user-supplied parameters
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A03`
- String concatenation builds JPQL query
- Injection attacks on user-supplied parameters

### VULN-02: A05 — Security Misconfiguration (Exposed Debug Endpoint)

**Severity:** Medium  
**Location:** `AdminController.java:14-25` — `getSystemInfo()`  
**Lines:**
```java
// VULNERABILITY A05: Exposed admin debug endpoint without authentication leaks system variables
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A05`
- Unauthenticated debug endpoint
- Leaks system variables and default credentials

### VULN-03: A07 — Authentication Failures (Session Fixation)

**Severity:** Medium  
**Location:** `SecurityConfig.java:31-35` — `filterChain()`  
**Lines:**
```java
// VULNERABILITY A07: Session fixation protection disabled via sessionFixation().none()
```

**Difficulty: MEDIUM**

- Comment explicitly marks it as `VULNERABILITY A07`
- `sessionFixation().none()` prevents session rotation
- Allows session fixation attacks after account takeover

---

## Chained Attack: chain-01

**Chain Name:** Debug Info Leak → Session Fixation → Account Takeover  
**Combined Impact:** Account Takeover  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Debug Info Leak (A05 — Medium)

**Difficulty: EASY**

- Unauthenticated debug endpoint exposes default admin credentials
- Environment info leak

### Link 2: Session Fixation (A07 — Medium)

**Difficulty: MEDIUM**

- No session rotation on login
- Attacker can fix session before admin logs in

---

## Summary

App-27 is a Spring Boot hotel reservation system with JPQL injection, unauthenticated debug endpoint exposing credentials, and disabled session fixation. Chain: leak credentials → session fixation → admin account takeover.

**Overall Difficulty Score:** 2/5 (Easy-Medium)