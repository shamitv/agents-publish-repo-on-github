# Audit Report: app-32 — Customer Support Ticket System

**Language:** TypeScript (Express)  
**Business Domain:** Customer Service / Support  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control (IDOR)

**Severity:** Medium  
**Location:** `src/index.ts:201-222` — `GET /api/tickets/:id`  
**Lines:**
```typescript
// VULNERABILITY A01: Broken Access Control (IDOR) on ticket retrieval
```

**Difficulty: EASY**

- Ticket detail endpoint returns full ticket data by ID
- No check verifying the requesting user owns the ticket
- Any authenticated user can view any support ticket

### VULN-02: A03 — Injection (SQLi)

**Severity:** High  
**Location:** `src/index.ts:186-199` — `GET /api/tickets/search`  
**Lines:**
```typescript
// VULNERABILITY A03: SQL Injection in ticket search endpoint
```

**Difficulty: EASY**

- Search query `q` concatenated directly into raw SQL statement
- No parameterization or input sanitization
- Attackers can dump the entire database

### VULN-03: A05 — Security Misconfiguration (Information Leakage)

**Severity:** Medium  
**Location:** `src/index.ts:224-245` — `GET /api/system/health`  
**Lines:**
```typescript
// VULNERABILITY A05: Security Misconfiguration - Diagnostics Endpoint
```

**Difficulty: EASY**

- `/api/system/health?diagnostics=true` leaks config including:
  - Hardcoded admin recovery token
  - Cookie signing secret
  - Node version and environment details
- Also leaks database error stacks with full queries via verbose error messages

---

## Chained Attack: chain-01

**Chain Name:** Diagnostics Leak → Admin Export → Database Exfiltration  
**Combined Impact:** Database Exfiltration  
**Overall Chain Difficulty: MEDIUM**

### Link 1: Diagnostics Exposure (A05 — Medium)

**Difficulty: EASY**

- `GET /api/system/health?diagnostics=true` reveals admin recovery token `SUPPORT-ADMIN-DEV-RECOVERY-KEY-2026`
- No authentication required to call this endpoint

### Link 2: Admin Export Bypass (A01 — Medium)

**Difficulty: EASY**

- `POST /api/admin/export` authenticates via `x-admin-token` header only
- Uses the leaked token as sole authentication — no session check, no role verification
- Returns all tickets and user records

---

## Summary

App-32 is a TypeScript Express customer support ticket system with SQL injection, IDOR on ticket details, and a diagnostics endpoint leaking sensitive configuration. Chain: Health diagnostics leak → admin export token → bulk database exfiltration.

**Overall Difficulty Score:** 2/5 (Easy)