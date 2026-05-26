# Audit Report: app-24 — Veterinary Clinic Management

**Language:** Python (FastAPI)  
**Business Domain:** Healthcare / Veterinary  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A02 — Cryptographic Failures (Weak JWT Secret)

**Severity:** High  
**Location:** `app.py:16-19` — `generate_token()`  
**Lines:**
```python
# VULNERABILITY A02: JWT tokens are signed with a weak, hardcoded secret using HS256.
SECRET_KEY = "secret123"
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A02`
- JWT secret is `"secret123"` — trivially guessable/brute-forceable
- An attacker can forge arbitrary tokens with any role (e.g. VET, ADMIN)
- Forms the start of chain-01

### VULN-02: A03 — Injection (SQL Injection)

**Severity:** High  
**Location:** `app.py:174-191` — `search_pets()`  
**Lines:**
```python
# VULNERABILITY A03: Raw SQL query concatenates user input directly.
cursor.execute(f"SELECT * FROM pets WHERE name LIKE '%{query}%' OR species LIKE '%{query}%'")
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A03`
- User input is concatenated directly into a raw SQL query via f-string
- No parameterized query or escaping is used
- Enables UNION-based data extraction and WHERE clause manipulation

### VULN-03: A09 — Security Logging & Monitoring Failures

**Severity:** Medium  
**Location:** `app.py:206-226` — `update_prescription()`  
**Lines:**
```python
# VULNERABILITY A09: Prescription modifications produce zero audit logs or monitoring.
# No record of who changed what or when is kept.
```

**Difficulty: EASY**

- Comment explicitly marks it as `VULNERABILITY A09`
- Controlled substance dosage changes are written to DB with zero logging
- No who, what, when, or why is recorded
- Contrasts with decoy: appointment scheduling has proper audit logging

---

## Chained Attack: chain-01

**Chain Name:** Weak JWT → SQL Injection → Prescription Tampering  
**Combined Impact:** Data Modification  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Weak JWT Secret (A02 — Medium)

**Location:** `app.py:16-19` — `generate_token()`  
**Difficulty: EASY**

- Comment marks it as `CHAIN LINK 1 (chain-01)`
- Attacker guesses `"secret123"` and forges a JWT with `role: "VET"`
- This provides access to veterinarian-only endpoints

### Link 2: SQL Injection for Record Enumeration (A03 — Medium)

**Location:** `app.py:174-191` — `search_pets()`  
**Difficulty: EASY**

- Comment marks it as `CHAIN LINK 2 (chain-01)`
- Authenticated with forged VET token, attacker uses SQLi to extract pet IDs and prescription data
- UNION-based injection can extract records from any table

### Link 3: Untracked Prescription Changes (A09 — Low)

**Location:** `app.py:206-226` — `update_prescription()`  
**Difficulty: EASY**

- Comment marks it as `CHAIN LINK 3 (chain-01)`
- With VET access and target pet IDs known, attacker modifies controlled substance dosages
- No audit trail captures the modification

---

## Hints in Code (Beyond Explicit Annotations)

| Hint | Location | Description | Usefulness |
|------|----------|-------------|------------|
| `SECRET_KEY = "secret123"` | Line ~16 | Extremely weak hardcoded JWT secret | **High** — trivially guessable |
| `f"SELECT * FROM pets WHERE name LIKE '%{query}%'"` | Line ~184 | f-string SQL concatenation | **High** — obvious SQLi |
| No logging call in prescription update | Lines 206-226 | Absence of `logger.info()` or `audit_log()` | **High** — missing audit |
| Decoy: audit logs for appointment scheduling | app.py | Proper logging exists on another endpoint | **Medium** — contrast highlights absence |
| Decoy: parameterized SQL for appointments | app.py | Safe query pattern used elsewhere | **Medium** — contrast with raw f-string |
| Decoy: Pydantic validators for age/weight | app.py | Input validation on some fields | **Low** — limited scope |

## Summary

App-24 is a FastAPI veterinary clinic app with three vulnerabilities. The weak JWT secret `"secret123"` is trivially forgeable. The SQL injection via f-string concatenation in `search_pets` is explicit and easy to exploit. The missing audit logging on prescription changes allows undetected data modification. The 3-step chained attack demonstrates a realistic path: forge credentials → extract data via SQLi → tamper with controlled substance records undetected.

**Overall Difficulty Score:** 1/5 (Easy — all indicators are explicit and clearly visible)