# Audit Report: app-07 — Airline Booking System

**Language:** Java (Spring Boot)  
**Business Domain:** Travel / Aviation  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection (SQL Injection)

**Severity:** Critical  
**Location:** `FlightSearchDao.java:15-22` — `searchFlights()`  
**Lines:**
```java
// VULNERABILITY A03: Flight search SQL query built via string concatenation with user-supplied origin, destination, and date values
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A03`
- String concatenation with user-supplied origin/destination/date
- Full SQL injection capable of dumping all records

### VULN-02: A07 — Authentication Failures (Session Fixation)

**Severity:** High  
**Location:** `SecurityConfig.java:28-30` — `filterChain()`  
**Lines:**
```java
// VULNERABILITY A07: Session fixation protection disabled via sessionFixation().none()
```

**Difficulty: MEDIUM**

- Comment explicitly marks it as `VULNERABILITY A07`
- `sessionFixation().none()` prevents session rotation on login
- Allows session fixation attacks

### VULN-03: A04 — Insecure Design (No Rate Limiting)

**Severity:** High  
**Location:** `BookingService.java:20-42` — `createBooking()`  
**Lines:**
```java
// VULNERABILITY A04: No rate limiting, no payment timeout, no concurrency control on booking creation
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A04`
- No rate limiting or concurrency controls
- Enables inventory hoarding

---

## Chained Attack: chain-01

**Chain Name:** Sequential PNR Enumeration → Booking IDOR → Stored XSS on Staff View  
**Combined Impact:** Account Takeover  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Predictable PNR Generation (A04 — Low)

**Difficulty: EASY**

- PNRs generated as incrementing integers
- All booking references are predictable

### Link 2: IDOR on Boarding Summary (A01 — Medium)

**Difficulty: EASY**

- `GET /api/bookings/{pnr}/boarding-summary` returns full booking details without ownership check
- Enumerated PNRs expose other passengers' data

### Link 3: Stored XSS via Passenger Name (A03 — Medium)

**Difficulty: EASY**

- Passenger name concatenated into raw HTML without encoding
- Executes as XSS when rendered via `innerHTML` on staff UI
- Steals staff session cookies

---

## Summary

App-07 is a Spring Boot airline booking system with SQLi in flight search, disabled session fixation, and no rate limiting. Chain: enumerate PNRs → exploit IDOR → stored XSS steals staff sessions.

**Overall Difficulty Score:** 2/5 (Easy-Medium)