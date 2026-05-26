# Audit Report: app-11 — Social Media Analytics Dashboard

**Language:** TypeScript (Express)  
**Business Domain:** Social Media / Marketing Analytics  
**Date:** 2026-05-24

---

## Standalone Vulnerabilities

### VULN-01: A10 — Server-Side Request Forgery (SSRF)

**Severity:** High  
**Location:** `src/index.ts:100-115` — `generatePreview()`  
**Description:** POST `/api/preview` fetches remote URLs using `axios.get()` with no domain/IP validation.

**Difficulty: EASY**

- No allowlist of permitted hosts
- No IP address filtering (can access 169.254.169.254, localhost)
- Can probe internal services and cloud metadata endpoints

### VULN-02: A03 — Cross-Site Scripting (XSS)

**Severity:** High  
**Location:** `public/js/app.js:80-100` — `renderWidgets()`  
**Description:** Dashboard widget titles rendered via `innerHTML` without HTML encoding.

**Difficulty: EASY**

- Direct DOM injection with unsanitized user data
- Widget titles are attacker-controllable via POST /api/widgets
- Stored XSS executed when victim views dashboard

### VULN-03: A05 — Hardcoded API Keys in Client-Side Bundle

**Severity:** Medium  
**Location:** `public/js/app.js:1-10`  
**Description:** Internal reporting API keys hardcoded in client-side JavaScript, exposed to all end-users.

**Difficulty: VERY EASY**

- View page source or open DevTools to find keys
- Keys are plaintext strings in the JS bundle
- No server-side proxy for API calls

---

## Chained Attack: chain-01

**Chain Name:** SSRF to Cloud Metadata → Full Credential Response → IAM Key Exfiltration  
**Combined Impact:** Lateral Movement (Cloud Credential Theft)  
**Overall Chain Difficulty: EASY**

### Link 1: SSRF to Metadata Endpoint (A10 — Medium)

**Location:** `src/index.ts` — `POST /api/preview`  
**Description:** Fetches arbitrary URLs, including `http://169.254.169.254/latest/meta-data/iam/security-credentials/`

### Link 2: Full Response Body (A05 — Low)

**Location:** `src/index.ts` — `POST /api/preview`  
**Description:** Response truncation removed — full IAM credential payload (AccessKeyId, SecretAccessKey, Token) returned verbatim.

### Link 3: Debug Headers Leak (A05 — Low)

**Location:** `src/index.ts` — `GET /api/debug/headers`  
**Description:** Returns all request headers including internal proxy headers.

---

## Summary

App-11 is an Express-based analytics dashboard with a classic SSRF vulnerability and client-side API key exposure. The SSRF chain targeting cloud metadata is realistic and impactful. This app tests for cloud-aware vulnerability detection.

**Overall Difficulty Score:** 2/5 (Easy — SSRF and XSS are well-understood)