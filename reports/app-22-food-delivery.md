# Audit Report: app-22 — Food Delivery Order System

**Language:** Python (FastAPI)  
**Business Domain:** E-commerce / Food Delivery  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A02 — Cryptographic Failures (Hardcoded Secret)

**Severity:** Medium  
**Location:** `app.py:12-14` — `PAYMENT_SECRET`  
**Lines:**
```python
# VULNERABILITY A02: Hardcoded payment gateway API key in the source code.
# CHAIN LINK 1 (chain-01): Hardcoded payment gateway key is stored in the source code as a module constant.
PAYMENT_SECRET = "mock_sk_live_51O1W2e3R4t5Y6u7I8o9P0a1S2d3F4g5H6j7K8l9Z0x1C2v3B4n5M"
```

**Difficulty: EASY**

- Comment at line 12 explicitly marks it as `VULNERABILITY A02`
- The secret is a module-level string constant, immediately visible on reading the source
- The same secret is reused for webhook authentication — forms the basis of chain-01

### VULN-02: A04 — Insecure Design (Missing Rate Limiting)

**Severity:** Medium  
**Location:** `app.py:169-198` — `place_order()`  
**Lines:**
```python
# VULNERABILITY A04: Insecure Design - Missing rate limiting, request validation, or
# idempotency checks on order placement. Clients can send infinite duplicate order
# requests, causing denial of service, resource exhaustion, or bulk db entries.
```

**Difficulty: EASY**

- Comment at line 169-171 explicitly marks it as `VULNERABILITY A04`
- No idempotency key, rate limit, or throttling mechanism exists
- An attacker can flood the endpoint with duplicate order requests
- Each request inserts a new row into the orders table

### VULN-03: A07 — Identification and Authentication Failures (Insecure Session Cookie)

**Severity:** Medium  
**Location:** `app.py:136-143` — `login()`  
**Lines:**
```python
# VULNERABILITY A07: Session cookie set without httpOnly or secure flags.
# This allows client-side JavaScript to access the session cookie, exposing it to XSS.
response.set_cookie(
    key="session_id",
    value=session_id,
    httponly=False,
    secure=False
)
```

**Difficulty: EASY**

- Comment at line 136-137 explicitly marks it as `VULNERABILITY A07`
- `httponly=False` means any XSS vulnerability can steal the session cookie
- `secure=False` means the cookie is transmitted over unencrypted HTTP
- Session tokens are cryptographically random (`os.urandom(16).hex()`), so the weakness is purely in cookie flags

---

## Chained Attack: chain-01

**Chain Name:** Hardcoded Secret Key → Webhook Forgery → Free Orders  
**Combined Impact:** Data Modification  
**Overall Chain Difficulty: EASY**

### Link 1: Hardcoded Payment Secret (A02 — Medium)

**Location:** `app.py:12-14` — `PAYMENT_SECRET`  
**Difficulty: EASY**

- Identical to VULN-01
- Attacker extracts the hardcoded secret from the source code
- Comment at line 13 marks it as `CHAIN LINK 1 (chain-01)`

### Link 2: Webhook Authentication Bypass (A04 — Medium)

**Location:** `app.py:218-238` — `payment_webhook()`  
**Difficulty: EASY**

- Comment at line 219-220 marks it as `CHAIN LINK 2 (chain-01)`
- Webhook endpoint compares auth token against the hardcoded `PAYMENT_SECRET` via simple string equality
- No HMAC signature, no IP allowlisting, no nonce, no timestamp validation
- With the secret in hand, the attacker can forge webhook requests for any order

---

## Hints in Code (Beyond Explicit Annotations)

| Hint | Location | Description | Usefulness |
|------|----------|-------------|------------|
| `PAYMENT_SECRET = "mock_sk_live_..."` | Line 14 | Hardcoded API key visible at module level | **High** — immediately identifiable |
| `httponly=False, secure=False` | Lines 141-142 | Exposed cookie flags | **High** — clearly insecure |
| No idempotency key parameter | Lines 172-198 | Missing rate-limiting primitives | **Medium** — absence of expected pattern |
| `req.auth_token != PAYMENT_SECRET` comparison | Line 224 | Plaintext string comparison for auth | **High** — weak webhook auth |
| Decoy: bcrypt hashing for passwords | Lines 51-56, 114 | Proper password storage on seed data and registration | **Low** — contrasts with hardcoded secret |
| Decoy: parameterized SQL queries | Lines 163-165, 179, 193-194, 228, 233-235 | Safe queries throughout | **Low** — no SQLi present |

## Summary

App-22 is a straightforward FastAPI application with three medium-severity vulnerabilities. The hardcoded `PAYMENT_SECRET` at module level is trivially discoverable via source code review. The missing HttpOnly/Secure flags on the session cookie expose sessions to theft if any XSS is present. The missing rate limiting is a resource exhaustion concern. The chained attack is simple: read the hardcoded secret → forge payment webhook → mark orders as paid. All vulnerabilities are EASY difficulty with explicit annotation comments.

**Overall Difficulty Score:** 1/5 (Easy — all indicators are explicit and clearly visible)