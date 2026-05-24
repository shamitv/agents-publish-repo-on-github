# Phase 5 — JavaScript Apps Implementation (15 apps)

**Status:** 🔴 TODO  
**Language:** JavaScript (Node.js)  
**Framework:** Express.js  
**Template Engine:** EJS / Handlebars

---

## App-16: Restaurant Reviews

**Domain:** Food Tech  
**Difficulty Target:** ★★☆☆☆ Easy  
**Business Logic:** Restaurant listings, user reviews, ratings, search

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A03 | Stored XSS in review text — `res.send(`<div>${review.text}</div>`)` | ★☆☆☆☆ | Trivial stored XSS |
| 2 | A01 | IDOR on review edit — modify other users' reviews | ★☆☆☆☆ | Trivial |
| 3 | A05 | Missing security headers — `X-Frame-Options`, CSP, etc. | ★☆☆☆☆ | Clickjacking possible |

### Chained Attack: XSS → Cookie Theft → Account Takeover

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Stored XSS via unsanitized review HTML | Medium | A03 |
| 2 | Session cookie missing httpOnly flag | Low | A05 |

**Impact:** Account Takeover  
**Difficulty:** ★★☆☆☆ Easy

---

## App-17: IoT Dashboard

**Domain:** IoT / Smart Devices  
**Difficulty Target:** ★★★★☆ Medium-Hard  
**Business Logic:** Device management, real-time sensor data, firmware updates, alerts

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on device commands — control any device | ★★☆☆☆ | `POST /api/devices/{id}/command` |
| 2 | A10 | SSRF in firmware fetch — `axios.get(firmwareUrl)` | ★★☆☆☆ | Fetches attacker URL |
| 3 | A08 | `eval()` in rule engine — user-created automation rules `eval(userRule)` | ★★★★★ | Hidden in custom rules |
| 4 | A09 | No audit trail for device configuration changes | ★★☆☆☆ | |

### Chained Attack: eval() → RCE → Full Device Control

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Unsafe `eval()` in automation rule engine | Medium | A08 |
| 2 | IDOR allows controlling all devices | Low | A01 |

**Impact:** Account Takeover — RCE leads to controlling all smart devices  
**Difficulty:** ★★★★☆ Medium-Hard — eval is hidden in rule engine feature

---

## App-18: P2P Lending Platform

**Domain:** FinTech  
**Difficulty Target:** ★★★★★ Hard  
**Business Logic:** Loan listings, investments, credit scoring, repayment tracking

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on loan applications — view/approve any loan | ★☆☆☆☆ | Obvious |
| 2 | A02 | Weak random number for loan ID generation — `Math.random()` | ★★☆☆☆ | Predictable loan IDs |
| 3 | A07 | JWT secret from env var that is logged on startup — `console.log(process.env.JWT_SECRET)` | ★★★★☆ | Very subtle — in startup script |
| 4 | A09 | Inconsistent logging — loan modifications logged but without userId | ★★☆☆☆ | |

### Chained Attack: JWT Secret Leak → IDOR → Fraudulent Loan Approval

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | JWT secret logged to console on startup (visible in logs) | Medium | A07 |
| 2 | IDOR allows approving any loan as any user | Medium | A01 |

**Impact:** Account Takeover — forge admin JWT, approve fraudulent loans, financial fraud  
**Difficulty:** ★★★★★ Hard — requires finding leaked secret in logs, combining with IDOR

---

## App-19: Content Management System

**Domain:** Web Publishing  
**Difficulty Target:** ★★★☆☆ Medium  
**Business Logic:** Article publishing, user roles, media upload, comments

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on unpublished articles — view drafts of other users | ★☆☆☆☆ | |
| 2 | A03 | Stored XSS in article body — rendered unsanitized in rich text | ★★☆☆☆ | |
| 3 | A05 | `multer` file upload with no extension validation — arbitrary file upload | ★★★☆☆ | Upload .js or .html files |

### Chained Attack: Arbitrary File Upload → Stored XSS → Admin Session Hijack

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Unrestricted file upload allows uploading HTML with malicious JS | Medium | A05 |
| 2 | Stored XSS in article body when admin previews | Medium | A03 |

**Impact:** Account Takeover — admin session stolen via embedded JS  
**Difficulty:** ★★★☆☆ Medium

---

## App-20: Fitness Tracker

**Domain:** Health / Wearables  
**Difficulty Target:** ★★☆☆☆ Easy  
**Business Logic:** User profiles, activity logs, workout plans, health metrics

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on health metrics — view any user's heart rate, steps, etc. | ★☆☆☆☆ | Trivial |
| 2 | A03 | NoSQLi in workout search — MongoDB `$where` injection | ★★★☆☆ | |
| 3 | A09 | No logging on personal data exports | ★☆☆☆☆ | |

### Chained Attack: NoSQLi → Bulk Health Data Extraction

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | NoSQL injection in workout search allows blind data extraction | Medium | A03 |
| 2 | No rate limiting on API calls | Low | A04 |

**Impact:** DB Exfiltration — extract all user health records  
**Difficulty:** ★★☆☆☆ Easy

---

## App-36: Parking Management System

**Domain:** Urban Infrastructure  
**Difficulty Target:** ★★☆☆☆ Easy  
**Business Logic:** Parking spot reservations, payments, vehicle registration, violation ticketing

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on reservations — view/cancel others' bookings | ★☆☆☆☆ | |
| 2 | A03 | SQLi in license plate search | ★★☆☆☆ | |
| 3 | A09 | No audit for violation record modifications | ★☆☆☆☆ | |

### Chained Attack: SQLi → User Credentials → Account Takeover

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | SQL injection in plate search | Medium | A03 |
| 2 | Passwords stored in plaintext | Low | A02 |

**Impact:** Account Takeover  
**Difficulty:** ★★☆☆☆ Easy

---

## App-37: Crop Planner

**Domain:** Agriculture  
**Difficulty Target:** ★★★☆☆ Medium  
**Business Logic:** Crop rotation planning, soil analysis, weather data, yield forecasting

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on farm data — view other farms' planting schedules | ★☆☆☆☆ | |
| 2 | A03 | SSTI in weather report rendering — `res.render(userProvidedTemplate)` | ★★★★☆ | Hidden in custom report builder |
| 3 | A10 | SSRF in weather API — user supplies weather API URL | ★★☆☆☆ | |

### Chained Attack: SSTI → RCE → Data Modification

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Server-side template injection in report builder | Medium | A03 |
| 2 | IDOR allows modifying other farms' data | Low | A01 |

**Impact:** Data Modification — RCE leading to altered crop forecasts  
**Difficulty:** ★★★★☆ Medium-Hard — SSTI is hidden in report template feature

---

## App-38: Museum Archive

**Domain:** Culture / Heritage  
**Difficulty Target:** ★★☆☆☆ Easy  
**Business Logic:** Artifact catalog, exhibition management, donor records, visitor analytics

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on donor records — view PII of all donors | ★☆☆☆☆ | Trivial |
| 2 | A03 | Stored XSS in artifact descriptions | ★★☆☆☆ | |
| 3 | A09 | No logging on collection record modifications | ★☆☆☆☆ | |

### Chained Attack: IDOR → Donor PII Harvesting

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | IDOR on donor list exposes full PII | Medium | A01 |
| 2 | No rate limiting on API | Low | A04 |

**Impact:** DB Exfiltration  
**Difficulty:** ★★☆☆☆ Easy

---

## App-39: Wedding Planning Platform

**Domain:** Events / Hospitality  
**Difficulty Target:** ★★★☆☆ Medium  
**Business Logic:** Vendor booking, guest lists, budget tracking, timeline management

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on guest lists — view other weddings' guest lists with RSVPs | ★☆☆☆☆ | Privacy violation |
| 2 | A03 | Stored XSS in vendor reviews | ★★☆☆☆ | |
| 3 | A07 | Weak JWT secret — `jwt_secret` or hardcoded string | ★★☆☆☆ | `"supersecret"` |
| 4 | A04 | Budget total calculated client-side — server accepts submitted total | ★★☆☆☆ | |

### Chained Attack: Weak JWT → Forge Token → Modify Vendor Payments

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Weak JWT secret allows token forgery | Medium | A07 |
| 2 | Client-side budget calculation accepts server-submitted total | Medium | A04 |

**Impact:** Data Modification — forge vendor account JWT, inflate payment amounts  
**Difficulty:** ★★★☆☆ Medium

---

## App-40: Pet Adoption Platform

**Domain:** Social / Animal Welfare  
**Difficulty Target:** ★★☆☆☆ Easy  
**Business Logic:** Pet listings, adoption applications, shelter management, donation tracking

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on adoption applications — view other applicants' personal info | ★☆☆☆☆ | |
| 2 | A03 | SQLi in pet search | ★★☆☆☆ | |
| 3 | A09 | No logging on application status changes | ★☆☆☆☆ | |

### Chained Attack: SQLi → Adopter PII Extraction

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | SQL injection in pet search | Medium | A03 |
| 2 | IDOR on adoption applications exposes PII | Low | A01 |

**Impact:** DB Exfiltration  
**Difficulty:** ★★☆☆☆ Easy

---

## App-41: Library Management System

**Domain:** Education  
**Difficulty Target:** ★★★☆☆ Medium  
**Business Logic:** Book catalog, member management, checkouts, fines

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on member details — view other members' borrowing history | ★☆☆☆☆ | |
| 2 | A03 | Stored XSS in book reviews | ★★☆☆☆ | |
| 3 | A05 | Directory traversal in cover image upload — `fs.readFileSync("covers/" + fileName)` | ★★★☆☆ | `../../../etc/passwd` |

### Chained Attack: Directory Traversal → File Read → Credential Extraction

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Directory traversal in cover image serving | Medium | A05 |
| 2 | Configuration file readable via traversal contains DB password | Low | A05 |

**Impact:** Lateral Movement — extracted credentials used to access database  
**Difficulty:** ★★★☆☆ Medium

---

## App-42: Construction Project Manager

**Domain:** Construction / Engineering  
**Difficulty Target:** ★★★★☆ Medium-Hard  
**Business Logic:** Project plans, permits, contractor management, material orders, inspections

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on project plans — view other companies' blueprints | ★☆☆☆☆ | IP theft |
| 2 | A10 | SSRF in material pricing — fetches from user-supplied URL | ★★☆☆☆ | |
| 3 | A08 | `eval()` in blueprint formula calculator | ★★★★☆ | Hidden in calculation engine |
| 4 | A09 | No logging on permit document changes | ★★☆☆☆ | |

### Chained Attack: eval() → SSRF → Internal Metadata

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Unsafe `eval()` in formula calculator | Medium | A08 |
| 2 | SSRF to extract cloud metadata from internal endpoint | Low | A10 |

**Impact:** Lateral Movement — cloud credential extraction  
**Difficulty:** ★★★★☆ Medium-Hard

---

## App-43: Music Streaming Backend

**Domain:** Media / Entertainment  
**Difficulty Target:** ★★☆☆☆ Easy  
**Business Logic:** Playlist management, song uploads, user subscriptions, recommendations

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on playlists — view/edit others' playlists | ★☆☆☆☆ | |
| 2 | A03 | Stored XSS in playlist descriptions | ★★☆☆☆ | |
| 3 | A05 | Unrestricted file upload — upload any file type | ★★☆☆☆ | Upload malicious files |

### Chained Attack: File Upload → XSS → Session Theft

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Unrestricted file upload allows HTML/JS file | Medium | A05 |
| 2 | Stored XSS via uploaded HTML file viewed by admin | Medium | A03 |

**Impact:** Account Takeover  
**Difficulty:** ★★☆☆☆ Easy

---

## App-44: Election Management System

**Domain:** Governance / Voting  
**Difficulty Target:** ★★★★★ Hard  
**Business Logic:** Voter registration, ballot creation, vote tallying, results

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on vote records — view who voted for whom | ★☆☆☆☆ | Privacy violation |
| 2 | A04 | Vote count logic flawed — race condition allows double voting | ★★★★★ | Very subtle timing issue |
| 3 | A03 | SSTI in ballot description — `res.render(template, { userText })` | ★★★★☆ | |
| 4 | A09 | No audit trail for ballot modifications | ★★☆☆☆ | |

### Chained Attack: Race Condition → Vote Tampering

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Race condition in vote submission allows double-counting | Medium | A04 |
| 2 | No locking on vote tally updates | Low | A04 |

**Impact:** Data Modification — manipulate election results  
**Difficulty:** ★★★★★ Hard — race condition requires concurrent request understanding

---

## App-45: Travel Expense Manager

**Domain:** Finance / Business  
**Difficulty Target:** ★★★☆☆ Medium  
**Business Logic:** Expense reports, approvals, reimbursements, policy compliance

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on expense reports — view other employees' reports | ★☆☆☆☆ | |
| 2 | A03 | SQLi in expense search | ★★☆☆☆ | |
| 3 | A07 | No CSRF protection on expense approval — admin can be tricked | ★★☆☆☆ | |
| 4 | A02 | Plaintext bank account numbers in export CSV | ★☆☆☆☆ | Data exposure |

### Chained Attack: CSRF → Expense Approval → Fraud

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | No CSRF token on expense approval endpoint | Medium | A04 |
| 2 | IDOR allows viewing any employee's banking details | Low | A01 |

**Impact:** Account Takeover — trick admin into approving fraudulent expenses, steal reimbursement funds  
**Difficulty:** ★★★☆☆ Medium

---

## Implementation Instructions

For each app:
1. Create directory: `apps/javascript/app-XX-<name>/`
2. Create `package.json` with Express + dependencies
3. Create `src/app.js` or `src/server.js` with routes
4. Create `src/views/` for EJS templates (XSS targets)
5. Create `src/public/` for static files
6. Create `.vulns` JSON manifest
7. Create `README.md` following the template
8. Create `reports/app-XX-<name>.md`