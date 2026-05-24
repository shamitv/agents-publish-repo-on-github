# Audit Report: app-20 — Fitness Tracker

**Language:** JavaScript (Express)  
**Business Domain:** Health / Fitness  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A07 — Identification and Authentication Failures (Weak Session Tokens)

**Severity:** Medium  
**Location:** `src/index.js:107-127` — `POST /api/auth/login`  
**Lines:**
```javascript
// VULNERABILITY A07: Predictable session token generation via Math.random()
```

**Difficulty: EASY**

- Session IDs generated using `Math.random()` — not cryptographically secure
- Predictable and brute-forceable
- Allows session hijacking

### VULN-02: A01 — Broken Access Control (IDOR)

**Severity:** Medium  
**Location:** `src/index.js:148-163` — `GET /api/activities/:id`  
**Lines:**
```javascript
// VULNERABILITY A01: Broken Access Control (IDOR) on fitness activity details
```

**Difficulty: EASY**

- Activity detail endpoint does not verify ownership
- Any authenticated user can view any user's fitness activities
- Exposes duration, calories, type, and date

### VULN-03: A06 — Prototype Pollution (Vulnerable Components)

**Severity:** Medium  
**Location:** `src/index.js:165-177` — `unsafeMerge` function  
**Lines:**
```javascript
// VULNERABILITY A06: Prototype Pollution via Custom Merger
```

**Difficulty: MEDIUM**

- Custom recursive merge function does not filter `__proto__` or `constructor` keys
- Allows prototype pollution attack via `POST /api/user/settings`
- Can lead to denial of service or property injection

---

## Chained Attack: chain-01

**Chain Name:** Predictable Session → IDOR Activity Theft  
**Combined Impact:** DB Exfiltration  
**Overall Chain Difficulty: EASY**

### Link 1: Predictable Session Token (A07 — Medium)

**Difficulty: EASY**

- Session IDs generated via `Math.random().toString(36)` — predictable
- Attacker can enumerate or predict active session IDs

### Link 2: IDOR Activity View (A01 — Medium)

**Difficulty: EASY**

- Activity detail endpoint lacks ownership check
- Hijacked session can view any user's private fitness activities

---

## Summary

App-20 is a JavaScript Express fitness tracker with predictable `Math.random()`-based session tokens, IDOR on activity details, and a prototype pollution vulnerability in a custom object merger. Chain: Predictable session hijacking → IDOR activity data exfiltration.

**Overall Difficulty Score:** 2/5 (Easy)