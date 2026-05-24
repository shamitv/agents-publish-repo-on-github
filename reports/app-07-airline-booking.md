# Audit Report: app-07 — Airline Booking System

**Language:** Java (Spring Boot)  
**Business Domain:** Airline / Travel Booking  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A03 — SQL Injection

**Severity:** Critical  
**Location:** `FlightSearchDao.java:15-22` — `searchFlights()`  
**Description:** Flight search SQL query built via string concatenation with user-supplied origin, destination, and date values.

**Difficulty: EASY**

- Direct string concatenation of user input into SQL query
- Classic SQLi pattern: `"SELECT * FROM flights WHERE origin='" + origin + "'"`
- Error-based or UNION-based exploitation possible

### VULN-02: A07 — Session Fixation

**Severity:** High  
**Location:** `SecurityConfig.java:28-30` — `filterChain()`  
**Description:** Session fixation protection disabled via `sessionFixation().none()` — session ID not rotated on login.

**Difficulty: MEDIUM**

- Attacker must first obtain/forge a session ID, then trick victim into logging in with it
- After login, session ID remains the same — attacker can hijack the authenticated session
- Requires social engineering or another vector to plant the session ID

### VULN-03: A04 — Insecure Design (No Rate Limiting)

**Severity:** High  
**Location:** `BookingService.java:20-42` — `createBooking()`  
**Description:** No rate limiting, payment timeout, or concurrency control on booking creation — allows inventory hoarding.

**Difficulty: EASY**

- Bot can hold seats indefinitely without completing payment
- Lacks any timeout mechanism to release held inventory
- Can block legitimate customers from booking

---

## Chained Attack: chain-01

**Chain Name:** Sequential PNR Enumeration → Booking IDOR → Stored XSS on Staff View  
**Combined Impact:** Account Takeover (Staff Session Hijack)  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Predictable PNR Generation (A04 — Low)

**Location:** `PnrGenerator.java` — `generate()`  
**Description:** PNR generated as incrementing integer. Sequential booking references are trivially enumerable.

### Link 2: Boarding Summary IDOR (A01 — Medium)

**Location:** `BookingController.java` — `getBoardingSummary()`  
**Description:** Returns full booking details without verifying the requesting user owns the PNR.

### Link 3: Stored XSS via Passenger Name (A03 — Medium)

**Location:** `BookingController.java` — `getBoardingSummary()`  
**Description:** Passenger name concatenated into raw HTML string in response; executes as Stored XSS when staff views boarding list.

---

## Summary

App-07 features a classic SQL injection (critical), a subtle session fixation vulnerability, and a booking design flaw. The chain is interesting — predictable IDs, IDOR, and Stored XSS combine for account takeover. The SQL injection is the most obvious finding.

**Overall Difficulty Score:** 2/5 (Easy-Medium — session fixation is the subtlest vulnerability)