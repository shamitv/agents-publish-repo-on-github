# Security Report: app-27 — Hotel Reservation System

**Language:** Java (Spring-boot)
**Directory:** `apps/java/app-27-hotel-reservation`

---

## Application Information
- **App ID:** app-27
- **Name:** Hotel Reservation System
- **Language:** Java
- **Framework:** Spring-boot

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A03 | Injection | High | src/main/java/com/hotel/reservation/controller/RoomController.java | CWE-89 |
| V2 | A05 | Security Misconfiguration | Medium | src/main/java/com/hotel/reservation/controller/AdminController.java | CWE-215 |
| V3 | A07 | Identification and Authentication Failures | Medium | src/main/java/com/hotel/reservation/config/SecurityConfig.java | CWE-384 |

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection

- **Severity:** High
- **Location:** `src/main/java/com/hotel/reservation/controller/RoomController.java`:20-29 (method: `searchRooms`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
JPQL query constructed using string concatenation with user-supplied parameters allows SQL/JPQL injection

### VULN-02: A05 — Security Misconfiguration

- **Severity:** Medium
- **Location:** `src/main/java/com/hotel/reservation/controller/AdminController.java`:14-25 (method: `getSystemInfo`)
- **CWE:** [CWE-215](https://cwe.mitre.org/data/definitions/215.html)

#### Description
Exposed admin debug endpoint without authentication leaks system variables and default admin credentials

### VULN-03: A07 — Identification and Authentication Failures

- **Severity:** Medium
- **Location:** `src/main/java/com/hotel/reservation/config/SecurityConfig.java`:31-35 (method: `filterChain`)
- **CWE:** [CWE-384](https://cwe.mitre.org/data/definitions/384.html)

#### Description
Session fixation protection is disabled via sessionFixation().none(), meaning session IDs are not rotated upon login


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Debug Info Leak → Session Fixation → Account Takeover

- **Combined Impact:** `account_takeover`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
Attacker targets the unauthenticated debug endpoint to discover default credentials and environment details, sets up session fixation targeting the admin session, and successfully takes over the admin account once the admin logs in.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Unauthenticated debug configuration endpoint exposes system info and credentials. | Medium | A05 | CWE-215 | src/main/java/com/hotel/reservation/controller/AdminController.java | `getSystemInfo` |
| 2 | Security config session management lacks session rotation, allowing session fixation. | Medium | A07 | CWE-384 | src/main/java/com/hotel/reservation/config/SecurityConfig.java | `filterChain` |

### CHAIN-02: Subtle Auth Session Pivot To Injection

- **Combined Impact:** `account_takeover`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy` `secondary_chain`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
Attacker combines a low-visibility entry point with stored or derived application state, then pivots to a higher-impact sink that is reachable only after following the cross-file flow.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Session fixation protection is disabled via sessionFixation().none(), meaning session IDs are not rotated upon login | Medium | A07 | CWE-384 | src/main/java/com/hotel/reservation/config/SecurityConfig.java | `filterChain` |
| 2 | Exposed admin debug endpoint without authentication leaks system variables and default admin credentials | Medium | A05 | CWE-215 | src/main/java/com/hotel/reservation/controller/AdminController.java | `getSystemInfo` |
| 3 | JPQL query constructed using string concatenation with user-supplied parameters allows SQL/JPQL injection | High | A03 | CWE-89 | src/main/java/com/hotel/reservation/controller/RoomController.java | `searchRooms` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/main/java/com/hotel/reservation/repository/ReservationRepository.java | JPA queries on Reservation are parameterised and safe from injection |
| src/main/java/com/hotel/reservation/controller/GuestController.java | getGuestDetails validates that GUEST users can only retrieve their own record |
