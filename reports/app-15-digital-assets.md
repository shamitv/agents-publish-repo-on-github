# Audit Report: app-15 — Digital Asset Management

**Language:** TypeScript (Express)  
**Business Domain:** Digital Asset / File Management  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control (IDOR)

**Severity:** High  
**Location:** `src/index.ts:135-156` — `GET /api/assets/:id`  
**Lines:**
```typescript
// VULNERABILITY A01: Broken Access Control (IDOR)
```

**Difficulty: EASY**

- Asset detail endpoint returns file metadata and download URLs by ID
- No check verifying requesting user owns the private asset (`is_public = 0`)
- Any authenticated user can view any asset's details and download link

### VULN-02: A08 — Software and Data Integrity Failures (Unrestricted File Upload)

**Severity:** High  
**Location:** `src/index.ts:90-100` / `src/index.ts:158-182` — Multer config + `POST /api/assets/upload`  
**Lines:**
```typescript
// VULNERABILITY A08: Unrestricted File Upload
```

**Difficulty: MEDIUM**

- Multer disk storage writes files to public `/uploads` directory
- Original filename preserved directly with no extension validation
- Allows uploading executable files (`.js`, `.html`, `.jsp`, etc.)

### VULN-03: A10 — Server-Side Request Forgery (SSRF)

**Severity:** Medium  
**Location:** `src/index.ts:184-228` — `POST /api/assets/import`  
**Lines:**
```typescript
// VULNERABILITY A10: Server-Side Request Forgery (SSRF)
```

**Difficulty: MEDIUM**

- Import endpoint fetches content from user-supplied URL with no validation
- No block on loopback, private, or internal IP ranges
- Response content is written directly to the public uploads directory

---

## Chained Attack: chain-01

**Chain Name:** SSRF → Unrestricted File Write → Lateral Movement / RCE  
**Combined Impact:** Lateral Movement  
**Overall Chain Difficulty: MEDIUM-HARD**

### Link 1: SSRF on Import Endpoint (A10 — Medium)

**Difficulty: MEDIUM**

- Fetches arbitrary user-supplied URL via native `fetch()`
- Attacker can target internal services (e.g., cloud metadata `http://169.254.169.254/`, internal dashboards)
- Also allows fetching content from attacker-controlled external hosts

### Link 2: Unrestricted File Write into Web Root (A08 — Medium)

**Difficulty: EASY**

- Downloaded content is written to public `/uploads` directory with user-specified filename
- No extension validation — `.js`, `.html`, or script files can be uploaded
- Can be executed by requesting `http://localhost:8015/uploads/malicious.js`
- Combined with SSRF, attacker can exfiltrate internal service data and then execute remote scripts

---

## Summary

App-15 is a TypeScript Express digital asset management system with an IDOR exposing private files, unrestricted file upload enabling RCE, and SSRF enabling internal network probing. Chain: SSRF → unrestricted file write into web root → lateral movement or RCE.

**Overall Difficulty Score:** 3/5 (Medium)