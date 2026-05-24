# Audit Report: app-34 — Subscription Box Service

**Language:** TypeScript (Express)  
**Business Domain:** E-Commerce / Subscriptions  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection (SQLi)

**Severity:** High  
**Location:** `src/index.ts:176-189` — `GET /api/packages/search`  
**Lines:**
```typescript
// VULNERABILITY A03: SQL Injection in package search endpoint
```

**Difficulty: EASY**

- Search query `q` concatenated directly into raw SQL statement
- No parameterization or input sanitization
- UNION-based injection can dump arbitrary tables (users, subscriptions)

### VULN-02: A07 — Identification and Authentication Failures (Unsalted MD5)

**Severity:** Medium  
**Location:** `src/index.ts:56-68` (seed), `src/index.ts:126-141` (register), `src/index.ts:143-165` (login)  
**Lines:**
```typescript
// VULNERABILITY A07: Unsalted MD5 password hashes
```

**Difficulty: EASY**

- All passwords stored as unsalted MD5 hashes
- Trivially crackable via rainbow tables or brute force
- Admin password `adminpass2026` hashes to `a57e4e138a08d3744952bd0176cd1f91`

### VULN-03: A09 — Security Logging and Monitoring Failures

**Severity:** Low  
**Location:** `src/index.ts:201-233` — `POST /api/subscriptions/update`  
**Lines:**
```typescript
// VULNERABILITY A09: Security Logging and Monitoring Failures
```

**Difficulty: EASY**

- Subscription status updates are not logged or audited
- No trace of unauthorized modifications or account changes
- Contrast with profile endpoint that properly logs security events

---

## Chained Attack: chain-01

**Chain Name:** SQLi → Unsalted MD5 Cracking → Account Takeover  
**Combined Impact:** Account Takeover  
**Overall Chain Difficulty: MEDIUM**

### Link 1: SQL Injection in Package Search (A03 — Medium)

**Difficulty: EASY**

- Use UNION injection to dump users table:
  `?q=coffee' UNION SELECT 1,username,password_hash,role FROM users --`
- Retrieves unsalted MD5 password hashes for all users

### Link 2: Unsalted MD5 Credential Cracking (A07 — Medium)

**Difficulty: EASY**

- Admin hash `a57e4e138a08d3744952bd0176cd1f91` cracks to `adminpass2026` via offline lookup
- Attacker logs in as admin and takes over all subscriptions

---

## Summary

App-34 is a TypeScript Express subscription box service with SQL injection in package search, unsalted MD5 password storage, and missing security logging on critical subscription updates. Chain: SQLi → unsalted MD5 credential dump → account takeover.

**Overall Difficulty Score:** 2/5 (Easy)