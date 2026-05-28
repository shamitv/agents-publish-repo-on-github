# Security Report: app-07 — Airline Booking System

**Language:** Java (Spring-boot)
**Directory:** `apps/java/app-07-airline-booking`

---

## Application Information
- **App ID:** app-07
- **Name:** Airline Booking System
- **Language:** Java
- **Framework:** Spring-boot

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A03 | Injection | Critical | src/main/java/com/airline/repository/FlightSearchDao.java | CWE-89 |
| V2 | A07 | Identification and Authentication Failures | High | src/main/java/com/airline/config/SecurityConfig.java | CWE-384 |
| V3 | A04 | Insecure Design | High | src/main/java/com/airline/service/BookingService.java | CWE-799 |

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection

- **Severity:** Critical
- **Location:** `src/main/java/com/airline/repository/FlightSearchDao.java`:15-22 (method: `searchFlights`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
Flight search SQL query built via string concatenation with user-supplied origin, destination, and date values

### VULN-02: A07 — Identification and Authentication Failures

- **Severity:** High
- **Location:** `src/main/java/com/airline/config/SecurityConfig.java`:28-30 (method: `filterChain`)
- **CWE:** [CWE-384](https://cwe.mitre.org/data/definitions/384.html)

#### Description
Session fixation protection disabled via sessionFixation().none() — session ID not rotated on login

### VULN-03: A04 — Insecure Design

- **Severity:** High
- **Location:** `src/main/java/com/airline/service/BookingService.java`:20-42 (method: `createBooking`)
- **CWE:** [CWE-799](https://cwe.mitre.org/data/definitions/799.html)

#### Description
No rate limiting, no payment timeout, no concurrency control on booking creation — allows inventory hoarding


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Sequential PNR Enumeration → Booking IDOR → Stored XSS on Staff View

- **Combined Impact:** `account_takeover`
- **Difficulty:** Medium
- **Subtlety Tags:** `cross_file` `direct_data_flow` `realistic_decoy`

#### Prerequisites
- attacker can reach the public request path
- attacker can control one request parameter or body field

#### Attack Narrative
Attacker registers with a name containing a script tag, enumerates sequential PNRs to access other passengers' bookings via the IDOR boarding-summary endpoint, and the malicious name executes as XSS when airline staff renders the boarding list, stealing staff session cookies.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | PNR generated as an incrementing integer counter making all booking references predictable and enumerable | Low | A04 | CWE-330 | src/main/java/com/airline/service/PnrGenerator.java | `generate` |
| 2 | GET /api/bookings/{pnr}/boarding-summary returns full booking details without verifying the requesting user owns the PNR | Medium | A01 | CWE-639 | src/main/java/com/airline/controller/BookingController.java | `getBoardingSummary` |
| 3 | Passenger name is concatenated into a raw HTML string in the API response without encoding; executes as Stored XSS when rendered via innerHTML on staff UI | Medium | A03 | CWE-79 | src/main/java/com/airline/controller/BookingController.java | `getBoardingSummary` |

### CHAIN-02: Subtle Injection Pivot To Injection

- **Combined Impact:** `account_takeover`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy` `direct_data_flow` `secondary_chain`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state
- attacker can reach the public request path
- attacker can control one request parameter or body field

#### Attack Narrative
Attacker combines a low-visibility entry point with stored or derived application state, then pivots to a higher-impact sink that is reachable only after following the cross-file flow.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | No rate limiting, no payment timeout, no concurrency control on booking creation — allows inventory hoarding | High | A04 | CWE-799 | src/main/java/com/airline/service/BookingService.java | `createBooking` |
| 2 | Session fixation protection disabled via sessionFixation().none() — session ID not rotated on login | High | A07 | CWE-384 | src/main/java/com/airline/config/SecurityConfig.java | `filterChain` |
| 3 | Flight search SQL query built via string concatenation with user-supplied origin, destination, and date values | Critical | A03 | CWE-89 | src/main/java/com/airline/repository/FlightSearchDao.java | `searchFlights` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/main/java/com/airline/config/SecurityConfig.java | BCryptPasswordEncoder — password hashing is SAFE |
| src/main/java/com/airline/repository/FlightRepository.java | Spring Data JPA with @Query and named params — NOT injectable |
| src/main/java/com/airline/controller/BookingController.java | PNR lookup validates ownership — access control is correct here |
