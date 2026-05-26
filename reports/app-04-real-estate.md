# Audit Report: app-04 — Real Estate Listing Platform

**Language:** Python (Flask)  
**Business Domain:** Real Estate / Property Listings  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A03 — OS Command Injection (RCE)

**Severity:** High  
**Location:** `app.py:168-186` — `analyze_listing()`  
**Lines:**
```python
cmd = f"echo 'Metadata inspection for property description filename: {filename}'"
p = subprocess.Popen(cmd, shell=True, ...)
```

**Difficulty: EASY**

- Comment at line 167: "OWASP VULNERABILITY A03: OS Command Injection via Subprocess shell=True"
- `shell=True` flag is explicitly set — a known dangerous pattern
- `cmd_executed` field in response shows the full command, including injected payloads
- The `filename` parameter is user-controlled with zero sanitization

### VULN-02: A05 — Security Misconfiguration

**Severity:** Medium  
**Location:** `app.py:11` — Flask config  
**Lines:** `app.config['SECRET_KEY'] = 'dev'` and `app.run(..., debug=True)`

**Difficulty: EASY**

- Comment at line 9-10: "OWASP VULNERABILITY A05: Security Misconfiguration"
- Secret key is `'dev'` — trivially guessable, enables Flask session tampering
- `debug=True` at line 265 enables the Werkzeug debugger with remote code execution capability
- Both are immediately visible at the top and bottom of the file

### VULN-03: A10 — Server-Side Request Forgery (SSRF)

**Severity:** High  
**Location:** `app.py:189-212` — `import_external_image()`  
**Lines:** `res = requests.get(target_url, timeout=4)` with no URL validation

**Difficulty: EASY**

- Comment at line 188: "OWASP VULNERABILITY A10: Server-Side Request Forgery (SSRF)"
- `requests.get()` called directly on user-supplied URL
- No allowlist, no IP restriction, no DNS sandboxing
- Error messages return exception details aiding reconnaissance

---

## Chained Attack: chain-01

**Chain Name:** Debug Environment Exposure → SSRF Internal Recon → OS Command Injection RCE  
**Combined Impact:** Lateral Movement  
**Overall Chain Difficulty: EASY**

### Link 1: Debug Environment Info Leak (A05 — Low)

**Location:** `app.py:219-222` — `debug_env()`  
**Difficulty: EASY**

- `CHAIN LINK 1 (chain-01)` comment at lines 215-218 explicitly explains the purpose
- Unauthenticated endpoint returns ALL environment variables and current working directory
- Reveals internal file paths, service URLs, and potential credentials

### Link 2: SSRF to Probe Internal Services (A10 — High)

**Location:** `app.py:189-212` — `import_external_image()`  
**Difficulty: EASY**

- Same as VULN-03
- Armed with environment info from Link 1, attacker can probe internal services
- Returns `bytes_fetched`, `content_type`, `status_code` — confirms reachable services

### Link 3: OS Command Injection RCE (A03 — High)

**Location:** `app.py:168-186` — `analyze_listing()`  
**Difficulty: EASY**

- Same as VULN-01
- After mapping internal topology, attacker executes arbitrary commands
- `cmd_executed` in response confirms the injection worked

---

## Hints in Code (Beyond Explicit Annotations)

| Hint | Location | Description | Usefulness |
|------|----------|-------------|------------|
| `shell=True` flag | Line 177 | Explicit dangerous subprocess flag | **High** — obvious RCE indicator |
| `cmd_executed` in response | Line 180 | Returns full command with injected payloads | **High** — confirms exploitation |
| `SECRET_KEY = 'dev'` | Line 11 | Known default secret key | **High** — enables session forging |
| `debug=True` in run config | Line 265 | Enables remote Werkzeug debugger | **High** — RCE via debugger console |
| `requests.get(target_url)` raw call | Line 201 | User-controlled URL fetched server-side | **High** — SSRF indicator |
| Error messages with exception details | Lines 211-212 | Returns str(ex) with full traceback | **Medium** — aids recon |
| `os.environ.items()` dump | Line 221 | Returns ALL environment variables | **High** — credential leakage |
| `@app.route('/api/debug/env')` naming | Line 219 | "debug" in path signals non-production | **Medium** — obvious dev endpoint |
| Decoy: parameterized SQL | Lines 92-93, 129 | Proper queries on some endpoints | **Low** — contrasts with command injection |
| Decoy: role check on messages | Lines 243-244 | Auth gate on one endpoint | **Low** — makes missing auth on others noticeable |

## Summary

App-04 has all vulnerabilities at **EASY** difficulty. The command injection is particularly obvious with `shell=True` and the `cmd_executed` response field. The `debug=True` with `SECRET_KEY='dev'` combination enables full session forging. The chain progresses logically: read environment → probe internal services → execute commands. All three vulns are explicitly annotated with `OWASP VULNERABILITY` comments.

**Overall Difficulty Score:** 1/5 (Easy — all indicators are explicit and clearly visible)