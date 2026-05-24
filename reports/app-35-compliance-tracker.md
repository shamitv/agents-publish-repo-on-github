# Audit Report: app-35 — Compliance Document Tracker

**Language:** TypeScript (Express)  
**Business Domain:** Legal / Compliance  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control (IDOR)

**Severity:** Medium  
**Location:** `src/index.ts:166-180` — `GET /api/documents/:id`  
**Lines:**
```typescript
// VULNERABILITY A01: Broken Access Control (IDOR) on document details retrieval
```

**Difficulty: EASY**

- Document detail endpoint returns compliance document contents by ID
- No ownership or role check on retrieval
- Any authenticated user can view any compliance document

### VULN-02: A05 — Security Misconfiguration (Information Leakage)

**Severity:** Medium  
**Location:** `src/index.ts:236-252` — `GET /api/admin/debug`  
**Lines:**
```typescript
// VULNERABILITY A05: Security Misconfiguration - Dev Mode Credentials Disclosure
```

**Difficulty: EASY**

- Debug endpoint `GET /api/admin/debug?dev=true` leaks admin token `ADMIN-DEV-TOKEN-KEY-8871`
- Also leaks environment, database type, and version info
- No authentication required to call this endpoint

### VULN-03: A08 — Software and Data Integrity Failures (Insecure Deserialization)

**Severity:** High  
**Location:** `src/index.ts:182-209` — `POST /api/documents`  
**Lines:**
```typescript
// VULNERABILITY A08: Software and Data Integrity Failures - Insecure Deserialization
```

**Difficulty: MEDIUM**

- Document metadata is deserialized using `eval()` on user-supplied data
- Allows arbitrary code execution on the server
- Contrast with `/api/documents/safe` endpoint that properly uses `JSON.parse()`

---

## Chained Attack: chain-01

**Chain Name:** Debug Config Leak → Admin Document Access  
**Combined Impact:** Account Takeover  
**Overall Chain Difficulty: EASY**

### Link 1: Debug Endpoint Token Disclosure (A05 — Medium)

**Difficulty: EASY**

- `GET /api/admin/debug?dev=true` reveals admin token `ADMIN-DEV-TOKEN-KEY-8871`
- No authentication required

### Link 2: IDOR via Admin Auth (A01 — Medium)

**Difficulty: EASY**

- Document detail endpoint uses `requireAuth` middleware that accepts `x-admin-token` header
- The leaked token authenticates as admin (user ID 3)
- Attacker can fetch arbitrary documents with the leaked token

---

## Summary

App-35 is a TypeScript Express compliance document tracker with IDOR on document retrieval, a debug endpoint leaking the admin token, and insecure deserialization via `eval()` in document creation. Chain: Debug token leak → IDOR document access → sensitive data exfiltration.

**Overall Difficulty Score:** 2/5 (Easy)