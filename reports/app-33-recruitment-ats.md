# Audit Report: app-33 — Recruitment ATS Platform

**Language:** TypeScript (Express)  
**Business Domain:** HR / Recruitment  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control (IDOR)

**Severity:** Medium  
**Location:** `src/index.ts:204-218` — `GET /api/applications/:id`  
**Lines:**
```typescript
// VULNERABILITY A01: Broken Access Control (IDOR) on job applications
```

**Difficulty: EASY**

- Application detail endpoint returns candidate PII and resume text by ID
- No ownership or role check on retrieval
- Any authenticated user can view any candidate's application

### VULN-02: A02 — Cryptographic Failures (Weak API Key Generation)

**Severity:** Medium  
**Location:** `src/index.ts:196-202` — `POST /api/auth/api-key`  
**Lines:**
```typescript
// VULNERABILITY A02: Cryptographic Failure - Weak Predictable Token Generation
```

**Difficulty: EASY**

- API keys generated using MD5 hash of the user's sequential integer ID
- MD5 is fast, reversible via rainbow tables, and trivially predictable
- Attacker can compute any user's API key knowing only their user ID

### VULN-03: A06 — Vulnerable and Outdated Components (Zip Slip Path Traversal)

**Severity:** High  
**Location:** `src/index.ts:220-261` — `POST /api/applications/upload-portfolio`  
**Lines:**
```typescript
// VULNERABILITY A06: Path Traversal via Zip Slip
```

**Difficulty: MEDIUM**

- ZIP archive extraction uses entry names directly without path traversal checks
- Entry names like `../../package.json` overwrite files outside the target directory
- Recruiter-level endpoint — requires authenticated recruiter account

---

## Chained Attack: chain-01

**Chain Name:** MD5 API Key → Zip Slip Arbitrary File Write  
**Combined Impact:** Data Modification  
**Overall Chain Difficulty: MEDIUM-HARD**

### Link 1: Predictable API Key (A02 — Medium)

**Difficulty: EASY**

- API endpoint `POST /api/auth/api-key` returns `md5(user.id)` as the API key
- Recruiter is user ID 3 → `md5("3")` = `eccbc87e4b5ce2fe28308fd9f2a7baf3`
- Attacker can compute this without any authentication

### Link 2: Zip Slip via Admin Upload (A06 — Medium)

**Difficulty: MEDIUM**

- Upload-portfolio endpoint requires recruiter role verified by session or API key
- Authenticating with the leaked recruiter API key grants access
- ZIP archive with traversal entries (`../../app.js`) overwrites files outside uploads dir
- Can overwrite application source, config, or startup scripts for RCE

---

## Summary

App-33 is a TypeScript Express recruitment ATS with IDOR exposing candidate applications, MD5-based predictable API key generation, and a Zip Slip path traversal vulnerability in portfolio upload. Chain: Predictable API key derivation → Zip Slip arbitrary file overwrite → data modification / RCE.

**Overall Difficulty Score:** 3/5 (Medium)