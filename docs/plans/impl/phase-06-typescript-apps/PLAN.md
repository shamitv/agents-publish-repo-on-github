# Phase 6 — TypeScript Apps Implementation (7 apps)

**Status:** 🔴 TODO  
**Language:** TypeScript  
**Frameworks:** Express.js, NestJS  
**Template Engine:** EJS / Handlebars

---

## App-14: Telemedicine Platform

**Domain:** Healthcare  
**Difficulty Target:** ★★★★☆ Medium-Hard  
**Framework:** Express + TypeScript  
**Business Logic:** Patient registration, appointment scheduling, video consultation, prescription management

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on medical records — `GET /api/patients/:id/records` without doctor verification | ★☆☆☆☆ | Obvious IDOR |
| 2 | A02 | Hardcoded API key for third-party pharmacy service in source | ★☆☆☆☆ | Plaintext in config |
| 3 | A03 | SQLi in patient search — raw query `WHERE name LIKE '%${query}%'` | ★★☆☆☆ | Simple injection |
| 4 | A07 | JWT stored in localStorage with no httpOnly — readable by XSS | ★★★☆☆ | Cookie misconfig |

### Chained Attack: XSS via Poor Config → localStorage JWT Steal → Account Takeover

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | JWT in localStorage (not httpOnly cookie) allows XSS theft | Medium | A07 |
| 2 | IDOR on prescription endpoint allows viewing any patient's meds | Medium | A01 |

**Impact:** DB Exfiltration — steal doctor's JWT via XSS, access all patient records  
**Difficulty:** ★★★★☆ Medium-Hard

### Decoys
- Proper JWT cookie on a "secure" route
- Helmet.js security headers partially configured

---

## App-15: Digital Asset Vault

**Domain:** FinTech / Security  
**Difficulty Target:** ★★★★★ Hard  
**Framework:** NestJS  
**Business Logic:** Asset storage, permission management, sharing, activity log

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | Broken object-level authorization — `@UseGuards(AuthGuard)` missing on specific routes | ★★☆☆☆ | Missing guard on some routes |
| 2 | A02 | Weak encryption of asset files — AES-ECB mode with hardcoded key | ★★★☆☆ | ECB pattern leak |
| 3 | A05 | CORS misconfiguration — `origin: '*'` on asset-sharing endpoint | ★★☆☆☆ | |
| 4 | A08 | Insecure deserialization via class-transformer — `plainToClass` with user input | ★★★★★ | Hidden in NestJS DTO validation |

### Chained Attack: Insecure Deserialization → RCE → Asset Exfiltration

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Insecure deserialization via `class-transformer` with crafted JSON | Medium | A08 |
| 2 | CORS allows exfiltration to attacker origin | Low | A05 |

**Impact:** DB Exfiltration — RCE leads to all digital assets being stolen  
**Difficulty:** ★★★★★ Hard — requires crafting exploit for NestJS class-transformer deserialization

### Decoys
- CORS restricted on most endpoints except one "sharing" endpoint
- Proper auth guard on most routes except one forgotten route

---

## App-31: Event Ticketing System

**Domain:** Events / Entertainment  
**Difficulty Target:** ★★☆☆☆ Easy  
**Framework:** Express + TypeScript  
**Business Logic:** Event listings, ticket purchasing, seat selection, order history

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on order history — view anyone's tickets | ★☆☆☆☆ | Trivial |
| 2 | A03 | Stored XSS in event description — rendered unsanitized | ★★☆☆☆ | |
| 3 | A09 | No logging of ticket transfers (selling to others) | ★☆☆☆☆ | Easy miss |

### Chained Attack: XSS → Ticket Theft → Account Takeover

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Stored XSS in event description | Medium | A03 |
| 2 | Session cookie lacks httpOnly flag | Low | A05 |

**Impact:** Account Takeover  
**Difficulty:** ★★☆☆☆ Easy

---

## App-32: IT Support Ticketing

**Domain:** Enterprise / IT  
**Difficulty Target:** ★★★☆☆ Medium  
**Framework:** NestJS  
**Business Logic:** Ticket creation, assignment, escalation, knowledge base

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on tickets — view other users' support tickets | ★☆☆☆☆ | |
| 2 | A03 | SQLi in ticket search | ★★☆☆☆ | |
| 3 | A05 | Directory traversal in attachment download | ★★★☆☆ | |
| 4 | A09 | No audit for ticket status changes (who escalated/closed) | ★☆☆☆☆ | |

### Chained Attack: Directory Traversal → Config Read → DB Credentials

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Directory traversal in attachment download | Medium | A05 |
| 2 | NestJS config file readable via traversal contains DB password | Low | A05 |

**Impact:** Lateral Movement — extracted DB credentials  
**Difficulty:** ★★★☆☆ Medium

---

## App-33: Recruitment ATS

**Domain:** HR / Recruitment  
**Difficulty Target:** ★★★★☆ Medium-Hard  
**Framework:** Express + TypeScript  
**Business Logic:** Job postings, applications, resume parsing, interview scheduling

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on applications — view other candidates' resumes and cover letters | ★☆☆☆☆ | |
| 2 | A03 | SSTI in email templates — `ejs.render(template, { name })` with user name | ★★★★☆ | Hidden in hiring email |
| 3 | A05 | Unrestricted file upload on resumes — upload executable files | ★★☆☆☆ | |
| 4 | A02 | Plaintext salary data in API responses | ★☆☆☆☆ | |

### Chained Attack: SSTI in Email → RCE → Bulk Resume Extraction

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | SSTI via user name in hiring email template | Medium | A03 |
| 2 | IDOR allows viewing all candidates' resumes | Low | A01 |

**Impact:** DB Exfiltration — RCE leads to extracting all candidate PII from database  
**Difficulty:** ★★★★☆ Medium-Hard — SSTI is in email template, not obvious from endpoints

---

## App-34: Subscription Box Service

**Domain:** E-Commerce  
**Difficulty Target:** ★★☆☆☆ Easy  
**Framework:** Express + TypeScript  
**Business Logic:** Subscription plans, box curation, shipping, billing

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on subscription details — view/edit any user's subscription | ★☆☆☆☆ | |
| 2 | A03 | Stored XSS in product reviews | ★★☆☆☆ | |
| 3 | A09 | No logging on address changes | ★☆☆☆☆ | |

### Chained Attack: IDOR → Address Change → Package Theft

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | IDOR on subscription management | Medium | A01 |
| 2 | No audit/fraud detection on address changes | Low | A09 |

**Impact:** Account Takeover — change victim's shipping address, steal their subscription box  
**Difficulty:** ★★☆☆☆ Easy

---

## App-35: Compliance Tracking System

**Domain:** Legal / Enterprise  
**Difficulty Target:** ★★★☆☆ Medium  
**Framework:** NestJS  
**Business Logic:** Regulation tracking, audit logs, report generation, policy management

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on audit logs — view other orgs' compliance audit data | ★☆☆☆☆ | |
| 2 | A03 | SQLi in report generation — dynamic query building | ★★☆☆☆ | |
| 3 | A05 | Sensitive data exposure via error messages — `Error: ${err.stack}` returned to user | ★★☆☆☆ | Stack trace leak |
| 4 | A07 | Weak password policy — no complexity requirements, no rate limiting | ★☆☆☆☆ | |

### Chained Attack: SQLi → Audit Log Manipulation → Compliance Cover-Up

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | SQL injection in report generator | Medium | A03 |
| 2 | IDOR on audit log endpoints allows modifying/deleting logs | Low | A01 |

**Impact:** Data Modification — attacker alters audit logs to hide compliance violations  
**Difficulty:** ★★★☆☆ Medium

---

## Implementation Instructions

For each app:
1. Create directory: `apps/typescript/app-XX-<name>/`
2. Create `package.json` with Express/NestJS + TypeScript dependencies
3. Create `tsconfig.json`
4. Create `src/` with routes/controllers, services, models
5. Create `src/views/` for EJS templates (if using Express)
6. Create `.vulns` JSON manifest
7. Create `README.md` following the template
8. Create `reports/app-XX-<name>.md`