# Audit Report: app-13 — Project Management Tool

**Language:** TypeScript (Express)  
**Business Domain:** Project Management / Collaboration  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control (Cross-Org Board IDOR)

**Severity:** High  
**Location:** `src/index.ts:84-96` — `getBoardById()`  
**Description:** Board retrieval endpoint fetches by numeric ID without verifying `board.orgId` matches the authenticated user's `user.orgId`.

**Difficulty: EASY**

- No cross-organization isolation check
- User from org 101 can access org 202's boards
- Sensitive board data exposed (e.g., "Secret Project X")

### VULN-02: A03 — Stored Cross-Site Scripting (XSS)

**Severity:** High  
**Location:** `public/js/app.js:100-115` — `renderTasks()`  
**Description:** Task descriptions rendered via `innerHTML` without HTML encoding.

**Difficulty: EASY**

- Task content is user-supplied and unsanitized
- Stored in memory and served to all viewers
- Script payloads execute in victim's browser

### VULN-03: A09 — Security Logging and Monitoring Failures

**Severity:** Medium  
**Location:** `src/index.ts:116-136` — `updateBoardPermissions()`  
**Description:** Permission changes made without any audit log or trace event generation.

**Difficulty: EASY**

- Visibility changes (INTERNAL → PUBLIC) leave no audit trail
- No timestamp, user ID, or before/after state recorded
- Incident response impossible without logs

---

## Chained Attack: chain-01

**Chain Name:** Board IDOR → Stored XSS in Comments → Session Token Exfiltration  
**Combined Impact:** Account Takeover (Manager Session Hijack)  
**Overall Chain Difficulty: EASY-MEDIUM**

### Link 1: Cross-Org Board Access (A01 — Medium)

**Location:** `src/index.ts` — `GET /api/boards/:id`  
**Description:** No orgId verification allows attacker to access any organization's boards and tasks.

### Link 2: Unsanitized Comments → Stored XSS (A03 — Medium)

**Location:** `src/index.ts` — `POST /api/boards/:boardId/tasks/:taskId/comments`  
**Description:** Comment content stored verbatim without HTML encoding; script tags execute when rendered via innerHTML.

### Link 3: Missing httpOnly on Session Cookie (A07 — Medium)

**Location:** `src/index.ts` — `POST /api/auth/login`  
**Description:** Session cookie set without httpOnly flag; JavaScript can read `document.cookie` and exfiltrate.

---

## Summary

App-13 is a project management tool with a realistic cross-organization data breach scenario. The chain from IDOR to XSS to session hijack is educationally valuable for demonstrating how multiple low/medium issues combine for account takeover. The missing audit logging is a subtle finding.

**Overall Difficulty Score:** 2/5 (Easy — chain requires basic web security knowledge)