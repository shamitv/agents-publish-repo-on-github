# Implementation Plan — Secure Code Hunt

## Status Summary

All **50** application benchmark targets have been fully implemented across four languages (Python, Java, JavaScript, TypeScript). Each app includes:

- Complete runnable source code in `apps/<language>/app-<NN>-<name>/src/`
- A `README.md` with business domain, tech stack, features, and security benchmarking notes
- A `.vulns` machine-readable vulnerability manifest
- Project dependency files (`pom.xml`, `package.json`, `requirements.txt`, etc.)

Security reports have been generated for all **50** applications (see [Report Status](#report-status)).

---

## Delivery Summary

| # | App ID | App Name | Language | Framework | Vulns | Chains | Difficulty | Report |
|---|--------|----------|----------|-----------|-------|--------|------------|--------|
| 1 | app-01 | E-Commerce Catalog | Python | Flask | 3 | 1 | Hard | ✅ |
| 2 | app-02 | Patient Portal | Python | Flask | 3 | 1 | Medium | ✅ |
| 3 | app-03 | Banking Service | Python | Flask | 3 | 1 | Medium | ✅ |
| 4 | app-04 | Real Estate Platform | Python | Flask | 3 | 1 | Medium | ✅ |
| 5 | app-05 | Learning Management System | Python | Flask | 3 | 1 | Hard | ✅ |
| 6 | app-06 | HR Management | Java | Spring Boot | 3 | 1 | Medium | ✅ |
| 7 | app-07 | Airline Booking System | Java | Spring Boot | 3 | 1 | Easy | ✅ |
| 8 | app-08 | Warehouse Management | Java | Spring Boot | 3 | 1 | Easy | ✅ |
| 9 | app-09 | Legal Document Manager | Java | Spring Boot | 3 | 1 | Medium | ✅ |
| 10 | app-10 | Telecom Billing | Java | Spring Boot | 3 | 1 | Medium | ✅ |
| 11 | app-11 | Social Analytics | TypeScript | NestJS | 3 | 1 | Medium | ✅ |
| 12 | app-12 | Crypto Wallet | TypeScript | Express | 3 | 1 | Medium | ✅ |
| 13 | app-13 | Project Management | TypeScript | Express | 3 | 1 | Medium | ✅ |
| 14 | app-14 | Telemedicine | TypeScript | Express | 3 | 1 | Medium | ✅ |
| 15 | app-15 | Digital Assets Manager | TypeScript | Express | 3 | 1 | Medium | ✅ |
| 16 | app-16 | Restaurant Reviews | JavaScript | Express | 3 | 1 | Medium | ✅ |
| 17 | app-17 | IoT Device Dashboard | JavaScript | Express | 3 | 1 | Medium | ✅ |
| 18 | app-18 | P2P Lending Platform | JavaScript | Express | 3 | 1 | Easy | ✅ |
| 19 | app-19 | Content Management System | JavaScript | Express | 3 | 1 | Medium | ✅ |
| 20 | app-20 | Fitness Tracker | JavaScript | Express | 3 | 1 | Easy | ✅ |
| 21 | app-21 | Insurance Claims | Python | Flask | 3 | 1 | Medium | ✅ |
| 22 | app-22 | Food Delivery Order System | Python | FastAPI | 3 | 1 | Easy | ✅ |
| 23 | app-23 | Government Permits Portal | Python | Django | 3 | 1 | Medium | ✅ |
| 24 | app-24 | Veterinary Clinic | Python | FastAPI | 3 | 1 | Medium | ✅ |
| 25 | app-25 | Supply Chain Tracker | Python | Flask | 3 | 1 | Medium | ✅ |
| 26 | app-26 | Pharmaceutical Tracking | Java | Spring Boot | 3 | 1 | Hard | ✅ |
| 27 | app-27 | Hotel Reservation System | Java | Spring Boot | 3 | 1 | Medium | ✅ |
| 28 | app-28 | Manufacturing QC | Java | Spring Boot | 3 | 1 | Medium | ✅ |
| 29 | app-29 | Fleet Management | Java | Spring Boot | 3 | 1 | Hard | ✅ |
| 30 | app-30 | Auction Platform | Java | Spring Boot | 3 | 1 | Medium | ✅ |
| 31 | app-31 | Event Ticketing | TypeScript | Express | 3 | 1 | Medium | ✅ |
| 32 | app-32 | Support Ticket System | TypeScript | Express | 3 | 1 | Medium | ✅ |
| 33 | app-33 | Recruitment ATS | TypeScript | Express | 3 | 1 | Medium | ✅ |
| 34 | app-34 | Subscription Box Service | TypeScript | Express | 3 | 1 | Medium | ✅ |
| 35 | app-35 | Compliance Document Tracker | TypeScript | Express | 3 | 1 | Medium | ✅ |
| 36 | app-36 | Parking Management | JavaScript | Express | 3 | 1 | Medium | ✅ |
| 37 | app-37 | Crop Planner | JavaScript | Express | 3 | 1 | Medium | ✅ |
| 38 | app-38 | Museum Collection Catalog | JavaScript | Express | 3 | 1 | Medium | ✅ |
| 39 | app-39 | Wedding Planning Platform | JavaScript | Express | 3 | 1 | Easy | ✅ |
| 40 | app-40 | Pet Adoption Portal | JavaScript | Express | 3 | 1 | Medium | ✅ |
| 41 | app-41 | Library Reservation System | JavaScript | Express | 3 | 1 | Medium | ✅ |
| 42 | app-42 | Construction Tracker | JavaScript | Express | 3 | 1 | Medium | ✅ |
| 43 | app-43 | Music Streaming Service | JavaScript | Express | 3 | 1 | Medium | ✅ |
| 44 | app-44 | Election Polling System | JavaScript | Express | 3 | 1 | Easy | ✅ |
| 45 | app-45 | Travel & Expense System | JavaScript | Express | 3 | 1 | Medium | ✅ |
| 46 | app-46 | Charity Donation Platform | Python | Flask | 3 | 1 | Medium | ✅ |
| 47 | app-47 | Smart Home Device Manager | Python | FastAPI | 3 | 1 | Hard | ✅ |
| 48 | app-48 | Freelancer Marketplace | Python | FastAPI | 3 | 1 | Easy | ✅ |
| 49 | app-49 | Sports League Management | Python | Flask | 3 | 1 | Medium | ✅ |
| 50 | app-50 | Energy Utility Billing | Java | Spring Boot | 4 | 1 | Hard | ✅ |

**Total:** 50 apps (50 with reports)

---

## Language Breakdown

| Language | Count | Apps |
|----------|-------|------|
| Python | 14 | app-01–05, app-21–25, app-46–49 |
| Java | 11 | app-06–10, app-26–30, app-50 |
| JavaScript | 15 | app-16–20, app-36–45 |
| TypeScript | 10 | app-11–15, app-31–35 |

---

## OWASP Top 10: 2021 Coverage

| ID | Category | App Count |
|----|----------|-----------|
| A01 | Broken Access Control | 24 |
| A02 | Cryptographic Failures | 11 |
| A03 | Injection (SQL, XSS, LDAP, JPQL) | 23 |
| A04 | Insecure Design | 8 |
| A05 | Security Misconfiguration | 13 |
| A06 | Vulnerable & Outdated Components | 6 |
| A07 | Identification & Authentication Failures | 18 |
| A08 | Software & Data Integrity Failures | 10 |
| A09 | Security Logging & Monitoring Failures | 11 |
| A10 | Server-Side Request Forgery (SSRF) | 11 |

Every OWASP Top 10:2021 category is covered by at least 6 applications.

---

## Difficulty Distribution

| Difficulty | Count | Criteria |
|-----------|-------|----------|
| **Easy** | 8 | All vulnerabilities ≤ medium severity; simple 2-step chains or standard IDOR/SQLi patterns |
| **Medium** | 36 | Mix of high + medium severity vulns; standard 2-step chained attack scenarios |
| **Hard** | 6 | Critical-severity vulns (RCE, Log4Shell, insecure deserialization) or complex 3-step chains with lateral movement impact |

### Easy (8)
app-07 (Airline Booking), app-08 (Warehouse Mgmt), app-18 (P2P Lending), app-20 (Fitness Tracker), app-22 (Food Delivery), app-39 (Wedding Planner), app-44 (Election Polling), app-48 (Freelancer Marketplace)

### Hard (6)
app-01 (E-Commerce — pickle RCE), app-05 (LMS — pickle RCE), app-26 (Pharma — Java deserialization RCE), app-29 (Fleet — Log4Shell CVE-2021-44228), app-47 (Smart Home — 3-step firmware hijack chain), app-50 (Energy — SSRF → H2 console → DB exfil + SQLi)

---

## Chained Vulnerability Scenarios

Every application includes **≥ 1 chained vulnerability scenario** per the specification in [`AGENTS.md`](../../AGENTS.md). Chain impacts are distributed across all four required categories:

| Impact Category | App Count |
|----------------|-----------|
| `account_takeover` | 7 |
| `lateral_movement` | 8 |
| `db_exfiltration` | 14 |
| `data_modification` | 21 |

---

## Report Status

Security benchmark reports exist under `reports/` for the following apps:

| App | Report |
|-----|--------|
| app-01 E-Commerce Catalog | `reports/app-01-ecommerce-catalog.md` |
| app-02 Patient Portal | `reports/app-02-patient-portal.md` |
| app-03 Banking Service | `reports/app-03-banking-service.md` |
| app-04 Real Estate Platform | `reports/app-04-real-estate.md` |
| app-05 Learning Management System | `reports/app-05-learning-mgmt.md` |
| app-06 HR Management | `reports/app-06-hr-management.md` |
| app-07 Airline Booking | `reports/app-07-airline-booking.md` |
| app-08 Warehouse Management | `reports/app-08-warehouse-mgmt.md` |
| app-09 Legal Document Manager | `reports/app-09-legal-documents.md` |
| app-10 Telecom Billing | `reports/app-10-telecom-billing.md` |
| app-11 Social Analytics | `reports/app-11-social-analytics.md` |
| app-12 Crypto Wallet | `reports/app-12-crypto-wallet.md` |
| app-13 Project Management | `reports/app-13-project-mgmt.md` |
| app-14 Telemedicine | `reports/app-14-telemedicine.md` |
| app-15 Digital Assets Manager | `reports/app-15-digital-assets.md` |
| app-16 Restaurant Reviews | `reports/app-16-restaurant-reviews.md` |
| app-17 IoT Device Dashboard | `reports/app-17-iot-dashboard.md` |
| app-18 P2P Lending Platform | `reports/app-18-p2p-lending.md` |
| app-19 Content Management System | `reports/app-19-cms.md` |
| app-20 Fitness Tracker | `reports/app-20-fitness-tracker.md` |
| app-31 Event Ticketing | `reports/app-31-event-ticketing.md` |
| app-32 Support Ticket System | `reports/app-32-support-tickets.md` |
| app-33 Recruitment ATS | `reports/app-33-recruitment-ats.md` |
| app-34 Subscription Box Service | `reports/app-34-subscription-box.md` |
| app-35 Compliance Document Tracker | `reports/app-35-compliance-tracker.md` |
| app-36 Parking Management | `reports/app-36-parking-mgmt.md` |
| app-37 Crop Planner | `reports/app-37-crop-planner.md` |
| app-38 Museum Collection Catalog | `reports/app-38-museum-catalog.md` |
| app-39 Wedding Planning Platform | `reports/app-39-wedding-planner.md` |
| app-40 Pet Adoption Portal | `reports/app-40-pet-adoption.md` |
| app-41 Library Reservation System | `reports/app-41-library-reservation.md` |
| app-42 Construction Tracker | `reports/app-42-construction-tracker.md` |
| app-43 Music Streaming Service | `reports/app-43-music-streaming.md` |
| app-44 Election Polling System | `reports/app-44-election-polling.md` |
| app-45 Travel & Expense System | `reports/app-45-travel-expense.md` |
| app-21 Insurance Claims | `reports/app-21-insurance-claims.md` |
| app-22 Food Delivery | `reports/app-22-food-delivery.md` |
| app-23 Government Permits | `reports/app-23-govt-permits.md` |
| app-24 Veterinary Clinic | `reports/app-24-vet-clinic.md` |
| app-25 Supply Chain Tracker | `reports/app-25-supply-chain.md` |
| app-26 Pharmaceutical Tracking | `reports/app-26-pharma-tracking.md` |
| app-27 Hotel Reservation System | `reports/app-27-hotel-reservation.md` |
| app-28 Manufacturing QC | `reports/app-28-mfg-quality.md` |
| app-29 Fleet Management | `reports/app-29-fleet-management.md` |
| app-30 Auction Platform | `reports/app-30-auction-platform.md` |
| app-46 Charity Donation Platform | `reports/app-46-charity-donations.md` |
| app-47 Smart Home Device Manager | `reports/app-47-smart-home.md` |
| app-48 Freelancer Marketplace | `reports/app-48-freelancer-market.md` |
| app-49 Sports League Management | `reports/app-49-sports-league.md` |
| app-50 Energy Utility Billing | `reports/app-50-energy-billing.md` |

**All 50 reports are complete.**

---

## Next Steps

1. **Run agent benchmarks** — Execute security detection agents against each app and record results in the corresponding report.
2. **Triage findings** — Validate agent detection rates (true positives vs. false positives) and compute precision/recall per OWASP category.
3. **Target published reports** — Aggregate cross-app benchmark statistics and publish final results.

---

## Phased Implementation (Historical Reference)

The implementation was completed across the following phases:

| Phase | Apps | Scope | Status |
|-------|------|-------|--------|
| Phase 1 | app-01–04 | Python (Flask) + Reports | ✅ Complete |
| Phase 2 | app-05, app-21–25 | Python (Flask/FastAPI/Django) | ✅ Complete |
| Phase 3 | app-06–10 | Java (Spring Boot) + Reports | ✅ Complete |
| Phase 4 | app-11–15 | TypeScript (Express/NestJS) + Reports | ✅ Complete |
| Phase 5 | app-16–20 | JavaScript (Express) | ✅ Complete |
| Phase 6 | app-26–30, app-50 | Java (Spring Boot) | ✅ Complete |
| Phase 7 | app-31–35 | TypeScript (Express) | ✅ Complete |
| Phase 8 | app-36–45 | JavaScript (Express) | ✅ Complete |
| Phase 9 | app-46–49 | Python (Flask/FastAPI) | ✅ Complete |

---

## Technical Notes

- Apps follow the conventions defined in [`AGENTS.md`](../../AGENTS.md) for vulnerability annotation, chained scenarios, and decoy placement.
- The `.vulns` JSON manifests are machine-readable and schema-validated.
- All apps use mock/in-memory databases — no external infrastructure is required.
- Decoy safe patterns are documented in each app's `.vulns` under the `"decoys"` array.