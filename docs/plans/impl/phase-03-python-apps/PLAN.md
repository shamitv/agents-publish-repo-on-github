# Phase 3 — Python Apps Implementation (9 apps)

**Status:** 🔴 TODO  
**Language:** Python  
**Frameworks:** Flask (apps 05, 21, 22, 24, 25, 46, 47, 48, 49)

---

## App-05: Learning Management System (LMS)

**Domain:** Education / E-Learning  
**Difficulty Target:** ★★★☆☆ Medium-Hard  
**Framework:** Flask  
**Business Logic:** Course catalog, student enrollment, quiz submission, grade viewing

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on grade endpoint — students can view other students' grades by changing `user_id` | ★☆☆☆☆ | Obvious IDOR |
| 2 | A03 | SQLi in course search — raw query with `f"WHERE title LIKE '%{query}%'"` | ★★☆☆☆ | Classic search injection |
| 3 | A07 | Weak password reset — token generated via `random.randint(100000,999999)` | ★★★☆☆ | Predictable 6-digit token — brute-forceable |
| 4 | A04 | Mass assignment — `User.update(request.form)` allows setting `is_admin=True` | ★★☆☆☆ | Hidden in profile update |

### Chained Attack: Weak Reset → IDOR → Admin Escalation

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Predictable password reset token (6-digit int) | Low | A07 |
| 2 | IDOR on profile endpoint to change email after reset | Medium | A01 |
| 3 | Mass assignment to set `is_admin=True` | Medium | A04 |

**Impact:** Account Takeover (admin account)  
**Difficulty:** ★★★☆☆ Medium — requires understanding token generation and chaining with mass assignment

### Decoys
- "Secure" password reset endpoint that actually resets via email (but token is weak)
- Sanitized course search on a different route using parameterized queries

---

## App-21: Insurance Claims Portal

**Domain:** Insurance / Finance  
**Difficulty Target:** ★★★★★ Hard  
**Framework:** Flask  
**Business Logic:** File claims, upload documents, view claim status, process payouts

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on claim details — `GET /api/claims/<id>` without ownership check | ★☆☆☆☆ | Obvious |
| 2 | A03 | NoSQLi in MongoDB claim search — `db.claims.find({"$where": f"this.status == '{input}'"})` | ★★★★☆ | Blind NoSQL injection — hard to detect |
| 3 | A10 | SSRF in document preview — fetches from attacker-controlled URL | ★★☆☆☆ | `requests.get(url)` in doc viewer |
| 4 | A02 | Weak encryption of SSN — XOR with static key | ★★★☆☆ | Hidden in payout processor |

### Chained Attack: NoSQLi → SSRF → Internal Metadata Exposure

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | NoSQL injection in claim status filter | Medium | A03 |
| 2 | SSRF via document preview fetching internal metadata endpoint | Medium | A10 |

**Impact:** Lateral Movement — extract cloud metadata credentials from internal endpoint  
**Difficulty:** ★★★★★ Hard — NoSQLi requires blind injection techniques; SSRF target requires internal knowledge

### Decoys
- Parameterized MongoDB query on a different route
- URL validation on document upload that allows legitimate URLs but misses SSRF edge cases

---

## App-22: Food Delivery Platform

**Domain:** Food Tech / Logistics  
**Difficulty Target:** ★★☆☆☆ Easy  
**Framework:** Flask  
**Business Logic:** Restaurant listings, order placement, delivery tracking, payment

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on order details — view any order by ID | ★☆☆☆☆ | Trivial |
| 2 | A03 | Stored XSS in restaurant review — `render_template_string(review_text)` | ★★☆☆☆ | Classic stored XSS |
| 3 | A04 | Insecure design — order total calculated client-side then accepted server-side | ★★☆☆☆ | Submit $0.01 orders |

### Chained Attack: XSS in Review → Session Theft → Account Takeover

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Stored XSS via unescaped restaurant review | Medium | A03 |
| 2 | Session cookie lacks httpOnly flag | Low | A07 |

**Impact:** Account Takeover  
**Difficulty:** ★★☆☆☆ Easy

### Decoys
- Properly escaped review display on admin review moderation page
- CSRF token implementation that's actually effective

---

## App-24: Veterinary Clinic Management

**Domain:** Healthcare / Veterinary  
**Difficulty Target:** ★★★☆☆ Medium  
**Framework:** Flask  
**Business Logic:** Patient records, appointment scheduling, prescription management, billing

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on pet medical records — `GET /api/pets/<id>/records` | ★☆☆☆☆ | No ownership check |
| 2 | A02 | Plaintext storage of pet owner's credit card in DB | ★★☆☆☆ | Logged in billing module |
| 3 | A08 | Insecure deserialization in appointment import — `pickle.loads(data)` | ★★★★☆ | Hidden in bulk import feature |

### Chained Attack: Pickle Deserialization → RCE → DB Exfiltration

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Pickle deserialization in appointment CSV import | Medium | A08 |
| 2 | No input validation on imported data allows arbitrary Python execution | Medium | A03 |

**Impact:** DB Exfiltration — RCE leads to full database dump  
**Difficulty:** ★★★★☆ Medium-Hard — requires crafting malicious pickle payload

### Decoys
- JSON-based import that validates properly
- "Secure" encryption of credit cards that's actually just base64

---

## App-25: Supply Chain Management

**Domain:** Logistics / Manufacturing  
**Difficulty Target:** ★★★★★ Hard  
**Framework:** Flask  
**Business Logic:** Inventory tracking, supplier management, order fulfillment, shipping

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | BOLA on inventory API — access any org's inventory | ★☆☆☆☆ | No org scoping |
| 2 | A10 | SSRF in supplier portal — fetches supplier prices from user-supplied URL | ★★☆☆☆ | `urllib.request.urlopen(url)` |
| 3 | A05 | Debug mode enabled — `/console` exposes Werkzeug debugger | ★★★☆☆ | Requires knowing to check |
| 4 | A03 | LDAP injection in supplier search — `ldap_search(f"(cn={input})")` | ★★★★☆ | Blind LDAP injection |

### Chained Attack: Debug Console → SSRF → Cloud Metadata → Credential Extraction

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | Werkzeug debug console enabled (no pin protection misconfig) | Medium | A05 |
| 2 | SSRF via supplier price checker to `http://169.254.169.254/latest/meta-data/` | Low | A10 |

**Impact:** Lateral Movement — extract cloud IAM credentials from metadata endpoint  
**Difficulty:** ★★★★★ Hard — requires knowing debug console exists AND chaining to SSRF

### Decoys
- Proper URL validation on a different "shipping label" endpoint
- Production config that disables debug elsewhere but not in this route

---

## App-46: Charity Donations Platform

**Domain:** Non-Profit / Finance  
**Difficulty Target:** ★★☆☆☆ Easy  
**Framework:** Flask  
**Business Logic:** Donation campaigns, donor management, fundraising tracking

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on campaign details — see other orgs' donors list | ★☆☆☆☆ | Trivial |
| 2 | A03 | Stored XSS in donor comments — innerHTML rendering | ★★☆☆☆ | Classic |
| 3 | A09 | No audit trail for donation refunds | ★☆☆☆☆ | Missing logs |

### Chained Attack: IDOR → Donor PII Harvesting

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | IDOR on campaign endpoint exposes donor list with emails | Low | A01 |
| 2 | No rate limiting on bulk API calls | Low | A04 |

**Impact:** DB Exfiltration — bulk harvest donor PII  
**Difficulty:** ★★☆☆☆ Easy

---

## App-47: Smart Home Controller

**Domain:** IoT / Home Automation  
**Difficulty Target:** ★★★★☆ Medium-Hard  
**Framework:** Flask  
**Business Logic:** Device management, automation rules, user access sharing, logs

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on device control — control other users' devices | ★★☆☆☆ | Can toggle locks remotely |
| 2 | A02 | Hardcoded API key for cloud service in source | ★☆☆☆☆ | Plaintext in config |
| 3 | A06 | Outdated library — Flask-CORS with `Access-Control-Allow-Origin: *` | ★★☆☆☆ | CORS misconfig |
| 4 | A10 | SSRF in firmware update — fetches from user-provided URL | ★★★☆☆ | Device firmware URL |

### Chained Attack: CORS Misconfig → Hardcoded Key → Cloud API Abuse

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | CORS allows any origin + hardcoded cloud API key in frontend JS | Medium | A05 |
| 2 | No CSRF protection on device control endpoints | Low | A04 |

**Impact:** Lateral Movement — attacker uses exposed API key to access cloud backend, control all devices  
**Difficulty:** ★★★★☆ Medium-Hard — requires understanding CORS + CSRF chaining

---

## App-48: Freelancer Marketplace

**Domain:** Gig Economy / Professional Services  
**Difficulty Target:** ★★★☆☆ Medium  
**Framework:** Flask  
**Business Logic:** Job listings, proposals, messaging, payments, ratings

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on proposal viewing — see other freelancers' proposals | ★☆☆☆☆ | Trivial |
| 2 | A03 | Stored XSS in portfolio HTML — freelancer embeds malicious script | ★★☆☆☆ | Rich text editor |
| 3 | A02 | Payment amount tampering — no server-side validation of final amount | ★★☆☆☆ | Change payment on client side |
| 4 | A07 | JWT with `alg: none` accepted — `"alg":"none","typ":"JWT"` — no signature verification | ★★★★☆ | Subtle — hidden in JWT decode path |

### Chained Attack: JWT Algorithm Confusion → Account Takeover

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | JWT verification library accepts `alg: none` tokens | Medium | A07 |
| 2 | IDOR on user profile update allows modifying email | Low | A01 |

**Impact:** Account Takeover — forge arbitrary user JWT, change their email, reset password  
**Difficulty:** ★★★★☆ Medium-Hard — JWT none attack is known but subtle in code review

---

## App-49: Sports League Management

**Domain:** Sports / Recreation  
**Difficulty Target:** ★★☆☆☆ Easy  
**Framework:** Flask  
**Business Logic:** Team rosters, match scheduling, score tracking, player stats

### Proposed Vulnerabilities

| # | OWASP | Vuln | Difficulty | Notes |
|---|-------|------|-----------|-------|
| 1 | A01 | IDOR on player stats — view/edit any player's personal info | ★☆☆☆☆ | Trivial |
| 2 | A03 | SQLi in team search — `WHERE team_name LIKE '%{search}%'` | ★★☆☆☆ | Simple injection |
| 3 | A09 | No logging of score changes — match results can be altered undetected | ★☆☆☆☆ | Easy miss |

### Chained Attack: SQLi → DB Schema Enumeration → Credential Extraction

| Step | Issue | Severity | OWASP |
|------|-------|---------|-------|
| 1 | SQL injection in team search endpoint | Medium | A03 |
| 2 | Database user has excessive privileges (can read `users` table) | Low | A05 |

**Impact:** DB Exfiltration — extract all user credentials  
**Difficulty:** ★★☆☆☆ Easy

---

## Implementation Instructions

For each app:
1. Create directory structure: `apps/python/app-XX-<name>/`
2. Create `requirements.txt` with Flask + dependencies
3. Create `src/app.py` (or `src/main.py`) with routes
4. Create `src/templates/` for HTML (XSS targets)
5. Create `src/static/` for JS (client-side vulns)
6. Create `.vulns` JSON manifest
7. Create `README.md` following the template
8. Create `reports/app-XX-<name>.md`