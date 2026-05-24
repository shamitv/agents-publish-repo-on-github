# Audit Report: app-21 — Insurance Claims Processor

**Language:** Python (Flask)  
**Business Domain:** Insurance  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Insecure Direct Object Reference (IDOR)

**Severity:** High  
**Location:** `app.py:215-240` — `get_claim()`  
**Line:** Claim detail endpoint returns any claim by ID without verifying the requesting user is the claimant

**Difficulty: EASY**

- The `claim_id` path parameter is taken directly from the URL with no ownership verification.
- Any authenticated user can view any claim's PII, payout amounts, and policy details.
- No check that the claim belongs to the requesting user.

### VULN-02: A03 — SQL Injection

**Severity:** High  
**Location:** `app.py:173-212` — `search_claims()`  
**Line:** User input is concatenated directly into a raw SQL WHERE clause without parameterization

**Difficulty: EASY**

- The search query parameter is directly interpolated into a SQL string.
- Allows extraction of arbitrary data from the database.
- Classic SQLi pattern with f-string formatting.

### VULN-03: A09 — Security Logging & Monitoring Failures

**Severity:** Medium  
**Location:** `app.py:268-296` — `approve_claim()`

**Difficulty: EASY**

- High-value claim approvals and automatic payout dispatches produce no audit logs.
- Makes it impossible to detect fraudulent approvals or trace who authorized payouts.
- No log entries written for approval events.

---

## Chained Attack: chain-01

**Chain Name:** SQL Injection → IDOR Claim Access → Silent Payout Fraud  
**Combined Impact:** Data Modification  
**Overall Chain Difficulty: EASY**

### Link 1: SQL Injection (A03 — Medium)

**Location:** `app.py:173-212` — `search_claims()`  
**Difficulty: EASY**

- SQL injection in claim search reveals internal claim IDs, amounts, and status values not normally visible.

### Link 2: IDOR Claim Access (A01 — Medium)

**Location:** `app.py:215-240` — `get_claim()`  
**Difficulty: EASY**

- IDOR on claim detail endpoint allows viewing any claim's full details including claimant PII.

### Link 3: Missing Audit Logging (A09 — Low)

**Location:** `app.py:268-296` — `approve_claim()`  
**Difficulty: EASY**

- Claim approval endpoint writes no audit logs, enabling silent fraudulent payout approval.

---

## Summary

App-21 presents a 3-step chained attack combining SQLi for reconnaissance, IDOR for data access, and missing audit logs for covering tracks. Three decoy safe patterns (parameterized login, admin role guard, user-scoped policy listing) provide false-positive testing opportunities.

**Overall Difficulty Score:** 1/5 (Easiest)