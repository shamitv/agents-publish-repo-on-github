# Audit Report: app-01 — E-Commerce Product Catalog API

**Language:** Python (Flask)  
**Business Domain:** Retail / E-Commerce  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A03 — SQL Injection (Product Search)

**Severity:** High  
**Location:** `app.py:164` — `list_products()`  
**Line:** `query = f"SELECT id, sku, name, description, category, price, quantity FROM products WHERE name LIKE '%{q}%' OR description LIKE '%{q}%'"`

**Difficulty: EASY**

- The `q` parameter from `request.args.get('q')` is directly interpolated into an f-string SQL query.
- The `VULNERABILITY` comment explicitly calls out "SQL Injection target".
- The error handler returns `query_executed` back to the user — a strong hint.
- The `debug_query` field is always returned in the JSON response, leaking the crafted query even on success.

### VULN-02: A01 — Insecure Direct Object Reference (IDOR)

**Severity:** High  
**Location:** `app.py:247` — `get_order_details()`  
**Line:** `cursor.execute("SELECT o.id, ... FROM orders o ... WHERE o.id = ?", (order_id,))`

**Difficulty: EASY**

- The `order_id` path parameter is taken directly from the URL with no ownership verification.
- Any authenticated user can view any order by enumerating IDs.
- The function name `get_order_details` is clear about what it does.
- The method is unguarded — no check that `order.user_id == session['user_id']`.

### VULN-03: A09 — Security Logging & Monitoring Failure

**Severity:** Medium  
**Location:** `app.py:320` — `create_order()`

**Difficulty: EASY**

- The `VULNERABILITY` comment at line 319 explicitly states: "Severe Logging Failure. Critical financial checkout and catalog stock deduction complete, but no auditable logs are written!"
- The comment itself is the strongest hint.

---

## Chained Attack: chain-01

**Chain Name:** User Enumeration → Session Forge → Admin Takeover  
**Combined Impact:** Account Takeover  
**Overall Chain Difficulty: EASY**

### Link 1: User Enumeration (A01 — Low)

**Location:** `app.py:137-145` — `user_exists()`  
**Difficulty: EASY**

- Returns `200 {"exists": True}` vs `404 {"exists": False}` based on username existence.
- No authentication required.
- The `CHAIN LINK 1` comment at line 134 explicitly explains the purpose.
- Function is literally named `user_exists`.

### Link 2: Hardcoded Secret Key (A05 — Medium)

**Location:** `app.py:6` — `app.secret_key`  
**Difficulty: EASY**

- `app.secret_key = 'cyberpunk_secret_key_glow_neon_quantum_core'` is a module-level constant visible to anyone with source access.
- The string is absurdly descriptive and stands out immediately.
- Can be used to forge Flask session cookies for any role (including ADMIN).

### Link 3: No CSRF Protection (A05 — Low)

**Location:** All POST endpoints  
**Difficulty: EASY**

- No CSRF tokens on any state-changing endpoint.
- A forged admin session cookie is all that's needed to call `POST /api/products` or any other admin action.

---

## Hints in Code (Beyond Explicit `VULNERABILITY` / `CHAIN LINK` Annotations)

| Hint | Location | Description | Usefulness |
|------|----------|-------------|------------|
| `debug_query` in response | `list_products()` return | The JSON response always includes the executed SQL query | **High** — directly reveals SQLi payload success/failure |
| Verbose error with `query_executed` | SQLi exception handler (line 170) | Returns the full query and error message to the user | **High** — helps attacker refine injection |
| `'cyberpunk_secret_key_glow_neon_quantum_core'` | Line 6 | Extremely conspicuous hardcoded secret key | **High** — obvious to any code reviewer |
| `user_exists` function name | Line 138 | Plainly indicates the endpoint's purpose | **Medium** — naming draws attention |
| Decoy comment: "Secure, parameterized SQL query" | Line 111-113 | Explicitly calls out the login query as "secure" — draws contrast to insecure queries | **Medium** — tells analyst where to look for insecure patterns |
| `app.run(debug=True)` | Line 330 | Debug mode enabled in production | **Low** — standard Flask misconfig, not a direct hint about other vulns |
| `CHAIN LINK 1` comment explaining enumeration | Lines 134-136 | Already describes the full chain purpose | **Very High** — the comment itself outlines the attack scenario |
| `db_conn.rollback()` | Line 326 | Indicates critical state-changing operation happening that could be exploited | **Low** — implicit hint that sensitive writes occur here |
| `return jsonify({'exists': True}), 404` vs `200` | Lines 144-145 | HTTP status code differentiation is a classic enumeration technique | **Medium** — observable behavior contrast |

## Summary

All vulnerabilities and chain links in app-01 are **EASY** difficulty. The code includes extensive explicit annotations (`VULNERABILITY`, `CHAIN LINK`), highly conspicuous hardcoded secrets, verbose error responses that leak SQL, and obvious naming conventions. The strongest hints are the returned `debug_query` field (exposes SQLi attempts) and the hardcoded `secret_key` that any automated scanner would flag immediately. The only subtle aspect is the IDOR, which requires the attacker to enumerate order IDs — but the absence of ownership checks is quickly evident from reading the code.

**Overall Difficulty Score:** 1/5 (Easiest)