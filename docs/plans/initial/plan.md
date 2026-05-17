# OWASP Vulnerability Test Applications — Master Plan

## Objective

Create 50 intentionally vulnerable web applications spanning diverse business domains and languages (Java, Python, TypeScript, JavaScript). These applications serve as a test corpus for an AI agent that detects OWASP Top 10 (2021) vulnerabilities.

Each application will contain **2–4 deliberately planted vulnerabilities** from the OWASP Top 10, along with realistic business logic to ensure the agent must distinguish real vulnerabilities from safe patterns.

---

## OWASP Top 10: 2021 — Reference

| ID | Category | Short Description |
|----|----------|-------------------|
| A01 | Broken Access Control | Missing or improper authorization checks |
| A02 | Cryptographic Failures | Weak encryption, plaintext secrets, poor key management |
| A03 | Injection | SQL, NoSQL, OS command, LDAP, XSS injection |
| A04 | Insecure Design | Architectural/design flaws, missing threat modeling |
| A05 | Security Misconfiguration | Default creds, verbose errors, open cloud storage |
| A06 | Vulnerable & Outdated Components | Known-vulnerable libraries/frameworks |
| A07 | Identification & Authentication Failures | Weak passwords, broken session management |
| A08 | Software & Data Integrity Failures | Insecure deserialization, unsigned updates, CI/CD flaws |
| A09 | Security Logging & Monitoring Failures | Missing audit trails, no alerting |
| A10 | Server-Side Request Forgery (SSRF) | Unvalidated URL fetching from server side |

---

## Language Distribution

| Language | Count | App IDs |
|----------|-------|---------|
| Python | 14 | 1–5, 21–25, 46–49 |
| Java | 13 | 6–10, 26–30, 50 |
| TypeScript | 12 | 11–15, 31–35 |
| JavaScript | 11 | 16–20, 36–40, 41–45 |

---

## Application Index

### Python Applications (14)

#### App 01 — E-Commerce Product Catalog API
- **Domain:** Retail / E-Commerce
- **Framework:** Flask
- **Description:** REST API for browsing products, managing carts, and processing orders.
- **Vulnerabilities:** A01 (IDOR on order details), A03 (SQL injection in product search), A09 (no audit logging)

#### App 02 — Healthcare Patient Portal
- **Domain:** Healthcare
- **Framework:** Django
- **Description:** Patient records viewer with appointment scheduling and prescription history.
- **Vulnerabilities:** A01 (horizontal privilege escalation on patient records), A02 (passwords stored with MD5), A07 (no account lockout)

#### App 03 — Banking Transaction Service
- **Domain:** Financial Services
- **Framework:** FastAPI
- **Description:** Microservice for fund transfers, balance inquiries, and transaction history.
- **Vulnerabilities:** A02 (API keys in source code), A04 (no rate limiting on transfers), A03 (NoSQL injection in transaction filter)

#### App 04 — Real Estate Listing Platform
- **Domain:** Real Estate
- **Framework:** Flask
- **Description:** Property listing service with image uploads, search, and agent contact forms.
- **Vulnerabilities:** A05 (debug mode enabled, default secret key), A03 (OS command injection in image processing), A10 (SSRF in URL-based image import)

#### App 05 — Online Learning Management System
- **Domain:** Education
- **Framework:** Django
- **Description:** Course management with student enrollment, grading, and file submissions.
- **Vulnerabilities:** A01 (students can access other students' grades), A08 (insecure deserialization of uploaded assignments via pickle), A05 (CORS wildcard)

#### App 21 — Insurance Claims Processor
- **Domain:** Insurance
- **Framework:** Flask
- **Description:** Claims submission, document upload, and adjuster assignment system.
- **Vulnerabilities:** A03 (SQL injection in claims search), A01 (adjusters can view any claim without authorization), A09 (no logging of claim modifications)

#### App 22 — Food Delivery Order System
- **Domain:** Food & Beverage
- **Framework:** FastAPI
- **Description:** Restaurant menu API, order placement, delivery tracking.
- **Vulnerabilities:** A04 (no rate limit on promo code redemption), A07 (JWT with no expiration), A02 (credit card numbers logged in plaintext)

#### App 23 — Government Permit Application Portal
- **Domain:** Government
- **Framework:** Django
- **Description:** Online permit applications with document uploads and status tracking.
- **Vulnerabilities:** A01 (any user can view/edit any permit application), A05 (admin panel exposed with default credentials), A08 (unsigned file uploads accepted as official documents)

#### App 24 — Veterinary Clinic Management
- **Domain:** Healthcare (Veterinary)
- **Framework:** Flask
- **Description:** Pet records, appointment scheduling, prescription management.
- **Vulnerabilities:** A03 (SQL injection in pet search), A02 (session tokens in URL parameters), A09 (no audit trail for prescription changes)

#### App 25 — Supply Chain Inventory Tracker
- **Domain:** Logistics / Supply Chain
- **Framework:** FastAPI
- **Description:** Warehouse inventory management with supplier integration endpoints.
- **Vulnerabilities:** A10 (SSRF via supplier webhook URL validation), A06 (uses known-vulnerable version of requests library), A07 (API keys shared across all suppliers)

#### App 46 — Charity Donation Platform
- **Domain:** Non-Profit
- **Framework:** Flask
- **Description:** Online donation processing with donor management and campaign tracking.
- **Vulnerabilities:** A02 (payment data transmitted over HTTP), A03 (SQL injection in donor search), A09 (no logging of financial transactions)

#### App 47 — Smart Home Device Manager
- **Domain:** IoT
- **Framework:** FastAPI
- **Description:** REST API for managing connected home devices, firmware updates, and scheduling.
- **Vulnerabilities:** A08 (unsigned firmware update packages accepted), A10 (SSRF in device discovery endpoint), A05 (default admin password)

#### App 48 — Freelancer Marketplace
- **Domain:** Gig Economy
- **Framework:** Django
- **Description:** Job posting, bidding, contract management, and payment escrow.
- **Vulnerabilities:** A01 (freelancers can modify other users' bids), A04 (no validation of payment amounts), A07 (password reset token never expires)

#### App 49 — Sports League Management
- **Domain:** Sports / Recreation
- **Framework:** Flask
- **Description:** Team registration, match scheduling, score reporting, and standings.
- **Vulnerabilities:** A03 (XSS in team name display), A01 (any user can update match scores), A05 (verbose error messages expose stack traces)

### Java Applications (13)

#### App 06 — Enterprise HR Management System
- **Domain:** Human Resources
- **Framework:** Spring Boot
- **Description:** Employee directory, payroll processing, leave management, and org charts.
- **Vulnerabilities:** A01 (any employee can view salary data), A08 (Java deserialization of employee import files), A02 (weak encryption for SSN storage)

#### App 07 — Airline Booking System
- **Domain:** Travel / Aviation
- **Framework:** Spring Boot
- **Description:** Flight search, seat reservation, booking management, and check-in.
- **Vulnerabilities:** A03 (SQL injection in flight search), A07 (session fixation on login), A04 (no booking rate limit allows inventory hoarding)

#### App 08 — Warehouse Management System
- **Domain:** Logistics
- **Framework:** Spring Boot
- **Description:** Inventory tracking, order fulfillment, shipping label generation.
- **Vulnerabilities:** A05 (Spring Actuator endpoints publicly exposed), A03 (LDAP injection in employee lookup), A10 (SSRF in shipping label URL fetch)

#### App 09 — Legal Document Management
- **Domain:** Legal
- **Framework:** Spring Boot
- **Description:** Case file management, document versioning, and client portal.
- **Vulnerabilities:** A01 (clients can access other clients' case files), A02 (documents stored unencrypted), A06 (uses Log4j 2.14.1)

#### App 10 — Telecom Billing Platform
- **Domain:** Telecommunications
- **Framework:** Spring Boot
- **Description:** Usage tracking, plan management, invoice generation, and payment processing.
- **Vulnerabilities:** A03 (SQL injection in usage report query), A04 (plan changes have no confirmation/review step), A09 (billing adjustments not logged)

#### App 26 — Pharmaceutical Drug Tracking
- **Domain:** Pharma
- **Framework:** Spring Boot
- **Description:** Drug batch tracking, distribution chain, and recall management.
- **Vulnerabilities:** A08 (XML external entity processing in batch import), A01 (any distributor can mark drugs as recalled), A02 (API tokens stored in properties file in plaintext)

#### App 27 — Hotel Reservation System
- **Domain:** Hospitality
- **Framework:** Spring Boot
- **Description:** Room booking, guest management, and housekeeping scheduling.
- **Vulnerabilities:** A07 (credential stuffing possible — no rate limit on login), A03 (SQL injection in guest search), A05 (H2 console enabled in production)

#### App 28 — Manufacturing Quality Control
- **Domain:** Manufacturing
- **Framework:** Spring Boot
- **Description:** Defect tracking, inspection workflows, and compliance reporting.
- **Vulnerabilities:** A01 (operators can approve their own inspections), A09 (quality overrides not logged), A04 (no separation of duties in approval workflow)

#### App 29 — Vehicle Fleet Management
- **Domain:** Transportation
- **Framework:** Spring Boot
- **Description:** Vehicle tracking, maintenance scheduling, driver assignment, fuel logging.
- **Vulnerabilities:** A10 (SSRF in GPS tracking integration), A06 (outdated Jackson databind with known CVE), A03 (injection in maintenance notes search)

#### App 30 — Auction Platform
- **Domain:** E-Commerce / Auctions
- **Framework:** Spring Boot
- **Description:** Item listing, bidding engine, auction timer, and payment settlement.
- **Vulnerabilities:** A04 (bid sniping prevention missing — design flaw), A07 (weak password policy), A08 (insecure deserialization in bid history import)

#### App 50 — Energy Utility Billing
- **Domain:** Energy / Utilities
- **Framework:** Spring Boot
- **Description:** Meter reading ingestion, usage calculation, bill generation, and outage reporting.
- **Vulnerabilities:** A03 (SQL injection in meter search), A01 (customers can view other accounts' bills), A10 (SSRF in meter data import URL), A05 (default Spring Security credentials)

### TypeScript Applications (12)

#### App 11 — Social Media Analytics Dashboard
- **Domain:** Marketing / Social Media
- **Framework:** Express + TypeScript
- **Description:** Dashboard aggregating social media metrics, campaign tracking, and report generation.
- **Vulnerabilities:** A10 (SSRF in social media URL preview), A03 (XSS in dashboard widget titles), A05 (API keys in client-side bundle)

#### App 12 — Crypto Wallet Service
- **Domain:** FinTech / Crypto
- **Framework:** NestJS
- **Description:** Wallet creation, balance management, transaction signing, and transfer history.
- **Vulnerabilities:** A02 (private keys stored in plaintext DB), A04 (no transaction confirmation step), A07 (no MFA on high-value transfers)

#### App 13 — Project Management Tool
- **Domain:** SaaS / Productivity
- **Framework:** Express + TypeScript
- **Description:** Task boards, sprint planning, team assignments, and time tracking.
- **Vulnerabilities:** A01 (users can access boards from other organizations), A03 (stored XSS in task descriptions), A09 (no audit log for permission changes)

#### App 14 — Telemedicine Appointment System
- **Domain:** Healthcare / Telehealth
- **Framework:** NestJS
- **Description:** Video appointment scheduling, patient intake forms, and prescription requests.
- **Vulnerabilities:** A02 (medical records sent over unencrypted channel), A07 (session tokens don't rotate after login), A01 (patients can view other patients' appointments)

#### App 15 — Digital Asset Management
- **Domain:** Media / Publishing
- **Framework:** Express + TypeScript
- **Description:** Image/video library with tagging, search, CDN integration, and access control.
- **Vulnerabilities:** A10 (SSRF in remote asset import), A01 (broken access control on private assets), A08 (no integrity check on uploaded assets)

#### App 31 — Event Ticketing Platform
- **Domain:** Entertainment
- **Framework:** NestJS
- **Description:** Event creation, ticket sales, QR code generation, and check-in.
- **Vulnerabilities:** A04 (no purchase quantity limits — scalping by design), A03 (SQL injection in event search), A07 (ticket transfer requires no authentication)

#### App 32 — Customer Support Ticket System
- **Domain:** Customer Service
- **Framework:** Express + TypeScript
- **Description:** Ticket creation, assignment, SLA tracking, and knowledge base.
- **Vulnerabilities:** A01 (agents can view tickets from other departments), A03 (stored XSS in ticket comments), A05 (CORS misconfiguration allows any origin)

#### App 33 — Recruitment ATS (Applicant Tracking)
- **Domain:** HR Tech
- **Framework:** NestJS
- **Description:** Job postings, candidate applications, interview scheduling, and offer management.
- **Vulnerabilities:** A01 (candidates can view other candidates' applications), A02 (resumes stored without encryption), A06 (uses vulnerable version of multer)

#### App 34 — Subscription Box Service
- **Domain:** E-Commerce / Subscription
- **Framework:** Express + TypeScript
- **Description:** Subscription management, box customization, billing cycle, and shipping.
- **Vulnerabilities:** A07 (predictable password reset tokens), A03 (NoSQL injection in product filter), A09 (subscription cancellations not logged)

#### App 35 — Compliance Document Tracker
- **Domain:** RegTech
- **Framework:** NestJS
- **Description:** Regulatory document management, deadline tracking, and audit preparation.
- **Vulnerabilities:** A01 (any user can mark compliance items as complete), A08 (document checksums not verified on upload), A05 (debug endpoints exposed)

### JavaScript Applications (10)

#### App 16 — Restaurant Review Platform
- **Domain:** Food & Hospitality
- **Framework:** Express.js
- **Description:** Restaurant profiles, user reviews, ratings, and photo uploads.
- **Vulnerabilities:** A03 (XSS in review text), A01 (users can delete other users' reviews), A07 (no rate limit on login endpoint)

#### App 17 — IoT Device Dashboard
- **Domain:** IoT / Smart Home
- **Framework:** Express.js
- **Description:** Device registration, telemetry visualization, remote control, and alerting.
- **Vulnerabilities:** A10 (SSRF in device firmware URL check), A05 (default MQTT credentials), A02 (device tokens transmitted in query strings)

#### App 18 — Peer-to-Peer Lending Platform
- **Domain:** FinTech
- **Framework:** Express.js
- **Description:** Loan listings, borrower applications, lender matching, and repayment tracking.
- **Vulnerabilities:** A02 (SSN/tax IDs stored with reversible encoding), A04 (no maximum loan amount validation), A01 (borrowers can view lender financial details)

#### App 19 — Content Management System
- **Domain:** Publishing / Media
- **Framework:** Express.js
- **Description:** Article authoring, editorial workflow, category management, and RSS feed.
- **Vulnerabilities:** A03 (stored XSS in article body), A08 (no CSP, third-party scripts loaded without integrity), A05 (admin route with no authentication)

#### App 20 — Fitness Tracking API
- **Domain:** Health & Wellness
- **Framework:** Express.js
- **Description:** Workout logging, nutrition tracking, goal setting, and progress reports.
- **Vulnerabilities:** A01 (users can view other users' health data), A07 (JWT secret is "secret"), A06 (uses express 4.16.0 with known vulnerabilities)

#### App 36 — Parking Management System
- **Domain:** Urban / Transportation
- **Framework:** Express.js
- **Description:** Parking spot availability, reservation, payment, and violation tracking.
- **Vulnerabilities:** A03 (SQL injection in license plate search), A04 (no validation of reservation time overlap), A09 (payment reversals not logged)

#### App 37 — Agricultural Crop Planner
- **Domain:** Agriculture
- **Framework:** Express.js
- **Description:** Field mapping, crop rotation planning, weather integration, and yield tracking.
- **Vulnerabilities:** A10 (SSRF in weather API proxy), A05 (environment variables logged to console), A06 (outdated axios with prototype pollution CVE)

#### App 38 — Museum Collection Catalog
- **Domain:** Arts & Culture
- **Framework:** Express.js
- **Description:** Artwork catalog, exhibition planning, loan management, and public search.
- **Vulnerabilities:** A01 (public users can access internal loan records), A03 (XSS in artwork description), A09 (no logging of catalog modifications)

#### App 39 — Wedding Planning Platform
- **Domain:** Events / Lifestyle
- **Framework:** Express.js
- **Description:** Vendor directory, guest list management, budget tracking, and timeline.
- **Vulnerabilities:** A07 (password stored in localStorage, no httpOnly cookies), A01 (users can view other users' guest lists), A02 (payment info in client-side state)

#### App 40 — Pet Adoption Portal
- **Domain:** Animal Welfare
- **Framework:** Express.js
- **Description:** Pet listings, adoption applications, shelter management, and volunteer coordination.
- **Vulnerabilities:** A03 (SQL injection in pet search), A05 (verbose error messages with stack traces), A08 (no CSRF tokens on adoption form submission)

#### App 41 — Library Book Reservation System
- **Domain:** Public Services
- **Framework:** Express.js
- **Description:** Book catalog, reservation, borrowing history, fine calculation, and notifications.
- **Vulnerabilities:** A01 (patrons can view other patrons' borrowing history), A03 (injection in book title search), A07 (session cookies without secure/httpOnly flags)

#### App 42 — Construction Project Tracker
- **Domain:** Construction
- **Framework:** Express.js
- **Description:** Project timeline, contractor management, material tracking, and compliance docs.
- **Vulnerabilities:** A01 (subcontractors can access all projects), A08 (compliance PDFs uploaded without integrity verification), A09 (no audit trail for project changes)

#### App 43 — Music Streaming Playlist Service
- **Domain:** Entertainment / Music
- **Framework:** Express.js
- **Description:** Playlist creation, track management, sharing, and playback history.
- **Vulnerabilities:** A01 (users can modify other users' playlists), A10 (SSRF in album art URL fetch), A05 (GraphQL introspection enabled in production)

#### App 44 — Election Polling System
- **Domain:** Government / Civic Tech
- **Framework:** Express.js
- **Description:** Poll creation, voter registration verification, vote casting, and result tallying.
- **Vulnerabilities:** A04 (no protection against double voting — design flaw), A02 (votes not encrypted at rest), A09 (vote modifications not logged)

#### App 45 — Corporate Travel & Expense
- **Domain:** Enterprise / Finance
- **Framework:** Express.js
- **Description:** Travel booking requests, expense report submission, approval workflows, and policy enforcement.
- **Vulnerabilities:** A01 (employees can approve their own expenses), A03 (injection in expense report search), A07 (SSO bypass via direct API access)

---

## Vulnerability Coverage Matrix

Each vulnerability should appear in at least 5 applications to ensure adequate test coverage.

| OWASP ID | Category | App Count | App IDs |
|----------|----------|-----------|---------|
| A01 | Broken Access Control | 28 | 1,2,5,6,9,13,14,15,16,18,20,21,23,26,28,32,33,35,38,39,41,42,43,45,48,49,50 |
| A02 | Cryptographic Failures | 14 | 2,3,6,9,11,12,14,17,18,22,24,26,33,39,44,46 |
| A03 | Injection | 20 | 1,3,4,7,8,10,11,13,16,19,21,24,27,29,31,34,36,38,40,41,43,45,46,49,50 |
| A04 | Insecure Design | 10 | 3,7,12,22,28,30,31,36,44,48 |
| A05 | Security Misconfiguration | 14 | 4,5,8,11,17,19,20,23,27,32,35,37,47,49,50 |
| A06 | Vulnerable & Outdated Components | 6 | 9,20,25,29,33,37 |
| A07 | Auth Failures | 14 | 2,7,12,14,16,20,22,27,30,31,34,39,41,45,48 |
| A08 | Integrity Failures | 10 | 5,6,8,15,19,23,26,30,35,42 |
| A09 | Logging Failures | 11 | 1,10,13,21,22,24,28,34,36,38,42,44,46 |
| A10 | SSRF | 10 | 4,8,10,11,15,17,25,29,37,43,47,50 |

---

## Directory Structure

```
owasp-test/
├── README.md
├── docs/
│   └── plans/
│       └── initial/
│           └── plan.md              # This document
├── apps/
│   ├── python/
│   │   ├── app-01-ecommerce-catalog/
│   │   ├── app-02-patient-portal/
│   │   ├── app-03-banking-service/
│   │   ├── app-04-real-estate/
│   │   ├── app-05-learning-mgmt/
│   │   ├── app-21-insurance-claims/
│   │   ├── app-22-food-delivery/
│   │   ├── app-23-govt-permits/
│   │   ├── app-24-vet-clinic/
│   │   ├── app-25-supply-chain/
│   │   ├── app-46-charity-donations/
│   │   ├── app-47-smart-home/
│   │   ├── app-48-freelancer-market/
│   │   └── app-49-sports-league/
│   ├── java/
│   │   ├── app-06-hr-management/
│   │   ├── app-07-airline-booking/
│   │   ├── app-08-warehouse-mgmt/
│   │   ├── app-09-legal-documents/
│   │   ├── app-10-telecom-billing/
│   │   ├── app-26-pharma-tracking/
│   │   ├── app-27-hotel-reservation/
│   │   ├── app-28-mfg-quality/
│   │   ├── app-29-fleet-management/
│   │   ├── app-30-auction-platform/
│   │   └── app-50-energy-billing/
│   ├── typescript/
│   │   ├── app-11-social-analytics/
│   │   ├── app-12-crypto-wallet/
│   │   ├── app-13-project-mgmt/
│   │   ├── app-14-telemedicine/
│   │   ├── app-15-digital-assets/
│   │   ├── app-31-event-ticketing/
│   │   ├── app-32-support-tickets/
│   │   ├── app-33-recruitment-ats/
│   │   ├── app-34-subscription-box/
│   │   └── app-35-compliance-tracker/
│   └── javascript/
│       ├── app-16-restaurant-reviews/
│       ├── app-17-iot-dashboard/
│       ├── app-18-p2p-lending/
│       ├── app-19-cms/
│       ├── app-20-fitness-tracker/
│       ├── app-36-parking-mgmt/
│       ├── app-37-crop-planner/
│       ├── app-38-museum-catalog/
│       ├── app-39-wedding-planner/
│       ├── app-40-pet-adoption/
│       ├── app-41-library-reservation/
│       ├── app-42-construction-tracker/
│       ├── app-43-music-streaming/
│       ├── app-44-election-polling/
│       └── app-45-travel-expense/
```

---

## Per-Application Structure

Each application should follow this standard structure:

```
app-NN-name/
├── README.md              # App description, setup, and HIDDEN vulnerability manifest
├── src/                   # Source code
├── tests/                 # Basic tests (not security-focused)
├── config/                # Configuration files
├── vulnerabilities.json   # Ground truth: list of planted vulnerabilities (for scoring)
└── Dockerfile             # Containerized deployment
```

### `vulnerabilities.json` Schema

```json
{
  "app_id": "app-01",
  "app_name": "E-Commerce Product Catalog API",
  "language": "python",
  "framework": "flask",
  "vulnerabilities": [
    {
      "owasp_id": "A01",
      "category": "Broken Access Control",
      "location": "src/routes/orders.py:45",
      "description": "Order details endpoint allows any authenticated user to view any order by ID without ownership check",
      "severity": "high",
      "cwe": "CWE-639"
    }
  ]
}
```

---

## Implementation Guidelines

1. **Realism First:** Each app should look like a legitimate (if simplified) business application. Vulnerabilities should be embedded naturally, not as obvious test cases.
2. **Minimum Viable Functionality:** Each app should have 3–5 working API endpoints or pages with actual business logic.
3. **Mixed Difficulty:** Some vulnerabilities should be surface-level (e.g., SQL injection in a query string), others should be subtle (e.g., TOCTOU race conditions, logic flaws).
4. **False Positives:** Include patterns that look suspicious but are actually safe (e.g., parameterized queries, properly validated inputs) to test agent precision.
5. **Ground Truth:** Every planted vulnerability must be documented in `vulnerabilities.json` for automated scoring.
6. **No External Dependencies at Runtime:** Apps should use SQLite/H2/in-memory stores. No external databases or services required.
7. **Docker Support:** Each app must include a Dockerfile for isolated testing.

---

## Phased Implementation

### Phase 1 — Foundation (Apps 1–10)
- 5 Python apps (Flask/Django/FastAPI)
- 5 Java apps (Spring Boot)
- Focus on A01, A02, A03, A05 — the most common vulnerabilities

### Phase 2 — Expansion (Apps 11–25)
- 5 TypeScript apps (Express/NestJS)
- 5 JavaScript apps (Express.js)
- 5 additional Python apps
- Introduce A04, A07, A08, A10

### Phase 3 — Full Coverage (Apps 26–40)
- 5 Java apps, 5 TypeScript apps, 5 JavaScript apps
- Ensure all OWASP categories have ≥5 apps
- Add more subtle/complex vulnerability patterns

### Phase 4 — Completion & Hardening (Apps 41–50)
- Remaining 10 apps across JS and Java
- Add decoy safe patterns for false-positive testing
- Review and finalize ground truth manifests

---

## Success Criteria

An effective vulnerability detection agent should achieve:
- **Recall ≥ 80%:** Detect at least 80% of planted vulnerabilities
- **Precision ≥ 70%:** At least 70% of reported findings are true positives
- **Coverage:** Detect at least one instance of each OWASP Top 10 category
- **Localization:** Identify the correct file and approximate line number
