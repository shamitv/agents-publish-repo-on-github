# Audit Report: app-16 — Restaurant Review Platform

**Language:** JavaScript (Express)  
**Business Domain:** Food / Reviews  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection (SQLi)

**Severity:** High  
**Location:** `src/index.js:162-175` — `GET /api/restaurants/search`  
**Lines:**
```javascript
// VULNERABILITY A03: SQL Injection in restaurant search endpoint
```

**Difficulty: EASY**

- Search query `q` concatenated directly into raw SQL
- No parameterization or sanitization
- UNION-based injection can dump arbitrary tables

### VULN-02: A01 — Broken Access Control (IDOR)

**Severity:** Medium  
**Location:** `src/index.js:193-214` — `POST /api/reviews/:id/edit`  
**Lines:**
```javascript
// VULNERABILITY A01: Broken Access Control (IDOR) on review edit
```

**Difficulty: EASY**

- Review edit endpoint does not verify ownership
- Any authenticated user can edit any review
- Can modify review text and rating

### VULN-03: A07 — Identification and Authentication Failures (Weak Session Tokens)

**Severity:** Medium  
**Location:** `src/index.js:123-143` — `POST /api/auth/login`  
**Lines:**
```javascript
// VULNERABILITY A07: Predictable session token generation via Math.random()
```

**Difficulty: EASY**

- Session IDs generated using `Math.random()` which is not cryptographically secure
- Predictable and brute-forceable
- Allows session hijacking

---

## Chained Attack: chain-01

**Chain Name:** Predictable Session → IDOR Review Sabotage  
**Combined Impact:** Data Modification  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Predictable Session Token (A07 — Medium)

**Difficulty: EASY**

- Session IDs generated via `Math.random().toString(36)` — predictable
- Attacker can enumerate or predict active session IDs

### Link 2: IDOR Review Edit (A01 — Medium)

**Difficulty: EASY**

- Review edit endpoint lacks ownership check
- Hijacked session can modify any review's text and rating

---

## Summary

App-16 is a JavaScript Express restaurant review platform with SQL injection in restaurant search, IDOR allowing arbitrary review edits, and predictable `Math.random()`-based session tokens. Chain: Predictable session hijacking → IDOR review modification → data manipulation.

**Overall Difficulty Score:** 2/5 (Easy)