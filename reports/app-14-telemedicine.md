# Audit Report: app-14 — Telemedicine Appointment System

**Language:** TypeScript (Express)  
**Business Domain:** Healthcare / Telemedicine  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control (IDOR)

**Severity:** High  
**Location:** `src/index.ts:208-229` — `GET /api/appointments/:id`  
**Lines:**
```typescript
// VULNERABILITY A01: Broken Access Control (IDOR)
```

**Difficulty: EASY**

- Appointment details endpoint returns private doctor notes and patient PII
- No ownership check against the authenticated user
- Any authenticated user can view any appointment by ID

### VULN-02: A02 — Cryptographic Failures (Weak JWT Secret)

**Severity:** High  
**Location:** `src/index.ts:11-13` — `JWT_SECRET`  
**Lines:**
```typescript
// VULNERABILITY A02: Weak JWT signing key
```

**Difficulty: EASY**

- JWT signed with hardcoded weak secret: `'healthcare123'`
- Offline brute-force or dictionary attack possible
- Allows token forgery and privilege escalation

### VULN-03: A07 — Identification and Authentication Failures (Missing httpOnly)

**Severity:** Medium  
**Location:** `src/index.ts:151-157` — `login()`  
**Lines:**
```typescript
// VULNERABILITY A07: Session token cookie missing httpOnly flag
```

**Difficulty: EASY**

- `httpOnly: false` allows JavaScript access to session cookie
- Exposes session to XSS-based hijacking attacks

---

## Chained Attack: chain-01

**Chain Name:** Weak JWT → IDOR Records Exfiltration  
**Combined Impact:** Database Exfiltration  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Weak JWT Secret (A02 — Medium)

**Difficulty: EASY**

- Secret `healthcare123` is trivially guessable
- Attacker can forge a JWT claiming any role (e.g., DOCTOR)

### Link 2: IDOR on Appointment Details (A01 — Medium)

**Difficulty: EASY**

- Forged token bypasses authentication but not authorization — except there is no authorization check
- Any appointment record is readable by any authenticated user

---

## Summary

App-14 is a TypeScript Express telemedicine system with an IDOR vulnerability exposing private medical records, a weak hardcoded JWT secret enabling token forgery, and a missing `httpOnly` flag on session cookies. Chain: Weak JWT → IDOR → bulk patient record exfiltration.

**Overall Difficulty Score:** 2/5 (Easy)