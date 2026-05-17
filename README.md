# OWASP Vulnerability Test Corpus

A collection of **50 intentionally vulnerable web applications** designed to benchmark AI agents that detect common security vulnerabilities (OWASP Top 10: 2021).

Each application simulates a realistic business system with **2–4 deliberately planted vulnerabilities**, along with safe code patterns to test agent precision.

---

## Languages & Frameworks

| Language | Count | Frameworks |
|----------|-------|------------|
| Python | 14 | Flask, Django, FastAPI |
| Java | 13 | Spring Boot |
| TypeScript | 12 | Express, NestJS |
| JavaScript | 11 | Express.js |

---

## OWASP Top 10: 2021 — Vulnerability Reference

| ID | Category | Description | Apps |
|----|----------|-------------|------|
| **A01** | Broken Access Control | IDOR, privilege escalation, missing authorization | 28 |
| **A02** | Cryptographic Failures | Plaintext secrets, weak hashing, unencrypted data | 14 |
| **A03** | Injection | SQL, NoSQL, XSS, OS command, LDAP injection | 20 |
| **A04** | Insecure Design | Missing rate limits, logic flaws, no threat modeling | 10 |
| **A05** | Security Misconfiguration | Default creds, debug mode, exposed endpoints | 14 |
| **A06** | Vulnerable & Outdated Components | Known-CVE libraries and frameworks | 6 |
| **A07** | Identification & Auth Failures | Weak passwords, session issues, missing MFA | 14 |
| **A08** | Software & Data Integrity Failures | Insecure deserialization, unsigned updates, no CSRF | 10 |
| **A09** | Security Logging & Monitoring Failures | Missing audit logs, no alerting | 11 |
| **A10** | Server-Side Request Forgery (SSRF) | Unvalidated server-side URL fetching | 10 |

---

## Application Index

### Python

| # | App Name | Domain | Vulnerabilities |
|---|----------|--------|-----------------|
| 01 | [E-Commerce Product Catalog API](apps/python/app-01-ecommerce-catalog/README.md) | Retail | A01, A03, A09 |
| 02 | [Healthcare Patient Portal](apps/python/app-02-patient-portal/README.md) | Healthcare | A01, A02, A07 |
| 03 | [Banking Transaction Service](apps/python/app-03-banking-service/README.md) | FinTech | A02, A03, A04 |
| 04 | [Real Estate Listing Platform](apps/python/app-04-real-estate/README.md) | Real Estate | A03, A05, A10 |
| 05 | Online Learning Management System | Education | A01, A05, A08 |
| 21 | Insurance Claims Processor | Insurance | A01, A03, A09 |
| 22 | Food Delivery Order System | Food & Beverage | A02, A04, A07 |
| 23 | Government Permit Application Portal | Government | A01, A05, A08 |
| 24 | Veterinary Clinic Management | Veterinary | A02, A03, A09 |
| 25 | Supply Chain Inventory Tracker | Logistics | A06, A07, A10 |
| 46 | Charity Donation Platform | Non-Profit | A02, A03, A09 |
| 47 | Smart Home Device Manager | IoT | A05, A08, A10 |
| 48 | Freelancer Marketplace | Gig Economy | A01, A04, A07 |
| 49 | Sports League Management | Sports | A01, A03, A05 |

### Java

| # | App Name | Domain | Vulnerabilities |
|---|----------|--------|-----------------|
| 06 | [Enterprise HR Management System](apps/java/app-06-hr-management/README.md) | HR | A01, A02, A08 |
| 07 | [Airline Booking System](apps/java/app-07-airline-booking/README.md) | Travel | A03, A04, A07 |
| 08 | [Warehouse Management System](apps/java/app-08-warehouse-mgmt/README.md) | Logistics | A03, A05, A10 |
| 09 | [Legal Document Management](apps/java/app-09-legal-documents/README.md) | Legal | A01, A02, A06 |
| 10 | Telecom Billing Platform | Telecom | A03, A04, A09 |
| 26 | Pharmaceutical Drug Tracking | Pharma | A01, A02, A08 |
| 27 | Hotel Reservation System | Hospitality | A03, A05, A07 |
| 28 | Manufacturing Quality Control | Manufacturing | A01, A04, A09 |
| 29 | Vehicle Fleet Management | Transportation | A03, A06, A10 |
| 30 | Auction Platform | E-Commerce | A04, A07, A08 |
| 50 | Energy Utility Billing | Utilities | A01, A03, A05, A10 |

### TypeScript

| # | App Name | Domain | Vulnerabilities |
|---|----------|--------|-----------------|
| 11 | [Social Media Analytics Dashboard](apps/typescript/app-11-social-analytics/README.md) | Marketing | A03, A05, A10 |
| 12 | [Crypto Wallet Service](apps/typescript/app-12-crypto-wallet/README.md) | FinTech | A02, A04, A07 |
| 13 | Project Management Tool | SaaS | A01, A03, A09 |
| 14 | Telemedicine Appointment System | Telehealth | A01, A02, A07 |
| 15 | Digital Asset Management | Media | A01, A08, A10 |
| 31 | Event Ticketing Platform | Entertainment | A03, A04, A07 |
| 32 | Customer Support Ticket System | Customer Service | A01, A03, A05 |
| 33 | Recruitment ATS | HR Tech | A01, A02, A06 |
| 34 | Subscription Box Service | Subscription | A03, A07, A09 |
| 35 | Compliance Document Tracker | RegTech | A01, A05, A08 |

### JavaScript

| # | App Name | Domain | Vulnerabilities |
|---|----------|--------|-----------------|
| 16 | Restaurant Review Platform | Food & Hospitality | A01, A03, A07 |
| 17 | IoT Device Dashboard | IoT | A02, A05, A10 |
| 18 | Peer-to-Peer Lending Platform | FinTech | A01, A02, A04 |
| 19 | Content Management System | Publishing | A03, A05, A08 |
| 20 | Fitness Tracking API | Health & Wellness | A01, A06, A07 |
| 36 | Parking Management System | Transportation | A03, A04, A09 |
| 37 | Agricultural Crop Planner | Agriculture | A05, A06, A10 |
| 38 | Museum Collection Catalog | Arts & Culture | A01, A03, A09 |
| 39 | Wedding Planning Platform | Lifestyle | A01, A02, A07 |
| 40 | Pet Adoption Portal | Animal Welfare | A03, A05, A08 |
| 41 | Library Book Reservation System | Public Services | A01, A03, A07 |
| 42 | Construction Project Tracker | Construction | A01, A08, A09 |
| 43 | Music Streaming Playlist Service | Entertainment | A01, A05, A10 |
| 44 | Election Polling System | Civic Tech | A02, A04, A09 |
| 45 | Corporate Travel & Expense | Enterprise | A01, A03, A07 |

---

## Project Structure

```
owasp-test/
├── README.md                        # This file
├── docs/plans/initial/plan.md       # Master implementation plan
├── apps/
│   ├── python/                      # 14 Python apps
│   ├── java/                        # 13 Java apps
│   ├── typescript/                  # 12 TypeScript apps
│   └── javascript/                  # 15 JavaScript apps
```

Each application contains:

```
app-NN-name/
├── README.md              # Setup instructions and app description
├── src/                   # Source code with planted vulnerabilities
├── tests/                 # Functional tests
├── config/                # Configuration files
├── vulnerabilities.json   # Ground truth vulnerability manifest
└── Dockerfile             # Containerized deployment
```

---

## Scoring

The ground truth for each application is stored in `vulnerabilities.json`. An agent is evaluated on:

| Metric | Target | Description |
|--------|--------|-------------|
| **Recall** | ≥ 80% | Percentage of planted vulnerabilities detected |
| **Precision** | ≥ 70% | Percentage of reported findings that are true positives |
| **Coverage** | 10/10 | Number of OWASP categories with at least one detection |
| **Localization** | File + line | Accuracy of reported vulnerability location |

---

## License

This project is for **security research and education purposes only**. Do not deploy these applications in production environments.
