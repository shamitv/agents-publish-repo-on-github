# Audit Report: app-25 — Supply Chain Inventory Tracker

**Language:** Python (Flask)  
**Business Domain:** Logistics / Supply Chain  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A06 — Vulnerable and Outdated Components (PyYAML RCE)

**Severity:** High  
**Location:** `requirements.txt:3` — `PyYAML==5.3.1`  
**Lines:**
```
PyYAML==5.3.1
```

**Difficulty: MEDIUM**

- Comment at `app.py:143-146` marks it as `VULNERABILITY A06`
- PyYAML 5.3.1 is vulnerable to arbitrary code execution via `yaml.load()` (CVE-2020-14343)
- The `import_inventory()` endpoint uses `yaml.load(resp.text)` on fetched content
- No explicit annotation on the requirements.txt line itself — requires connecting the dependency pin to the unsafe usage

### VULN-02: A07 — Identification and Authentication Failures (Plaintext Passwords)

**Severity:** Medium  
**Location:** `app.py:8-9, 43-48, 87-91` — login and seed data  
**Lines:**
```python
# VULNERABILITY A07: Simple plaintext query comparison for passwords.
cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
```

**Difficulty: EASY**

- Comment at lines 8-9 and 87 explicitly marks it as `VULNERABILITY A07`
- Passwords are stored as plaintext in the `users` table
- Login query compares raw input against stored plaintext: `WHERE username = ? AND password = ?`
- Session cookie lacks `secure` flag (default Flask session behavior)
- Seed data also stores plaintext passwords at line 43-48

### VULN-03: A10 — Server-Side Request Forgery (SSRF)

**Severity:** Medium  
**Location:** `app.py:119-141` — `check_supplier_api()`  
**Lines:**
```python
# VULNERABILITY A10: Server-Side Request Forgery (SSRF).
# CHAIN LINK 1 (chain-01): Supplier health check endpoint fetches arbitrary user-supplied URLs
resp = requests.get(url, timeout=5)
```

**Difficulty: EASY**

- Comment at lines 119-121 explicitly marks it as `VULNERABILITY A10`
- Takes a user-supplied `url` query parameter with zero validation
- Fetches the URL with `requests.get()` and returns response body, headers, and status code
- Can access internal services (e.g., `http://169.254.169.254/`, `http://localhost:5000/`)

---

## Chained Attack: chain-01

**Chain Name:** SSRF → YAML Deserialization → Lateral Movement  
**Combined Impact:** Lateral Movement  
**Overall Chain Difficulty: MEDIUM**

### Link 1: SSRF to Fetch Internal Content (A10 — Medium)

**Location:** `app.py:119-141` — `check_supplier_api()`  
**Difficulty: EASY**

- Comment at line 120 marks it as `CHAIN LINK 1 (chain-01)`
- Attacker uses `check_supplier_api` or `import_inventory` to fetch from internal network
- Can discover internal services, cloud metadata endpoints, or local resources

### Link 2: Unsafe YAML Deserialization for RCE (A06 — Medium)

**Location:** `app.py:143-179` — `import_inventory()`  
**Difficulty: MEDIUM**

- Comment at lines 143-146 marks it as `CHAIN LINK 2 (chain-01)`
- PyYAML 5.3.1's `yaml.load()` is unsafe — executes arbitrary Python objects during parsing
- Attacker hosts a malicious YAML payload at an attacker-controlled URL accessible from the server
- Using SSRF capability, the attacker feeds this URL to `import_inventory`
- Malicious YAML like `!!python/object/apply:os.system ["id"]` triggers code execution

---

## Hints in Code (Beyond Explicit Annotations)

| Hint | Location | Description | Usefulness |
|------|----------|-------------|------------|
| `PyYAML==5.3.1` | requirements.txt | Pinned vulnerable version | **High** — known CVE for RCE |
| `yaml.load(resp.text)` | Line 165 | Unsafe deserialization of fetched content | **High** — dangerous pattern |
| `requests.get(url, timeout=5)` | Lines 133, 159 | User-controlled URL fetching | **High** — SSRF enabler |
| `"SELECT * FROM users WHERE username = ? AND password = ?"` | Line 88-90 | Plaintext password comparison | **High** — no hash verification |
| Decoy: `yaml.safe_load()` in config endpoint | Lines 189-191 | Safe YAML pattern used for admin config | **Medium** — contrast with unsafe load |
| Decoy: parameterized SQL for warehouse lookup | Lines 204-206 | Safe query pattern on warehouse endpoint | **Low** — no SQLi present |

## Summary

App-25 is a Flask supply chain tracker with three vulnerabilities. The SSRF in `check_supplier_api` allows fetching arbitrary URLs. The pinned PyYAML 5.3.1 enables RCE via `yaml.load()` when processing fetched content. Plaintext password storage makes credential theft trivial. The chained attack is potent: use SSRF to access internal resources or fetch attacker-hosted content, then exploit PyYAML deserialization for RCE and lateral movement. The PyYAML vulnerability is MEDIUM difficulty since it requires connecting the dependency version to the unsafe usage pattern.

**Overall Difficulty Score:** 2/5 (Easy-Medium — one vulnerability requires version-aware knowledge)