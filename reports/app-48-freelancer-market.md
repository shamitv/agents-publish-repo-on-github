# Audit Report: app-48 — Freelancer Marketplace

**Language:** Python (FastAPI)  
**Business Domain:** Freelance / Gig Economy  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control (IDOR on Proposals)

**Severity:** Medium  
**Location:** `app.py:143-155` — `get_proposal()`  
**Lines:**
```python
# VULNERABILITY A01: No ownership check on proposal detail endpoint.
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A01`
- Any authenticated user can view any proposal's bid amount and details
- No validation that caller is the hiring client or submitting freelancer

### VULN-02: A04 — Insecure Design (Premature Payment Release)

**Severity:** Medium  
**Location:** `app.py:170-189` — `release_payment()`  
**Lines:**
```python
# VULNERABILITY A04: Payment release lacks delivery verification and client-job association check.
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A04`
- No delivery verification before releasing escrow
- No check that caller is the actual client for the job

### VULN-03: A07 — Authentication Failures (Weak Session Tokens)

**Severity:** Medium  
**Location:** `app.py:113-130` — `login()`  
**Lines:**
```python
# VULNERABILITY A07: Session tokens generated with predictable random.randint().
```

**Difficulty: MEDIUM**

- Comment explicitly marks it as `VULNERABILITY A07`
- Uses `random.randint()` instead of `secrets.token_hex()` or similar
- Tokens are predictable, enabling session hijacking

---

## Chained Attack: chain-01

**Chain Name:** Weak Token → IDOR Bid Espionage → Payment Fraud  
**Combined Impact:** Account Takeover  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Weak Session Token (A07 — Medium)

**Difficulty: MEDIUM**

- Predictable PRNG token generation
- Attacker predicts/brute-forces another user's session

### Link 2: IDOR on Proposals (A01 — Medium)

**Difficulty: EASY**

- Hijacked session reads competitor bid details

---

## Summary

App-48 is a FastAPI freelancer marketplace with IDOR on proposals, premature payment release, and weak session tokens via `random.randint()`. Chain: predict session → steal competitor bids → defraud payments.

**Overall Difficulty Score:** 2/5 (Easy-Medium)