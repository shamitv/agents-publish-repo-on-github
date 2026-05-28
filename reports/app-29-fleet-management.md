# Security Report: app-29 — Vehicle Fleet Management

**Language:** Java (Spring-boot)
**Directory:** `apps/java/app-29-fleet-management`

---

## Application Information
- **App ID:** app-29
- **Name:** Vehicle Fleet Management
- **Language:** Java
- **Framework:** Spring-boot

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A03 | Injection | Medium | src/main/java/com/fleet/mgmt/service/DriverService.java | CWE-90 |
| V2 | A06 | Vulnerable and Outdated Components | Critical | pom.xml | CWE-502 |
| V3 | A10 | Server-Side Request Forgery | Medium | src/main/java/com/fleet/mgmt/controller/IntegrationController.java | CWE-918 |

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection

- **Severity:** Medium
- **Location:** `src/main/java/com/fleet/mgmt/service/DriverService.java`:19-25 (method: `lookupDriverByLicense`)
- **CWE:** [CWE-90](https://cwe.mitre.org/data/definitions/90.html)

#### Description
LDAP query constructed via string concatenation with user-provided parameters allows LDAP injection

### VULN-02: A06 — Vulnerable and Outdated Components

- **Severity:** Critical
- **Location:** `pom.xml`:33-46 (method: `dependencies`)
- **CWE:** [CWE-502](https://cwe.mitre.org/data/definitions/502.html)

#### Description
Log4j dependency is pinned to vulnerable version 2.14.1 (CVE-2021-44228) allowing remote code execution

### VULN-03: A10 — Server-Side Request Forgery

- **Severity:** Medium
- **Location:** `src/main/java/com/fleet/mgmt/controller/IntegrationController.java`:16-21 (method: `fetchExternalVehicleData`)
- **CWE:** [CWE-918](https://cwe.mitre.org/data/definitions/918.html)

#### Description
SSRF in external vehicle endpoint allows fetching arbitrary server-side resources without validation


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: Log4Shell → SSRF → Lateral Movement

- **Combined Impact:** `lateral_movement`
- **Difficulty:** Hard
- **Subtlety Tags:** `cross_file` `stateful_flow` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker has or can create a low privilege account
- attacker can combine request input with stored application state

#### Attack Narrative
Attacker triggers Log4Shell injection via search parameter which gets logged via Log4j 2.14.1, gains initial execution environment access, and exploits the unvalidated SSRF endpoint to query cloud metadata (169.254.169.254) and retrieve IAM credentials.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Application uses Log4j 2.14.1 and logs query inputs, making it vulnerable to JNDI injection. | Medium | A06 | CWE-502 | src/main/java/com/fleet/mgmt/controller/VehicleController.java | `searchVehicles` |
| 2 | Integration endpoint does not validate URLs before fetching them, permitting SSRF to internal/cloud metadata networks. | Medium | A10 | CWE-918 | src/main/java/com/fleet/mgmt/controller/IntegrationController.java | `fetchExternalVehicleData` |

### CHAIN-02: Subtle Ssrf Pivot To Injection

- **Combined Impact:** `lateral_movement`
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
| 1 | SSRF in external vehicle endpoint allows fetching arbitrary server-side resources without validation | Medium | A10 | CWE-918 | src/main/java/com/fleet/mgmt/controller/IntegrationController.java | `fetchExternalVehicleData` |
| 2 | Log4j dependency is pinned to vulnerable version 2.14.1 (CVE-2021-44228) allowing remote code execution | Critical | A06 | CWE-502 | pom.xml | `dependencies` |
| 3 | LDAP query constructed via string concatenation with user-provided parameters allows LDAP injection | Medium | A03 | CWE-90 | src/main/java/com/fleet/mgmt/service/DriverService.java | `lookupDriverByLicense` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/main/java/com/fleet/mgmt/controller/MaintenanceController.java | getRecords endpoint is secured with PreAuthorize ensuring only FLEET_MANAGER can access maintenance logs |
| src/main/java/com/fleet/mgmt/repository/VehicleRepository.java | All repository queries use parameterised Spring Data JPA methods which are safe from injection |
