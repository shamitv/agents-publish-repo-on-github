# Secure Code Hunt — Audit Reports

This directory contains security audit reports for all intentionally vulnerable applications in the **secure-code-hunt** benchmark.

---

## Repository Overview

**Purpose:** An intentionally vulnerable application corpus for benchmarking AI security-detection agents against OWASP Top 10: 2021.

**Total Apps (planned):** 50  
**Apps with source code:** 11  
**Languages:** Python (4 apps), Java (4 apps), TypeScript (3 apps)  
**Scaffold-only apps:** 39 (app-05, app-10, app-14 through app-50)

---

## Completed Audit Reports

| # | App | Language | Framework | Standalone Vulns | Chained Attacks | Difficulty |
|---|-----|----------|-----------|-----------------|-----------------|------------|
| 1 | E-Commerce Catalog | Python | Flask | 4 (IDOR, SQLi, XSS, Info Leak) | 1 | Medium |
| 2 | Patient Portal | Python | Flask | 3 (IDOR, Mass Assignment, SQLi) | 1 | Easy-Medium |
| 3 | Banking Service | Python | Flask | 4 (BOLA, NoSQLi, XSS, Crypto) | 1 | Medium |
| 4 | Real Estate | Python | Flask | 3 (IDOR, Path Traversal, XSS) | 1 | Medium |
| 6 | HR Management | Java | Spring Boot | 3 (IDOR, Deserialization, XOR Crypto) | 1 | Medium |
| 7 | Airline Booking | Java | Spring Boot | 3 (SQLi, Session Fixation, Design Flaw) | 1 | Easy-Medium |
| 8 | Warehouse Mgmt | Java | Spring Boot | 3 (Actuator, LDAPi, SSRF) | 1 | Medium-Hard |
| 9 | Legal Documents | Java | Spring Boot | 3 (IDOR, Plaintext, Log4Shell) | 1 | Easy |
| 11 | Social Analytics | TypeScript | Express | 3 (SSRF, XSS, Hardcoded Keys) | 1 | Easy |
| 12 | Crypto Wallet | TypeScript | NestJS | 3 (Plaintext Keys, No Confirmation, No MFA) | 1 | Very Easy |
| 13 | Project Mgmt | TypeScript | Express | 3 (IDOR, XSS, No Audit Logging) | 1 | Easy |

---

## OWASP Coverage

| OWASP ID | Category | Apps with This Vuln |
|----------|----------|---------------------|
| A01 | Broken Access Control | 01, 02, 03, 04, 06, 07, 08, 09, 12, 13 |
| A02 | Cryptographic Failures | 03, 06, 09, 12 |
| A03 | Injection | 01, 02, 03, 04, 07, 08, 11, 13 |
| A04 | Insecure Design | 03, 07, 10* |
| A05 | Security Misconfiguration | 08, 11 |
| A06 | Vulnerable/Outdated Components | 09 |
| A07 | Identification/Auth Failures | 07, 12 |
| A08 | Software/Data Integrity | 06 |
| A09 | Security Logging Failures | 13 |
| A10 | Server-Side Request Forgery | 08, 11 |

\* app-05 (python), app-10 (typescript), app-14–50 are scaffold-only (empty directories)

---

## Chained Attack Coverage

| Impact | Apps with This Chain Type |
|--------|--------------------------|
| Account Takeover | 03, 07, 13 |
| Database Exfiltration | 01*, 06* |
| Data Modification | 08, 12 |
| Lateral Movement | 09, 11 |

\* Chained attacks present in these apps

---

## Difficulty Breakdown

| Level | Rating | Apps |
|-------|--------|------|
| 1 | Very Easy | 12 |
| 2 | Easy | 03, 09, 11, 13 |
| 3 | Easy-Medium | 02, 07 |
| 4 | Medium | 01, 04, 06 |
| 5 | Medium-Hard | 08 |

---

## Methodology

Each report follows this structure:
- **Standalone vulnerabilities** — OWASP category, severity, location, exploitation difficulty
- **Chained attack** — Step-by-step chain of low/medium issues reaching high-impact outcome
- **Difficulty rating** — 1 (Very Easy) to 5 (Very Hard) based on required exploit knowledge

Vulnerability detection agents should be able to identify all issues listed without fixing them (per AGENTS.md rules).