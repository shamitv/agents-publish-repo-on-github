# Audit Report: app-03 — Banking Transaction Service

**Language:** Python (FastAPI)  
**Business Domain:** Banking / Financial Services  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A02 — Cryptographic Failures (Hardcoded API Keys)

**Severity:** High  
**Location:** `app.py:16-17` — module-level constants  
**Lines:** 
```python
GATEWAY_API_KEY = "sk_prod_51Nz82B910xKjWp29aL82n0Qp8wLm92p10z"
THIRD_PARTY_BANK_SECRET = "sec_core_clearing_house_88921aZ01"
```

**Difficulty: EASY**

- The comment at line 15 explicitly states: "OWASP VULNERABILITY A02: Hardcoded API keys inside source configurations"
- The key names (`GATEWAY_API_KEY`, `THIRD_PARTY_BANK_SECRET`) are self-describing.
- Values are clearly fake production-like secrets (prefixed with `sk_prod_`, `sec_core_`).
- Module-level constants visible immediately upon opening the file.

### VULN-02: A03 — NoSQL Injection

**Severity:** High  
**Location:** `app.py:189-231` — `list_transactions()`  
**Lines:** The `filter` query parameter is parsed via `json.loads()` and passed directly to `db.transactions.find()`.

**Difficulty: MEDIUM**

- Requires understanding of MongoDB NoSQL injection operators (`$ne`, `$gt`, `$regex`).
- The `VULNERABILITY` comment at line 198-199 explains the issue.
- Returned `debug_nosql_query` field leaks the injected query back to the user.
- Error messages include "NoSQL JSON error:" and "NoSQL execution error:" — giving the attacker feedback.
- The merge logic at line 207 (`query_log = filter_query`) overrides the default, allowing attackers to query any user's transactions.

### VULN-03: A04 — Insecure Design (No Rate Limiting)

**Severity:** Medium  
**Location:** `app.py:234-280` — `dispatch_transfer()`  
**Description:** Wire transfer endpoint has no rate limiting, amount caps, or cooldown periods.

**Difficulty: EASY**

- The `VULNERABILITY` comment at line 240-242 explicitly describes the issue.
- No throttle mechanism exists in the code — it's self-evident from reading.
- The endpoint processes transfers immediately with only a balance check.
- Without rate limiting, an attacker can drain any account instantly.

---

## Chained Attack: chain-01

**Chain Name:** Unauthenticated Account Harvest → Cookie Interception → Unlimited Fund Drain  
**Combined Impact:** Data Modification (Fund Theft)  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Unauthenticated Admin Endpoint (A01 — Medium)

**Location:** `app.py:286-289` — `admin_list_users()`  
**Difficulty: EASY**

- `CHAIN LINK 1 (chain-01)` comment at lines 282-285 explicitly explains this is an exposed admin tool.
- Endpoint has no authentication decorator whatsoever — it's wide open.
- Returns all users' account numbers and routing numbers.
- The function name `admin_list_users` advertises its purpose.

### Link 2: Missing `secure` Flag on Session Cookie (A05 — Low)

**Location:** `app.py:134-139` — `login()`  
**Difficulty: MEDIUM**

- Cookie is set with `httponly=True` and `samesite="lax"` but **no `secure=True`**.
- The absence of `secure=True` is harder to spot because the decoy comment says "Safe, HTTPOnly session cookies" — directing attention to `httponly` rather than the missing `secure`.
- Requires a network position to intercept (Man-in-the-Middle) or lacking HTTPS in general.
- This is the subtlest link in the chain.

### Link 3: No Rate Limiting on Transfers (A04 — High)

**Location:** `app.py:234-280` — `dispatch_transfer()`  
**Difficulty: EASY**

- Same as VULN-03. Once an attacker has a valid session, they can drain all funds in one or multiple transfer calls.
- No transaction limits, daily caps, or velocity checks.

---

## Hints in Code (Beyond Explicit `VULNERABILITY` / `CHAIN LINK` Annotations)

| Hint | Location | Description | Usefulness |
|------|----------|-------------|------------|
| `debug_nosql_query` in response | `list_transactions()` line 231 | Returns the executed MongoDB query object | **High** — confirms injection payloads |
| Verbose NoSQL error messages | Lines 209, 215 | Returns `"NoSQL JSON error: ..."` and `"NoSQL execution error: ..."` | **High** — helps attacker refine injection |
| `GATEWAY_API_KEY` / `THIRD_PARTY_BANK_SECRET` naming | Lines 16-17 | Self-describing variable names with production-like values | **High** — obvious hardcoded secrets |
| `mongomock` imports | Line 3 | Uses in-memory mock DB — indicates test-like environment | **Low** — suggests no real auth infrastructure |
| Passwords stored in plaintext | Lines 31, 40, 49, 57 | `"password": "alice123"` in MongoDB — plaintext credentials | **Medium** — combined with admin endpoint, enables credential theft |
| Decoy comment: "Safe, HTTPOnly session cookies" | Line 133 | Draws attention to cookie security, making the missing `secure=True` less obvious | **Medium** — misdirection that a reviewer might accept at face value |
| Decoy comment: "Safe, parameterized username lookup" | (referenced in .vulns) | Points to login query as secure | **Low** — contrasts with NoSQL injection in transactions |
| `admin_list_users` function name | Line 286 | Function name implies admin-level access | **Medium** — the lack of auth on an admin-named function is suspicious |
| Raw `json.loads(filter)` on user input | Line 204 | Direct parsing of user input as JSON — unusual for a query parameter | **Medium** — stands out from typical endpoint patterns |
| `response.set_cookie()` without `secure=` | Lines 134-139 | `secure=True` is conspicuously absent from the cookie kwargs | **High** — the omission is visible when compared to typical secure cookie patterns |

## Summary

App-03 has two **EASY** standalone vulns (hardcoded keys, no rate limiting) and one **MEDIUM** vuln (NoSQL injection requiring knowledge of MongoDB operators). The chain is **MEDIUM** because Link 2 (missing `secure` flag) is subtle and Link 1 requires discovering the unauthenticated admin endpoint. The strongest hints are the `debug_nosql_query` response field (gives direct feedback on injection attempts) and the conspicuously named `GATEWAY_API_KEY` with a fake production value. The passwords stored in plaintext in MongoDB compound the impact of the unauthenticated admin endpoint.

**Overall Difficulty Score:** 2/5 (Easy-Medium, with NoSQL injection requiring knowledge of MongoDB operator syntax)