# Security Report: app-50 — Energy Utility Billing

**Language:** Java (Spring-boot)
**Directory:** `apps/java/app-50-energy-billing`

---

## Application Information
- **App ID:** app-50
- **Name:** Energy Utility Billing
- **Language:** Java
- **Framework:** Spring-boot

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A01 | Broken Access Control | Medium | src/main/java/com/energy/billing/controller/BillingController.java | CWE-639 |
| V2 | A03 | Injection | High | src/main/java/com/energy/billing/controller/MeterController.java | CWE-89 |
| V3 | A05 | Security Misconfiguration | Medium | src/main/java/com/energy/billing/config/SecurityConfig.java | CWE-16 |
| V4 | A10 | Server-Side Request Forgery | Medium | src/main/java/com/energy/billing/controller/IntegrationController.java | CWE-918 |

---

## Standalone Vulnerabilities

### VULN-01: A01 — Broken Access Control

- **Severity:** Medium
- **Location:** `src/main/java/com/energy/billing/controller/BillingController.java`:21-27 (method: `getInvoice`)
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)

#### Description
IDOR on invoice retrieval allows customer accounts to read details of other customers' invoices without checks

### VULN-02: A03 — Injection

- **Severity:** High
- **Location:** `src/main/java/com/energy/billing/controller/MeterController.java`:20-33 (method: `searchReadings`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
Meter reading native query constructed by string concatenation with user parameters allows SQL injection

### VULN-03: A05 — Security Misconfiguration

- **Severity:** Medium
- **Location:** `src/main/java/com/energy/billing/config/SecurityConfig.java`:31-36 (method: `filterChain`)
- **CWE:** [CWE-16](https://cwe.mitre.org/data/definitions/16.html)

#### Description
H2 web console is enabled and permitted without authentication, offering direct database access

### VULN-04: A10 — Server-Side Request Forgery

- **Severity:** Medium
- **Location:** `src/main/java/com/energy/billing/controller/IntegrationController.java`:17-22 (method: `fetchSmartMeterData`)
- **CWE:** [CWE-918](https://cwe.mitre.org/data/definitions/918.html)

#### Description
Smart meter endpoint fetches user-supplied URLs without validation, enabling server-side request forgery


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: SSRF → H2 Console Access → Database Exfiltration

- **Combined Impact:** `db_exfiltration`
- **Difficulty:** Expert
- **Subtlety Tags:** `cross_file` `state_confusion` `parser_or_config_reasoning` `implicit_trust` `realistic_decoy`

#### Prerequisites
- attacker can influence a multi-step workflow
- attacker can observe or reuse application state across requests

#### Attack Narrative
Attacker triggers SSRF via the smart meter endpoint to target the unauthenticated H2 database console listening on localhost, bypassing network blocks to execute arbitrary SQL and dump all customer data.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | SSRF allows sending requests to internal endpoints. | Medium | A10 | CWE-918 | src/main/java/com/energy/billing/controller/IntegrationController.java | `fetchSmartMeterData` |
| 2 | H2 database console is enabled without security check. | Medium | A05 | CWE-16 | src/main/java/com/energy/billing/config/SecurityConfig.java | `filterChain` |

### CHAIN-02: Subtle Ssrf Pivot To Idor

- **Combined Impact:** `db_exfiltration`
- **Difficulty:** Expert
- **Subtlety Tags:** `cross_file` `state_confusion` `parser_or_config_reasoning` `implicit_trust` `realistic_decoy` `secondary_chain`

#### Prerequisites
- attacker can influence a multi-step workflow
- attacker can observe or reuse application state across requests

#### Attack Narrative
Attacker combines a low-visibility entry point with stored or derived application state, then pivots to a higher-impact sink that is reachable only after following the cross-file flow.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | Smart meter endpoint fetches user-supplied URLs without validation, enabling server-side request forgery | Medium | A10 | CWE-918 | src/main/java/com/energy/billing/controller/IntegrationController.java | `fetchSmartMeterData` |
| 2 | H2 web console is enabled and permitted without authentication, offering direct database access | Medium | A05 | CWE-16 | src/main/java/com/energy/billing/config/SecurityConfig.java | `filterChain` |
| 3 | Meter reading native query constructed by string concatenation with user parameters allows SQL injection | High | A03 | CWE-89 | src/main/java/com/energy/billing/controller/MeterController.java | `searchReadings` |
| 4 | IDOR on invoice retrieval allows customer accounts to read details of other customers' invoices without checks | Medium | A01 | CWE-639 | src/main/java/com/energy/billing/controller/BillingController.java | `getInvoice` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/main/java/com/energy/billing/controller/TariffController.java | getTariffs endpoint is secured with PreAuthorize restricting access to BILLING_ADMIN role only |
| src/main/java/com/energy/billing/controller/CustomerController.java | getCustomer validates that CUSTOMER role users can only retrieve their own details |
