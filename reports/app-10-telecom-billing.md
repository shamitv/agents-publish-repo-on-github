# Security Report: app-10 — Telecom Billing Platform

**Language:** Java (Spring-boot)
**Directory:** `apps/java/app-10-telecom-billing`

---

## Application Information
- **App ID:** app-10
- **Name:** Telecom Billing Platform
- **Language:** Java
- **Framework:** Spring-boot

## Vulnerability Summary

The following vulnerability list represents the ground truth security issues identified for this application:

| ID | OWASP | Category | Severity | Location | CWE |
|---|---|---|---|---|---|
| V1 | A03 | Injection | High | src/main/java/com/telecom/billing/controller/UsageController.java | CWE-89 |
| V2 | A04 | Insecure Design | Medium | src/main/java/com/telecom/billing/service/PaymentService.java | CWE-799 |
| V3 | A09 | Security Logging and Monitoring Failures | Low | src/main/java/com/telecom/billing/controller/AdminController.java | CWE-778 |

---

## Standalone Vulnerabilities

### VULN-01: A03 — Injection

- **Severity:** High
- **Location:** `src/main/java/com/telecom/billing/controller/UsageController.java`:20-31 (method: `getUsageByDateRange`)
- **CWE:** [CWE-89](https://cwe.mitre.org/data/definitions/89.html)

#### Description
Usage search SQL query constructed using string concatenation with user-supplied date values

### VULN-02: A04 — Insecure Design

- **Severity:** Medium
- **Location:** `src/main/java/com/telecom/billing/service/PaymentService.java`:21-36 (method: `processPayment`)
- **CWE:** [CWE-799](https://cwe.mitre.org/data/definitions/799.html)

#### Description
No rate limiting or idempotency check on the payment processing service

### VULN-03: A09 — Security Logging and Monitoring Failures

- **Severity:** Low
- **Location:** `src/main/java/com/telecom/billing/controller/AdminController.java`:21-32 (method: `adjustBalance`)
- **CWE:** [CWE-778](https://cwe.mitre.org/data/definitions/778.html)

#### Description
Admin balance adjustment endpoint lacks audit logging, allowing undetectable database modification


---

## Chained Attack Scenarios

Chained scenarios represent multiple code-level weaknesses that, when exploited in sequence, lead to high-impact outcomes.

### CHAIN-01: SQL Injection → Payment Fraud → No Audit Trail

- **Combined Impact:** `data_modification`
- **Difficulty:** Medium
- **Subtlety Tags:** `cross_file` `direct_data_flow` `realistic_decoy`

#### Prerequisites
- attacker can reach the public request path
- attacker can control one request parameter or body field

#### Attack Narrative
Attacker exploits SQL injection in usage search to leak invoice details, submits multiple forged or replayed payment confirmations via the non-idempotent payment endpoint, and utilizes unlogged admin balance adjustments to complete fraud.

#### Chain Components
| Step | Description | Severity | OWASP | CWE | Location | Method |
|---|---|---|---|---|---|---|
| 1 | SQL injection in usage lookup allows exfiltrating details of other customers' invoices. | Medium | A03 | CWE-89 | src/main/java/com/telecom/billing/controller/UsageController.java | `getUsageByDateRange` |
| 2 | Payment endpoint lacks concurrency / replay / rate-limiting controls, allowing payment fraud. | Medium | A04 | CWE-799 | src/main/java/com/telecom/billing/service/PaymentService.java | `processPayment` |
| 3 | Admin balance adjustments are not audit logged. | Low | A09 | CWE-778 | src/main/java/com/telecom/billing/controller/AdminController.java | `adjustBalance` |

### CHAIN-02: Subtle State Confusion Pivot To Injection

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
| 1 | Admin balance adjustment endpoint lacks audit logging, allowing undetectable database modification | Low | A09 | CWE-778 | src/main/java/com/telecom/billing/controller/AdminController.java | `adjustBalance` |
| 2 | No rate limiting or idempotency check on the payment processing service | Medium | A04 | CWE-799 | src/main/java/com/telecom/billing/service/PaymentService.java | `processPayment` |
| 3 | Usage search SQL query constructed using string concatenation with user-supplied date values | High | A03 | CWE-89 | src/main/java/com/telecom/billing/controller/UsageController.java | `getUsageByDateRange` |


---

## Decoys (False-Positive Candidates)

These code patterns mimic security weaknesses but are safe. They are included to measure static analyzer precision:

| Location | Description |
|---|---|
| src/main/java/com/telecom/billing/config/SecurityConfig.java | Strong hashing (BCrypt) used for customer passwords |
| src/main/java/com/telecom/billing/controller/CustomerController.java | getCustomer validates Principal name matches resource owner before returning profile details |
