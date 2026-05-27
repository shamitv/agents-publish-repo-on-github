# OWASP Vulnerability Test Corpus

A collection of **50 intentionally vulnerable web applications** designed to benchmark AI agents that detect common security vulnerabilities (OWASP Top 10: 2021).

Each application simulates a realistic business system with **2–5 deliberately planted vulnerabilities**, along with safe code patterns to test agent precision.

---

## Languages & Frameworks

| Language | Count | Frameworks |
|----------|-------|------------|
| Python | 14 | Flask, Django, FastAPI |
| Java | 11 | Spring Boot |
| TypeScript | 10 | Express, NestJS |
| JavaScript | 15 | Express.js |

---

## OWASP Top 10: 2021 — Vulnerability Reference

| ID | Category | Description | Apps |
|----|----------|-------------|------|
| **A01** | Broken Access Control | IDOR, privilege escalation, missing authorization | 29 |
| **A02** | Cryptographic Failures | Plaintext secrets, weak hashing, unencrypted data | 16 |
| **A03** | Injection | SQL, NoSQL, XSS, OS command, LDAP injection | 25 |
| **A04** | Insecure Design | Missing rate limits, logic flaws, no threat modeling | 13 |
| **A05** | Security Misconfiguration | Default creds, debug mode, exposed endpoints | 17 |
| **A06** | Vulnerable & Outdated Components | Known-CVE libraries and frameworks | 6 |
| **A07** | Identification & Auth Failures | Weak passwords, session issues, missing MFA | 17 |
| **A08** | Software & Data Integrity Failures | Insecure deserialization, unsigned updates, no CSRF | 12 |
| **A09** | Security Logging & Monitoring Failures | Missing audit logs, no alerting | 12 |
| **A10** | Server-Side Request Forgery (SSRF) | Unvalidated server-side URL fetching | 11 |

---

## Application Index

### Python

| # | App Name | Domain | Vulnerabilities |
|---|----------|--------|-----------------|
| 01 | [E-Commerce Product Catalog API](apps/python/app-01-ecommerce-catalog/README.md) | Retail | A01, A03, A09 |
| 02 | [Healthcare Patient Portal](apps/python/app-02-patient-portal/README.md) | Healthcare | A01, A02, A07 |
| 03 | [Banking Transaction Service](apps/python/app-03-banking-service/README.md) | FinTech | A02, A03, A04 |
| 04 | [Real Estate Listing Platform](apps/python/app-04-real-estate/README.md) | Real Estate | A03, A05, A10 |
| 05 | [Online Learning Management System](apps/python/app-05-learning-mgmt/README.md) | Education | A01, A05, A08 |
| 21 | [Insurance Claims Processor](apps/python/app-21-insurance-claims/README.md) | Insurance | A01, A03, A09 |
| 22 | [Food Delivery Order System](apps/python/app-22-food-delivery/README.md) | Food & Beverage | A02, A04, A07 |
| 23 | [Government Permit Application Portal](apps/python/app-23-govt-permits/README.md) | Government | A01, A05, A08 |
| 24 | [Veterinary Clinic Management](apps/python/app-24-vet-clinic/README.md) | Veterinary | A02, A03, A09 |
| 25 | [Supply Chain Inventory Tracker](apps/python/app-25-supply-chain/README.md) | Logistics | A06, A07, A10 |
| 46 | [Charity Donation Platform](apps/python/app-46-charity-donations/README.md) | Non-Profit | A02, A03, A09 |
| 47 | [Smart Home Device Manager](apps/python/app-47-smart-home/README.md) | IoT | A05, A08, A10 |
| 48 | [Freelancer Marketplace](apps/python/app-48-freelancer-market/README.md) | Gig Economy | A01, A04, A07 |
| 49 | [Sports League Management](apps/python/app-49-sports-league/README.md) | Sports | A01, A03, A05 |

### Java

| # | App Name | Domain | Vulnerabilities |
|---|----------|--------|-----------------|
| 06 | [Enterprise HR Management System](apps/java/app-06-hr-management/README.md) | HR | A01, A02, A08 |
| 07 | [Airline Booking System](apps/java/app-07-airline-booking/README.md) | Travel | A03, A04, A07 |
| 08 | [Warehouse Management System](apps/java/app-08-warehouse-mgmt/README.md) | Logistics | A03, A05, A10 |
| 09 | [Legal Document Management](apps/java/app-09-legal-documents/README.md) | Legal | A01, A02, A06 |
| 10 | [Telecom Billing Platform](apps/java/app-10-telecom-billing/README.md) | Telecom | A01, A03, A04, A09 |
| 26 | [Pharmaceutical Drug Tracking](apps/java/app-26-pharma-tracking/README.md) | Pharma | A01, A02, A08 |
| 27 | [Hotel Reservation System](apps/java/app-27-hotel-reservation/README.md) | Hospitality | A03, A05, A07 |
| 28 | [Manufacturing Quality Control](apps/java/app-28-mfg-quality/README.md) | Manufacturing | A01, A04, A09 |
| 29 | [Vehicle Fleet Management](apps/java/app-29-fleet-management/README.md) | Transportation | A03, A06, A10 |
| 30 | [Auction Platform](apps/java/app-30-auction-platform/README.md) | E-Commerce | A04, A07, A08 |
| 50 | [Energy Utility Billing](apps/java/app-50-energy-billing/README.md) | Utilities | A01, A03, A05, A10 |

### TypeScript

| # | App Name | Domain | Vulnerabilities |
|---|----------|--------|-----------------|
| 11 | [Social Media Analytics Dashboard](apps/typescript/app-11-social-analytics/README.md) | Marketing | A01, A03, A05, A10 |
| 12 | [Crypto Wallet Service](apps/typescript/app-12-crypto-wallet/README.md) | FinTech | A02, A04, A07 |
| 13 | [Project Management Tool](apps/typescript/app-13-project-mgmt/README.md) | SaaS | A01, A03, A09 |
| 14 | [Telemedicine Appointment System](apps/typescript/app-14-telemedicine/README.md) | Telehealth | A01, A02, A07 |
| 15 | [Digital Asset Management](apps/typescript/app-15-digital-assets/README.md) | Media | A01, A08, A10 |
| 31 | [Event Ticketing Platform](apps/typescript/app-31-event-ticketing/README.md) | Entertainment | A03, A04, A07 |
| 32 | [Customer Support Ticket System](apps/typescript/app-32-support-tickets/README.md) | Customer Service | A01, A03, A05 |
| 33 | [Recruitment ATS Platform](apps/typescript/app-33-recruitment-ats/README.md) | HR Tech | A01, A02, A06 |
| 34 | [Subscription Box Service](apps/typescript/app-34-subscription-box/README.md) | Subscription | A03, A07, A09 |
| 35 | [Compliance Document Tracker](apps/typescript/app-35-compliance-tracker/README.md) | RegTech | A01, A05, A08 |

### JavaScript

| # | App Name | Domain | Vulnerabilities |
|---|----------|--------|-----------------|
| 16 | [Restaurant Review Platform](apps/javascript/app-16-restaurant-reviews/README.md) | Food & Hospitality | A01, A03, A07 |
| 17 | [IoT Device Dashboard](apps/javascript/app-17-iot-dashboard/README.md) | IoT | A02, A05, A10 |
| 18 | [Peer-to-Peer Lending Platform](apps/javascript/app-18-p2p-lending/README.md) | FinTech | A01, A02, A04 |
| 19 | [Content Management System](apps/javascript/app-19-cms/README.md) | Publishing | A03, A05, A08 |
| 20 | [Fitness Tracking API](apps/javascript/app-20-fitness-tracker/README.md) | Health & Wellness | A01, A06, A07 |
| 36 | [Parking Management System](apps/javascript/app-36-parking-mgmt/README.md) | Transportation | A03, A04, A09 |
| 37 | [Agricultural Crop Planner](apps/javascript/app-37-crop-planner/README.md) | Agriculture | A05, A06, A10 |
| 38 | [Museum Collection Catalog](apps/javascript/app-38-museum-catalog/README.md) | Arts & Culture | A01, A03, A09 |
| 39 | [Wedding Planning Platform](apps/javascript/app-39-wedding-planner/README.md) | Lifestyle | A01, A02, A07 |
| 40 | [Pet Adoption Portal](apps/javascript/app-40-pet-adoption/README.md) | Animal Welfare | A03, A05, A08 |
| 41 | [Library Book Reservation System](apps/javascript/app-41-library-reservation/README.md) | Public Services | A01, A03, A07 |
| 42 | [Construction Project Tracker](apps/javascript/app-42-construction-tracker/README.md) | Construction | A01, A08, A09 |
| 43 | [Music Streaming Playlist Service](apps/javascript/app-43-music-streaming/README.md) | Entertainment | A01, A05, A10 |
| 44 | [Election Polling System](apps/javascript/app-44-election-polling/README.md) | Civic Tech | A02, A04, A09 |
| 45 | [Corporate Travel & Expense System](apps/javascript/app-45-travel-expense/README.md) | Enterprise | A01, A03, A07 |

---

## Project Structure

```
owasp-test/
├── README.md                        # This file
├── docs/
│   ├── howto/sanitization.md        # How to produce scan-ready copies of any app
│   └── plans/                       # Expansion and run plans
├── apps/
│   ├── python/                      # 14 Python apps
│   ├── java/                        # 11 Java apps
│   ├── typescript/                  # 10 TypeScript apps
│   └── javascript/                  # 15 JavaScript apps
```

Each application contains:

```
app-NN-name/
├── README.md              # Setup instructions and app description
├── src/                   # Source code with planted vulnerabilities
├── tests/                 # Functional tests
├── config/                # Configuration files
├── .vulns                 # Ground truth vulnerability manifest
└── Dockerfile             # Containerized deployment
```

---

## Scoring

The ground truth for each application is stored in `.vulns`. An agent is evaluated on:

| Metric | Target | Description |
|--------|--------|-------------|
| **Recall** | ≥ 80% | Percentage of planted vulnerabilities detected |
| **Precision** | ≥ 70% | Percentage of reported findings that are true positives |
| **Coverage** | 10/10 | Number of OWASP categories with at least one detection |
| **Localization** | File + line | Accuracy of reported vulnerability location |

---

## License

This project is for **security research and education purposes only**. Do not deploy these applications in production environments.
