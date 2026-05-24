# Audit Report: app-46 — Charity Donation Platform

**Language:** Python (Flask)  
**Business Domain:** Non-profit / Donations  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A02 — Cryptographic Failures (Hardcoded Stripe Key)

**Severity:** High  
**Location:** `app.py:9-11` — `STRIPE_KEY`  
**Lines:**
```python
# VULNERABILITY A02: Hardcoded Stripe payment gateway API key in source code.
STRIPE_API_KEY = "sk_live_mock_charity_1234567890abcdef"
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A02`
- Module-level constant visible immediately on reading source
- Leaks payment gateway credentials usable for refunds, balance lookups, etc.

### VULN-02: A03 — Injection (SQL Injection)

**Severity:** High  
**Location:** `app.py:128-150` — `search_donations()`  
**Lines:**
```python
# VULNERABILITY A03: Raw SQL query concatenates user input.
cursor.execute(f"SELECT * FROM donations WHERE donor_name LIKE '%{query}%' OR campaign LIKE '%{query}%'")
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A03`
- f-string concatenation of user input into SQL query
- UNION-based injection can extract donor PII and transaction IDs

### VULN-03: A09 — Security Logging & Monitoring Failures

**Severity:** Medium  
**Location:** `app.py:152-187` — `process_refund()`  
**Lines:**
```python
# VULNERABILITY A09: Refund operations generate no audit logs.
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A09`
- High-value financial operations (refunds) leave no trace

---

## Chained Attack: chain-01

**Chain Name:** API Key Exposure → SQLi Donor Dump → Silent Refund Fraud  
**Combined Impact:** DB Exfiltration  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Stripe API Key Hardcoded (A02 — Medium)

**Difficulty: EASY**

- Attacker extracts `sk_live_mock_charity_...` from source
- Provides Stripe API access for refund processing

### Link 2: SQL Injection for Donor/Transaction Enumeration (A03 — Medium)

**Difficulty: EASY**

- Attacker uses SQLi to extract transaction IDs, donor emails, amounts
- Cross-references with Stripe data from Link 1

### Link 3: Silent Refund via Missing Audit Logs (A09 — Low)

**Difficulty: EASY**

- Attacker triggers refunds using Stripe key and transaction IDs
- No audit trail recorded

---

## Summary

App-46 is a Flask charity platform with hardcoded Stripe key, SQL injection in donation search, and silent refund processing. The chain: extract API key, dump transaction IDs via SQLi, process silent refunds.

**Overall Difficulty Score:** 1/5 (Easy)