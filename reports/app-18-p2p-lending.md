# Audit Report: app-18 — Peer-to-Peer Lending Platform

**Language:** JavaScript (Express)  
**Business Domain:** Finance / Lending  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A02 — Cryptographic Failures (Plaintext Passwords)

**Severity:** Medium  
**Location:** `src/index.js:38-51` — `initDb`, `src/index.js:88-101` — `POST /api/auth/register`  
**Lines:**
```javascript
// VULNERABILITY A02: Storing user passwords in plaintext (no hashing)
```

**Difficulty: EASY**

- All user passwords stored and transmitted in plaintext
- No hashing at all — direct string comparison in login
- Admin password `lenderSecure2026!` stored in plaintext

### VULN-02: A01 — Broken Access Control (IDOR)

**Severity:** Medium  
**Location:** `src/index.js:141-156` — `GET /api/contracts/:id`  
**Lines:**
```javascript
// VULNERABILITY A01: Broken Access Control (IDOR) on loan contracts
```

**Difficulty: EASY**

- Contract retrieval endpoint does not verify ownership
- Any authenticated user can read any borrower's loan contract
- Exposes loan amounts, interest rates, and status

### VULN-03: A04 — Insecure Design (Negative Interest Rate)

**Severity:** Medium  
**Location:** `src/index.js:158-183` — `POST /api/loans/apply`  
**Lines:**
```javascript
// VULNERABILITY A04: Insecure Design - Negative Interest Rate / Zero Rate Bypass
```

**Difficulty: EASY**

- Loan application endpoint does not validate interest rates
- Negative or zero interest rates accepted
- Allows borrower to take loans that accrue negative interest (money back)

---

## Chained Attack: chain-01

**Chain Name:** Debug Credential Leak → IDOR Contract Harvesting  
**Combined Impact:** DB Exfiltration  
**Overall Chain Difficulty: EASY**

### Link 1: Plaintext Credential Leak (A02 — Medium)

**Difficulty: EASY**

- `GET /api/debug/users` returns all users with plaintext passwords
- No authentication required
- Attacker obtains admin credentials `lenderSecure2026!`

### Link 2: IDOR Contract Read (A01 — Medium)

**Difficulty: EASY**

- Authenticated as admin, attacker calls `GET /api/contracts/1`, `GET /api/contracts/2`, etc.
- Exfiltrates all loan contract details (amounts, interest rates, statuses)

---

## Summary

App-18 is a JavaScript Express P2P lending platform with plaintext password storage, IDOR on contract details, and missing validation on loan interest rates. Chain: Debug user dump → plaintext credential extraction → IDOR contract data exfiltration.

**Overall Difficulty Score:** 1/5 (Very Easy)