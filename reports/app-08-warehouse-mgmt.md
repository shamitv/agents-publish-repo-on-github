# Security Report: app-08 — Warehouse Management System

**Language:** Java (Spring-boot)
**Directory:** `apps/java/app-08-warehouse-mgmt`

---

## Application Information
- **App ID:** app-08
- **Name:** Warehouse Management System
- **Language:** Java
- **Framework:** Spring-boot

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A05 | Security Misconfiguration | High | src/main/resources/application.properties | CWE-16 |
| V2 | A03 | Injection | High | src/main/java/com/warehouse/service/EmployeeLdapService.java | CWE-90 |
| V3 | A10 | Server-Side Request Forgery (SSRF) | Critical | src/main/java/com/warehouse/service/ShippingService.java | CWE-918 |

---

## Standalone Vulnerabilities

### VULN-01: A05 — Security Misconfiguration

- **Severity:** High
- **Location:** `src/main/resources/application.properties`:15-25 (method: `None`)
- **CWE:** [CWE-16](https://cwe.mitre.org/data/definitions/16.html)

#### Description
Spring Boot Actuator endpoints (env, heapdump, beans, mappings) exposed publicly without authentication via management.endpoints.web.exposure.include=*

### VULN-02: A03 — Injection

- **Severity:** High
- **Location:** `src/main/java/com/warehouse/service/EmployeeLdapService.java`:15-22 (method: `searchEmployees`)
- **CWE:** [CWE-90](https://cwe.mitre.org/data/definitions/90.html)

#### Description
LDAP filter constructed via string concatenation with user-supplied search term, enabling LDAP injection to enumerate all employees or extract hidden attributes

### VULN-03: A10 — Server-Side Request Forgery (SSRF)

- **Severity:** Critical
- **Location:** `src/main/java/com/warehouse/service/ShippingService.java`:12-35 (method: `generateLabel`)
- **CWE:** [CWE-918](https://cwe.mitre.org/data/definitions/918.html)

#### Description
Shipping label URL fetched server-side via HttpURLConnection with no scheme, host, or port validation — allows access to cloud metadata, internal services, and local files


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: LDAP Injection → Directory Structure Disclosure → Inventory Tampering

- **Combined Impact:** `data_modification`
- **Difficulty:** Medium
- **Subtlety Tags:** `cross_file` `direct_data_flow` `realistic_decoy`

#### Prerequisites
- attacker can reach the public request path
- attacker can control one request parameter or body field

#### Attack Narrative
Attacker injects a malformed LDAP filter that triggers an exception; the verbose error response reveals internal DN paths and account naming conventions. The attacker authenticates with a discovered worker account and calls the unprotected inventory adjustment endpoint to zero out stock counts.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | LDAP filter built by direct string concatenation of user input in searchEmployees(), enabling injection to enumerate arbitrary directory entries | Medium | A03 | CWE-90 | src/main/java/com/warehouse/service/EmployeeLdapService.java | `searchEmployees` |
| 2 | LDAP exceptions including internal DN paths are returned verbatim in the HTTP 500 error body, revealing directory structure to the attacker | Low | A05 | CWE-209 | src/main/java/com/warehouse/controller/EmployeeController.java | `search` |
| 3 | POST /api/inventory/{id}/adjust requires only authentication (no role check), allowing any worker account to modify stock quantities for any item | High | A01 | CWE-862 | src/main/java/com/warehouse/controller/InventoryController.java | `adjustQuantity` |

### CHAIN-02: Subtle Ssrf Pivot To Auth Session

- **Combined Impact:** `data_modification`
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
| 1 | Shipping label URL fetched server-side via HttpURLConnection with no scheme, host, or port validation — allows access to cloud metadata, internal services, and local files | Critical | A10 | CWE-918 | src/main/java/com/warehouse/service/ShippingService.java | `generateLabel` |
| 2 | LDAP filter constructed via string concatenation with user-supplied search term, enabling LDAP injection to enumerate all employees or extract hidden attributes | High | A03 | CWE-90 | src/main/java/com/warehouse/service/EmployeeLdapService.java | `searchEmployees` |
| 3 | Spring Boot Actuator endpoints (env, heapdump, beans, mappings) exposed publicly without authentication via management.endpoints.web.exposure.include=* | High | A05 | CWE-16 | src/main/resources/application.properties | `application` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/main/java/com/warehouse/repository/InventoryRepository.java | Spring Data JPA with parameterised @Query — NOT injectable |
| src/main/java/com/warehouse/config/SecurityConfig.java | BCryptPasswordEncoder — password hashing is SAFE |
| src/main/java/com/warehouse/controller/OrderController.java | @PreAuthorize on status change endpoints — access control is correct |
| src/main/java/com/warehouse/config/SecurityConfig.java | Session fixation protection set to migrateSession() — properly configured |
