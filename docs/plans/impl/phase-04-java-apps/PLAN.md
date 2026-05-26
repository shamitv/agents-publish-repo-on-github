# Phase 4 — Java Apps Implementation (7 apps)

**Status:** 🔴 TODO  
**Language:** Java  
**Frameworks:** Spring Boot  
**Build Tool:** Maven (pom.xml)

---

## App-10: Telecom Billing System

**Domain:** Telecommunications  
**Difficulty Target:** ★★★★☆ Medium-Hard  
**Business Logic:** Customer account management, call detail records, invoice generation, payment processing

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on invoice PDF — `GET /api/invoices/{id}/download` without customer verification | ★☆☆☆☆ | Obvious |
| 2 | A03 | JNDI injection in customer import — Log4j `logger.info(importedName)` with attacker-controlled name | ★★★★★ | CVE-2021-44832 variant — subtle |
| 3 | A02 | Weak encryption of credit card numbers — AES-ECB with hardcoded key | ★★★☆☆ | ECB mode leaks patterns |
| 4 | A05 | Spring Actuator `/actuator/env` exposed without authentication | ★★☆☆☆ | Exposes environment variables |

### Chained Attack: JNDI Injection → RCE → Database Exfiltration

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Log4j JNDI injection via customer name field (Log4j 2.14.x pinned) | Medium | A03 |
| 2 | Actuator env endpoint leaks DB credentials | Low | A05 |

**Impact:** DB Exfiltration — RCE leads to credential extraction and database dump  
**Difficulty:** ★★★★★ Hard — requires exploiting Log4j JNDI lookup with crafted payload

### Decoys
- Properly escaped customer name display on other pages
- Parameterized queries in invoice search

---

## App-26: Pharmaceutical Tracking System

**Domain:** Pharma / Healthcare  
**Difficulty Target:** ★★★★★ Hard  
**Business Logic:** Drug batch tracking, expiration monitoring, supplier verification, recall management

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | BOLA on batch records — `GET /api/batches/{id}` returns data for any org | ★☆☆☆☆ | No org isolation |
| 2 | A03 | SQLi via Hibernate HQL concatenation — `session.createQuery("FROM Batch WHERE name='" + input + "'")` | ★★★☆☆ | Classic HQL injection |
| 3 | A06 | Vulnerable dependency — SnakeYAML 1.30 for batch YAML import | ★★★★☆ | CVE-2022-1471 — RCE via YAML |
| 4 | A09 | No audit log for batch disposition changes (quarantine/release) | ★★☆☆☆ | Supply chain integrity failure |

### Chained Attack: SnakeYAML Deserialization → RCE → Data Modification

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | SnakeYAML deserialization in batch import (1.30 is vulnerable) | Medium | A06 |
| 2 | No integrity checking on imported batch data | Medium | A08 |

**Impact:** Data Modification — attacker modifies drug batch records via RCE, leads to contaminated supply chain  
**Difficulty:** ★★★★★ Hard — requires crafting SnakeYAML deserialization payload + understanding pharma supply chain logic

### Decoys
- Proper XML parser with XXE protection on a different upload endpoint
- Input validation on batch number format that seems secure

---

## App-27: Hotel Reservation System

**Domain:** Hospitality  
**Difficulty Target:** ★★★☆☆ Medium  
**Business Logic:** Room booking, availability search, guest management, billing

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on booking details — `GET /api/bookings/{id}` exposes other guests' PII | ★☆☆☆☆ | Trivial |
| 2 | A03 | Stored XSS in guest feedback — stored and rendered unsanitized | ★★☆☆☆ | Classic |
| 3 | A07 | Session fixation — session ID accepted via URL parameter | ★★★☆☆ | `?sessionId=ABC123` in URL |

### Chained Attack: Session Fixation → XSS → Admin Session Hijack

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Session fixation — attacker sets victim's session ID | Medium | A07 |
| 2 | Stored XSS in guest feedback that steals cookie | Medium | A03 |

**Impact:** Account Takeover — admin session hijacked after viewing malicious feedback  
**Difficulty:** ★★★☆☆ Medium

### Decoys
- Proper session regeneration on login
- CSP header set but doesn't prevent inline scripts

---

## App-28: Manufacturing Quality Control

**Domain:** Manufacturing  
**Difficulty Target:** ★★★★☆ Medium-Hard  
**Business Logic:** Product inspection records, defect tracking, quality reports, equipment calibration

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on inspection records — view/edit any product's inspection data | ★☆☆☆☆ | No ownership |
| 2 | A05 | Spring Boot Actuator `/heapdump` exposed — download heap dump with secrets | ★★★★☆ | Subtle — requires knowing to download heap |
| 3 | A08 | Insecure deserialization via Java serialization in equipment config import | ★★★★☆ | `ObjectInputStream.readObject()` |
| 4 | A03 | H2 Console enabled in production — `/h2-console` with default creds | ★★★☆☆ | Exposes database |

### Chained Attack: Heapdump → JWT Secret Extraction → Data Modification

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Heapdump exposed via actuator leaks JWT signing secret | Medium | A05 |
| 2 | Insufficient logging on quality record modification | Low | A09 |

**Impact:** Data Modification — forge JWT as quality manager, alter inspection records to hide defects  
**Difficulty:** ★★★★☆ Medium-Hard — requires parsing heap dump for secrets

### Decoys
- Health endpoint properly secured with authentication
- H2 Console disabled in application.properties (but enabled in a profile-specific config)

---

## App-29: Fleet Management System

**Domain:** Logistics / Transportation  
**Difficulty Target:** ★★☆☆☆ Easy  
**Business Logic:** Vehicle tracking, driver assignments, fuel management, maintenance scheduling

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on driver records — view other drivers' personal info and routes | ★☆☆☆☆ | Trivial |
| 2 | A03 | SQLi in vehicle search — string concatenation in query | ★★☆☆☆ | Simple |
| 3 | A09 | No logging on fuel card assignment changes | ★☆☆☆☆ | Easy miss |

### Chained Attack: SQLi → Driver PII Extraction → Lateral Movement

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | SQL injection in vehicle search | Medium | A03 |
| 2 | IDOR on driver records exposes SSN and license numbers | Low | A01 |

**Impact:** DB Exfiltration — bulk driver PII including SSNs  
**Difficulty:** ★★☆☆☆ Easy

### Decoys
- Prepared statement in "secure" search endpoint
- Masked SSN display on UI (but full SSN in API response)

---

## App-30: Auction Platform

**Domain:** E-Commerce  
**Difficulty Target:** ★★★☆☆ Medium  
**Business Logic:** Item listings, bidding, auction timer, payment processing

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on bid history — view other users' max bids | ★☆☆☆☆ | Reveals proxy bids |
| 2 | A04 | Insecure design — auction timer checked client-side, bid accepted after expiry | ★★☆☆☆ | Bid after auction ends |
| 3 | A03 | SQLi in item search — `WHERE title LIKE '%{search}%'` | ★★☆☆☆ | Simple |
| 4 | A02 | Plaintext credit card storage in payment table | ★☆☆☆☆ | Obvious |

### Chained Attack: IDOR → Max Bid Exposure → Auction Manipulation

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | IDOR on bid history reveals other bidders' max amounts | Low | A01 |
| 2 | Client-side timer allows late bids | Medium | A04 |

**Impact:** Data Modification — attacker sees competitors' max bids, places winning bid $1 higher  
**Difficulty:** ★★★☆☆ Medium

### Decoys
- Server-side timer validation on "premium" auctions
- Tokenized payment storage that appears secure

---

## App-50: Energy Billing System

**Domain:** Utilities / Energy  
**Difficulty Target:** ★★☆☆☆ Easy  
**Business Logic:** Meter reading, bill calculation, customer invoices, payment tracking

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on meter readings — submit readings for any customer | ★☆☆☆☆ | Tamper billing |
| 2 | A03 | Stored XSS in customer feedback form | ★★☆☆☆ | Classic |
| 3 | A09 | No audit log on bill adjustments | ★☆☆☆☆ | Easy to miss |

### Chained Attack: IDOR → Bill Tampering → Fraud

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | IDOR allows submitting fake meter readings for any account | Medium | A01 |
| 2 | No logging of who modified readings | Low | A09 |

**Impact:** Data Modification — reduce energy bills, commit billing fraud  
**Difficulty:** ★★☆☆☆ Easy

### Decoys
- Role-based access on customer search endpoint
- Proper audit trail on payment processing

---

## Implementation Instructions

For each app:
1. Create Spring Boot project structure: `apps/java/app-XX-<name>/`
2. Create `pom.xml` with Spring Boot + dependencies (pinning vulnerable versions where needed)
3. Create `src/main/java/com/example/` with controllers, services, models
4. Create `src/main/resources/application.properties` (or `.yml`)
5. Create `.vulns` JSON manifest
6. Create `README.md` following the template
7. Create `reports/app-XX-<name>.md`