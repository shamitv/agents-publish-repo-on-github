# Secure Code Hunt — Audit Reports

This directory contains security audit reports for all **50 intentionally vulnerable applications** in the **secure-code-hunt** benchmark.

---

## Repository Overview

**Purpose:** An intentionally vulnerable application corpus for benchmarking AI security-detection agents against OWASP Top 10: 2021.

| Metric | Value |
|--------|-------|
| **Total Apps** | **50** |
| **Python apps** | 14 (Django, FastAPI, Flask) |
| **Java apps** | 11 (Spring Boot) |
| **TypeScript apps** | 10 (Express, NestJS) |
| **JavaScript apps** | 15 (Express) |
| **Standalone vulns per app** | 3–5 |
| **Chained attacks per app** | 1–2 |
| **Total exploit chains** | 92 |

---

## Completed Audit Reports

| # | App | Language | Framework | Vulns | Chains |
|---|-----|----------|-----------|-------|--------|
| 1 | E-Commerce Product Catalog API | python | flask | 3 | 1 |
| 2 | Healthcare Patient Portal | python | django | 3 | 2 |
| 3 | Banking Transaction Service | python | fastapi | 3 | 2 |
| 4 | Real Estate Listing Platform | python | flask | 3 | 2 |
| 5 | Online Learning Management System | python | flask | 3 | 1 |
| 6 | Enterprise HR Management System | java | spring-boot | 4 | 1 |
| 7 | Airline Booking System | java | spring-boot | 3 | 2 |
| 8 | Warehouse Management System | java | spring-boot | 3 | 2 |
| 9 | Legal Document Management | java | spring-boot | 3 | 2 |
| 10 | Telecom Billing Platform | java | spring-boot | 5 | 1 |
| 11 | Social Media Analytics Dashboard | typescript | express | 5 | 1 |
| 12 | Crypto Wallet Service | typescript | nestjs | 3 | 2 |
| 13 | Project Management Tool | typescript | express | 3 | 2 |
| 14 | Telemedicine Appointment System | typescript | express | 4 | 1 |
| 15 | Digital Asset Management | typescript | express | 3 | 2 |
| 16 | Restaurant Review Platform | javascript | express | 3 | 2 |
| 17 | IoT Device Dashboard | javascript | express | 4 | 1 |
| 18 | Peer-to-Peer Lending Platform | javascript | express | 3 | 2 |
| 19 | Content Management System | javascript | express | 3 | 2 |
| 20 | Fitness Tracking API | javascript | express | 3 | 2 |
| 21 | Insurance Claims Processor | python | flask | 3 | 2 |
| 22 | Food Delivery Order System | python | fastapi | 3 | 2 |
| 23 | Government Permit Application Portal | python | django | 3 | 2 |
| 24 | Veterinary Clinic Management | python | fastapi | 3 | 2 |
| 25 | Supply Chain Inventory Tracker | python | flask | 3 | 2 |
| 26 | Pharmaceutical Drug Tracking | java | spring-boot | 3 | 2 |
| 27 | Hotel Reservation System | java | spring-boot | 3 | 2 |
| 28 | Manufacturing Quality Control | java | spring-boot | 3 | 2 |
| 29 | Vehicle Fleet Management | java | spring-boot | 3 | 2 |
| 30 | Auction Platform | java | spring-boot | 3 | 2 |
| 31 | Event Ticketing Platform | typescript | express | 3 | 2 |
| 32 | Customer Support Ticket System | typescript | express | 3 | 2 |
| 33 | Recruitment ATS Platform | typescript | express | 3 | 2 |
| 34 | Subscription Box Service | typescript | express | 3 | 2 |
| 35 | Compliance Document Tracker | typescript | express | 3 | 2 |
| 36 | Parking Management System | javascript | express | 3 | 1 |
| 37 | Agricultural Crop Planner | javascript | express | 3 | 2 |
| 38 | Museum Collection Catalog | javascript | express | 3 | 2 |
| 39 | Wedding Planning Platform | javascript | express | 3 | 2 |
| 40 | Pet Adoption Portal | javascript | express | 3 | 2 |
| 41 | Library Book Reservation System | javascript | express | 3 | 2 |
| 42 | Construction Project Tracker | javascript | express | 3 | 2 |
| 43 | Music Streaming Playlist Service | javascript | express | 3 | 2 |
| 44 | Election Polling System | javascript | express | 3 | 2 |
| 45 | Corporate Travel & Expense System | javascript | express | 3 | 2 |
| 46 | Charity Donation Platform | python | flask | 3 | 2 |
| 47 | Smart Home Device Manager | python | fastapi | 3 | 2 |
| 48 | Freelancer Marketplace | python | fastapi | 3 | 2 |
| 49 | Sports League Management | python | flask | 3 | 2 |
| 50 | Energy Utility Billing | java | spring-boot | 4 | 2 |

---

## OWASP Coverage

| OWASP ID | Category | Apps with This Vuln |
|----------|----------|---------------------|
| A01 | Broken Access Control | 29 apps — 01, 02, 05, 06, 09, 10, 11, 13, 14, 15, 16, 18, 20, 21, 23, 26, 28, 32, 33, 35, 38, 39, 41, 42, 43, 45, 48, 49, 50 |
| A02 | Cryptographic Failures | 15 apps — 02, 03, 06, 09, 12, 14, 17, 18, 22, 24, 26, 33, 39, 44, 46 |
| A03 | Injection | 25 apps — 01, 03, 04, 07, 08, 10, 11, 13, 16, 19, 21, 24, 27, 29, 31, 32, 34, 36, 38, 40, 41, 45, 46, 49, 50 |
| A04 | Insecure Design | 12 apps — 03, 07, 10, 12, 18, 22, 28, 30, 31, 36, 44, 48 |
| A05 | Security Misconfiguration | 16 apps — 04, 05, 08, 11, 17, 19, 23, 27, 32, 35, 37, 40, 43, 47, 49, 50 |
| A06 | Vulnerable/Outdated Components | 6 apps — 09, 20, 25, 29, 33, 37 |
| A07 | Identification/Auth Failures | 16 apps — 02, 07, 12, 14, 16, 20, 22, 25, 27, 30, 31, 34, 39, 41, 45, 48 |
| A08 | Software/Data Integrity | 11 apps — 05, 06, 15, 19, 23, 26, 30, 35, 40, 42, 47 |
| A09 | Security Logging Failures | 12 apps — 01, 10, 13, 21, 24, 28, 34, 36, 38, 42, 44, 46 |
| A10 | Server-Side Request Forgery | 11 apps — 04, 08, 11, 15, 17, 25, 29, 37, 43, 47, 50 |

All 10 OWASP Top 10:2021 categories are covered across the 50 apps.

---

## Chained Attack Coverage

| Impact | Apps with This Chain Type |
|--------|--------------------------|
| Account Takeover | 11 apps — 07, 13, 19, 27, 31, 34, 35, 40, 41, 42, 48 |
| Data Modification | 16 apps — 01, 03, 08, 10, 12, 16, 21, 22, 24, 26, 28, 30, 33, 36, 44, 49 |
| Database Exfiltration | 12 apps — 02, 05, 06, 14, 18, 20, 32, 38, 39, 45, 46, 50 |
| Lateral Movement | 11 apps — 04, 09, 11, 15, 17, 23, 25, 29, 37, 43, 47 |

---

## Difficulty Breakdown

| Level | Rating | Apps |
|-------|--------|------|
| Easy | 8 apps | 07, 08, 18, 20, 22, 39, 44, 48 |
| Medium | 36 apps | 02, 03, 04, 06, 09, 10, 11, 12, 13, 14, 15, 16, 17, 19, 21, 23, 24, 25, 27, 28, 30, 31, 32, 33, 34, 35, 36, 37, 38, 40, 41, 42, 43, 45, 46, 49 |
| Hard | 6 apps | 01, 05, 26, 29, 47, 50 |

Each report's `Difficulty` column links to the individual report file for detailed analysis.

---

## Methodology

Each report follows this structure:
- **Standalone vulnerabilities** — OWASP category, severity, location, exploitation difficulty
- **Chained attack** — Step-by-step chain of low/medium issues reaching high-impact outcome
- **Difficulty rating** — Easy, Medium, or Hard based on required exploit knowledge and complexity

Vulnerability detection agents should be able to identify all issues listed without fixing them (per AGENTS.md rules). Decoy safe patterns are intentionally placed near vulnerable code to measure agent precision (false-positive rate).
