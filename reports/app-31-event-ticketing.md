# Audit Report: app-31 — Event Ticketing Platform

**Language:** TypeScript (Express)  
**Business Domain:** Entertainment / Ticketing  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection (SQLi)

**Severity:** High  
**Location:** `src/index.ts:148-161` — `GET /api/events/search`  
**Lines:**
```typescript
// VULNERABILITY A03: SQL Injection
```

**Difficulty: EASY**

- User search query `q` concatenated directly into raw SQL
- No parameterization or sanitization of input
- Attackers can dump tables, bypass authentication, or extract booking data

### VULN-02: A04 — Insecure Design (Missing Rate Limits / Concurrency Controls)

**Severity:** Medium  
**Location:** `src/index.ts:176-223` — `POST /api/tickets/book`  
**Lines:**
```typescript
// VULNERABILITY A04: Insecure Design (Missing Rate Limits and Concurrency Controls)
```

**Difficulty: MEDIUM**

- No transactional locking on ticket inventory updates
- No rate limiting on booking endpoint
- Automated scripts can deplete ticket inventory (scalping / DoS)

### VULN-03: A07 — Identification and Authentication Failures (Weak Session Generation)

**Severity:** Medium  
**Location:** `src/index.ts:126-130` — `login()`  
**Lines:**
```typescript
// VULNERABILITY A07: Session key generated via Math.random()
```

**Difficulty: MEDIUM**

- Session IDs generated with `Math.random()` (predictable PRNG)
- 6-digit numeric session tokens are easily brute-forced
- Allows session hijacking of active users

---

## Chained Attack: chain-01

**Chain Name:** Predictable Session → SQLi Ticket Theft  
**Combined Impact:** Account Takeover  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Weak Session Generation (A07 — Medium)

**Difficulty: MEDIUM**

- 6-digit numeric session tokens are predictable
- Attacker can brute-force or predict tokens of active customers

### Link 2: SQL Injection in Search (A03 — Medium)

**Difficulty: EASY**

- Once session is hijacked, attacker can use SQLi in search to dump booking records
- Can extract payment details, steal or cancel premium reservations

---

## Summary

App-31 is a TypeScript Express event ticketing platform with SQL injection in event search, missing concurrency controls on ticket booking (enabling scalping), and predictable `Math.random()`-based session tokens enabling session hijacking. Chain: Predictable session → SQLi → account takeover and ticket theft.

**Overall Difficulty Score:** 2/5 (Easy)